import gc
import time
import image
import sensor
import bluetooth
import struct
import os
import pyb

# --- LEDs ---
led_red = pyb.LED(1)
led_green = pyb.LED(2)
led_blue = pyb.LED(3)

def leds_off():
    led_red.off()
    led_green.off()
    led_blue.off()

leds_off()

# --- Configurações ---
USE_ML_MODEL = True
ENABLE_HTTP_DEBUG = False  # Alterar para False para desativar o servidor web

WIFI_SSID = "NOS-4406"
WIFI_PASSWORD = "USV3WALC"
HTTP_PORT = 8081

DEBUG_ROW = 1
DEBUG_COL = 1

if USE_ML_MODEL:
    import ml
else:
    ml = None

# --- Imports para Servidor Web ---
network = None
socket = None
if ENABLE_HTTP_DEBUG:
    try:
        import network
        try:
            import usocket as socket
        except ImportError:
            import socket
    except ImportError:
        pass

# --- BLE Peripheral Implementation ---
_ADV_TYPE_FLAGS = 0x01
_ADV_TYPE_NAME = 0x09
_ADV_TYPE_UUID128_COMPLETE = 0x07

class BLEPeripheral:
    def __init__(self, ble, name="Nicla"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        service_uuid = bluetooth.UUID("3f0d0993-67eb-4f86-a858-10f9d6c16f88")
        tx_uuid = bluetooth.UUID("dafa5642-b1ca-4eed-93ec-fc161d95107a")
        rx_uuid = bluetooth.UUID("6dafa070-2ae1-4185-9ff2-73a5da2471c2")
        self._tx_char = (tx_uuid, bluetooth.FLAG_NOTIFY | bluetooth.FLAG_READ,)
        self._rx_char = (rx_uuid, bluetooth.FLAG_WRITE,)
        self._service = (service_uuid, (self._tx_char, self._rx_char),)
        ((self._tx_handle, self._rx_handle),) = self._ble.gatts_register_services((self._service,))
        self._conn_handle = None
        self._payload = self._advertise_payload(name=name, services=[service_uuid])
        self._advertise()
        self._last_rx_data = None

    def _irq(self, event, data):
        if event == 1: self._conn_handle, _, _ = data
        elif event == 2:
            self._conn_handle = None
            self._advertise()
        elif event == 3:
            conn_handle, value_handle = data
            if conn_handle == self._conn_handle and value_handle == self._rx_handle:
                self._last_rx_data = self._ble.gatts_read(self._rx_handle)

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def _advertise_payload(self, name=None, services=None):
        payload = bytearray()
        def add(type, value):
            nonlocal payload
            payload += struct.pack("BB", len(value) + 1, type) + value
        add(_ADV_TYPE_FLAGS, struct.pack("B", 0x06))
        if name: add(_ADV_TYPE_NAME, name.encode())
        if services:
            for s in services: add(_ADV_TYPE_UUID128_COMPLETE, bytes(s))
        return payload

    def send(self, value):
        if self._conn_handle is not None:
            data = struct.pack("<H", int(value))
            self._ble.gatts_notify(self._conn_handle, self._tx_handle, data)

    def is_connected(self):
        return self._conn_handle is not None

    def read(self):
        data = self._last_rx_data
        self._last_rx_data = None
        if data:
            try:
                return struct.unpack("<H", data)[0]
            except:
                return None
        return None

# --- HTTP Server Implementation ---
class DebugHttpServer:
    def __init__(self):
        self.server = None
        self.ip = None
        if not ENABLE_HTTP_DEBUG or network is None: return

        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            start = time.ticks_ms()
            while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start) < 10000:
                time.sleep_ms(500)

            if wlan.isconnected():
                self.ip = wlan.ifconfig()[0]
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                self.actual_port = 8080
                bound = False
                while self.actual_port <= 8090:
                    try:
                        self.server.bind(("0.0.0.0", self.actual_port))
                        bound = True
                        break
                    except OSError:
                        self.actual_port += 1

                if bound:
                    self.server.listen(1)
                    self.server.setblocking(False)
                    print("HTTP Server: http://%s:%d/" % (self.ip, self.actual_port))
                else:
                    self.server.close()
                    self.server = None
        except Exception as e:
            print("HTTP Server Erro:", e)

    def poll(self, scanner):
        if self.server is None: return
        try:
            client, _ = self.server.accept()
        except OSError:
            return

        try:
            client.settimeout(2)
            request = client.recv(1024)
            if b"GET /debug_raw.bmp" in request:
                self._send_file(client, "debug_raw.bmp", "image/bmp")
            elif b"GET /debug_cell.bmp" in request:
                self._send_file(client, "debug_cell.bmp", "image/bmp")
            elif b"GET /" in request:
                if b"?" in request:
                    try:
                        path = request.decode().split(" ")[1]
                        query = path.split("?")[1]
                        for part in query.split("&"):
                            if part.startswith("row="):
                                global DEBUG_ROW
                                DEBUG_ROW = int(part.split("=")[1])
                            if part.startswith("col="):
                                global DEBUG_COL
                                DEBUG_COL = int(part.split("=")[1])
                    except: pass
                body = self._build_page(scanner).encode()
                header = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % len(body)
                client.sendall(header.encode())
                client.sendall(body)
        except Exception as e:
            print("HTTP poll erro:", e)
        finally:
            client.close()

    def _build_page(self, scanner):
        return """<html><head><meta http-equiv="refresh" content="2"></head>
        <body style="background:#111; color:#eee; font-family:sans-serif;">
        <h3>Debug Nicla (%d,%d)</h3>
        <img src="/debug_raw.bmp?t=%d" width="200"><br>
        <img src="/debug_cell.bmp?t=%d" width="200">
        <p>Previsão: %s</p>
        <div style="display:grid; grid-template-columns:repeat(3,40px); gap:5px;">
        %s</div></body></html>""" % (DEBUG_ROW, DEBUG_COL, time.ticks_ms(), time.ticks_ms(),
        getattr(scanner, 'last_pred', 'n/a'),
        "".join(['<a href="/?row=%d&col=%d" style="background:#333; color:#fff; text-align:center;">%d,%d</a>'%(r,c,r,c) for r in range(3) for c in range(3)]))

    def _send_file(self, client, path, content_type):
        try:
            size = os.stat(path)[6]
            header = "HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % (content_type, size)
            client.sendall(header.encode())
            with open(path, "rb") as f:
                while True:
                    data = f.read(512)
                    if not data: break
                    client.sendall(data)
        except: pass

# --- Detector: Baseado em Blobs / IA ---
class BoardBlobDetector:
    def __init__(self):
        self.clock = time.clock()
        self.last_pred = "n/a"
        gc.collect()
        self.model = None
        if USE_ML_MODEL:
            try: self.model = ml.Model("model.tflite", always_console_output=False)
            except: pass
        sensor.reset()
        sensor.set_pixformat(sensor.GRAYSCALE)
        sensor.set_framesize(sensor.B160X160)
        sensor.set_auto_exposure(True)

    def preprocess_cell(self, cell_img, row=None, col=None):
        w, h = cell_img.width(), cell_img.height()
        margin = 6
        cropped = cell_img.copy(roi=(margin, margin, w - (2 * margin), h - (2 * margin)))
        cropped.gaussian(1)

        if ENABLE_HTTP_DEBUG and row == DEBUG_ROW and col == DEBUG_COL:
            try: cropped.save("debug_raw.bmp")
            except: pass

        stats = cropped.get_statistics()
        if stats.stdev() < 8:
            if ENABLE_HTTP_DEBUG and row == DEBUG_ROW and col == DEBUG_COL:
                self.last_pred = "empty"
                try: cropped.clear().save("debug_cell.bmp")
                except: pass
            return "empty"

        # Adaptive Threshold (Fundo Local - Original)
        bg = cropped.copy()
        bg.mean(3) # Janela de 7x7 para uma melhor estimativa do papel
        bg.sub(cropped)

        # Baixamos o limiar para 15 para traços mais definidos
        bg.binary([(15, 255)])

        # Dilação suave (1) para não engrossar demasiado
        bg.dilate(1)
        bg.median(1)

        if ENABLE_HTTP_DEBUG and row == DEBUG_ROW and col == DEBUG_COL:
            try: bg.save("debug_cell.bmp")
            except: pass

        # Aumentamos o stride para 4 para unir fragmentos mesmo com traços finos
        blobs = bg.find_blobs([(200, 255)], pixels_threshold=15, area_threshold=15, merge=True, x_stride=4, y_stride=4)
        if not blobs:
            if row == DEBUG_ROW and col == DEBUG_COL: self.last_pred = "empty"
            return "empty"

        x0, y0, x1, y1 = bg.width(), bg.height(), 0, 0
        for blob in blobs:
            bx, by, bw, bh = blob.rect()
            x0, y0 = min(x0, bx), min(y0, by)
            x1, y1 = max(x1, bx + bw), max(y1, by + bh)

        pad = 2
        x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
        x1, y1 = min(bg.width(), x1 + pad), min(bg.height(), y1 + pad)
        # Recortamos o símbolo da imagem binária para enviar ao classificador
        cropped = bg.copy(roi=(x0, y0, x1 - x0, y1 - y0))

        resized = image.Image(28, 28, sensor.GRAYSCALE)
        resized.clear()
        scale = min(24 / cropped.width(), 24 / cropped.height())
        resized.draw_image(cropped, (28 - int(cropped.width()*scale)) // 2, (28 - int(cropped.height()*scale)) // 2, x_scale=scale, y_scale=scale)

        if self.model is None:
            pred = self.classify_cell_by_image(resized)
        else:
            arr = resized.to_ndarray("f").reshape((1, 1, 28, 28)) / 255.0
            out = self.model.predict([arr])[0][0]
            best = 0
            for i in range(1, 3):
                if out[i] > out[best]: best = i
            pred = ["cross", "empty", "round"][best]

        if row == DEBUG_ROW and col == DEBUG_COL: self.last_pred = pred
        return pred

    def classify_cell_by_image(self, img):
        ink = img.get_statistics().mean() / 255.0
        center_ink = img.get_statistics(roi=(8, 8, 12, 12)).mean() / 255.0
        if ink < 0.04: return "empty"
        if center_ink < 0.18: return "round"
        return "cross"

    def scan(self):
        img = sensor.snapshot()
        w, h = img.width(), img.height()
        cell_w, cell_h = w // 3, h // 3
        for i in range(1, 3):
            img.draw_line((i * cell_w, 0, i * cell_w, h), color=150)
            img.draw_line((0, i * cell_h, w, i * cell_h), color=150)

        predictions = []
        for row in range(3):
            for col in range(3):
                cell = img.copy(roi=(col * cell_w, row * cell_h, cell_w, cell_h))
                predictions.append(self.preprocess_cell(cell, row, col))
                del cell
            gc.collect()
        return predictions

def board_to_int(results):
    # Mapeamento para o Robot: 1=Humano (Round), 2=Robô (Cross)
    mapping = {"empty": 0, "round": 1, "cross": 2}
    val = 0
    for i, res in enumerate(results):
        val += mapping.get(res, 0) * (3**i)
    return val

def count_differences(b1, b2):
    return sum(1 for i in range(9) if b1[i] != b2[i])

# --- Inicialização ---
scanner = BoardBlobDetector()

ble = BLEPeripheral(bluetooth.BLE())
http_server = DebugHttpServer()

current_state = 0 # 0=WAIT_PLAYER, 1=WAIT_ROBOT
last_committed_board = ["empty"] * 9
stable_board = ["empty"] * 9
stable_counter = 0
robot_signalled = False

print("Iniciado. Aguardando conexão BLE...")

while True:
    try:
        if ENABLE_HTTP_DEBUG: http_server.poll(scanner)

        results = scanner.scan()

        if not ble.is_connected():
            stable_counter = 0
            time.sleep_ms(50)
            continue

        print(results)
        if results == stable_board: stable_counter += 1
        else:
            stable_board = list(results)
            stable_counter = 0

        if stable_counter >= 20:
            # Diferença em relação ao último tabuleiro OFICIAL
            diffs = count_differences(results, last_committed_board)

            if current_state == 0 and diffs == 1 and ble.is_connected():
                print("Jogada Player detetada:", results)
                ble.send(board_to_int(results))
                last_committed_board = list(results)
                current_state = 1
                robot_signalled = False

            elif current_state == 1:
                ble_cmd = ble.read()
                if ble_cmd == 11:
                    robot_signalled = True
                    print("Robot sinalizou WAIT.")
                elif ble_cmd == 21:
                    print("GAME OVER: ROBOT VENCEU!")
                    scanner.last_pred = "ROBOT VENCEU!"
                    leds_off()
                    led_blue.on() # Azul para o Robô
                    current_state = 2 # Estado de fim de jogo
                elif ble_cmd == 22:
                    print("GAME OVER: TU VENCESTE!")
                    scanner.last_pred = "TU VENCESTE!"
                    leds_off()
                    led_green.on() # Verde para o Humano
                    current_state = 2
                elif ble_cmd == 23:
                    print("GAME OVER: EMPATE!")
                    scanner.last_pred = "EMPATE!"
                    leds_off()
                    led_red.on() # Vermelho para Empate
                    current_state = 2

            elif current_state == 2:
                # Se o jogo acabou, verificamos se o tabuleiro foi limpo para reiniciar
                if all(res == "empty" for res in results):
                    print("Tabuleiro limpo. Reiniciando...")
                    leds_off()
                    last_committed_board = ["empty"] * 9
                    stable_board = ["empty"] * 9
                    current_state = 0
                    robot_signalled = False

                # Após o sinal do robot, esperamos que o tabuleiro mude (mais 1 peça)
                if robot_signalled and diffs == 1:
                    print("Robot move detetada:", results)
                    last_committed_board = list(results)
                    current_state = 0
                    print("--- Tua vez! ---")

        gc.collect()
    except Exception as e:
        print("Erro:", e)
        time.sleep_ms(1000)
