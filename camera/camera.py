import gc
import time
import image
import sensor
import ml
import os

try:
    import network

    try:
        import usocket as socket
    except ImportError:
        import socket
except ImportError:
    network = None
    socket = None

try:
    import network

    try:
        import usocket as socket
    except ImportError:
        import socket
except ImportError:
    network = None
    socket = None


WIFI_SSID = "WIFI_SSID"  # mete aqui o nome da tua rede Wi-Fi
WIFI_PASSWORD = "WIFI_PASSWORD"  # mete aqui a password da tua rede Wi-Fi
HTTP_PORT = 8081
ENABLE_HTTP_DEBUG = True
DEBUG_ROW = 1
DEBUG_COL = 1


class DebugHttpServer:
    def __init__(self):
        self.server = None
        self.ip = None

        if not ENABLE_HTTP_DEBUG:
            print("HTTP debug desativado.")
            return

        if not WIFI_SSID or network is None or socket is None:
            print("HTTP debug desativado: configura WIFI_SSID/WIFI_PASSWORD.")
            return

        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            print("HTTP debug: a ligar ao Wi-Fi", WIFI_SSID)
            wlan.connect(WIFI_SSID, WIFI_PASSWORD)

            start = time.ticks_ms()
            while not wlan.isconnected():
                if time.ticks_diff(time.ticks_ms(), start) > 15000:
                    print("HTTP debug: timeout ao ligar ao Wi-Fi.")
                    return
                time.sleep_ms(250)

            self.ip = wlan.ifconfig()[0]
            print("HTTP debug ifconfig:", wlan.ifconfig())
            gc.collect()  # Limpar memória de sockets anteriores
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Tentar fazer bind com retries (caso o porto ainda esteja preso)
            for i in range(5):
                try:
                    self.server.bind(("0.0.0.0", HTTP_PORT))
                    break
                except OSError as e:
                    if i < 4:
                        print("Porto %d ocupado, a tentar novamente..." % HTTP_PORT)
                        time.sleep_ms(2000)
                    else:
                        raise e

            self.server.listen(5)
            self.server.setblocking(False)

            print("HTTP debug:", "http://%s:%d/" % (self.ip, HTTP_PORT))
        except Exception as e:
            print("HTTP debug desativado:", e)
            self.server = None

    def _send_all(self, client, data):
        while data:
            sent = client.send(data)
            data = data[sent:]

    def poll(self, scanner):
        if self.server is None:
            return

        for _ in range(5):
            try:
                client, _ = self.server.accept()
            except OSError:
                break

            try:
                client.settimeout(2)
                request = b""
                try:
                    request = client.recv(1024)
                except Exception:
                    pass

                if b"GET /debug_raw.bmp" in request:
                    self._send_file(client, "debug_raw.bmp", b"image/bmp")
                elif b"GET /debug_cell.bmp" in request:
                    self._send_file(client, "debug_cell.bmp", b"image/bmp")
                elif b"GET /" in request:
                    if b"?" in request:
                        try:
                            # Extrair parâmetros ?row=X&col=Y
                            path = request.decode().split(" ")[1]
                            query = path.split("?")[1]
                            for part in query.split("&"):
                                if part.startswith("row="):
                                    global DEBUG_ROW
                                    DEBUG_ROW = int(part.split("=")[1])
                                if part.startswith("col="):
                                    global DEBUG_COL
                                    DEBUG_COL = int(part.split("=")[1])
                        except:
                            pass

                    body = self._build_page(scanner).encode()
                    header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html; charset=utf-8\r\n"
                        "Content-Length: %d\r\n"
                        "Cache-Control: no-store\r\n"
                        "Connection: close\r\n\r\n" % len(body)
                    )
                    self._send_all(client, header.encode())
                    self._send_all(client, body)
            except Exception as e:
                print("HTTP debug erro:", e)
            finally:
                client.close()

    def _build_page(self, scanner):
        prediction = scanner.last_debug_prediction or "n/a"
        scores = scanner.last_debug_scores or []

        grid_html = '<div class="grid">'
        for r in range(3):
            for c in range(3):
                active = "active" if (r == DEBUG_ROW and c == DEBUG_COL) else ""
                grid_html += '<a href="/?row=%d&col=%d" class="%s">%d,%d</a>' % (
                    r,
                    c,
                    active,
                    r,
                    c,
                )
        grid_html += "</div>"

        return """<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="2">
<style>
body { font-family: sans-serif; background: #111; color: #eee; margin: 24px; }
.grid { display: grid; grid-template-columns: repeat(3, 50px); gap: 8px; margin-bottom: 20px; }
.grid a { display: block; background: #333; color: #fff; text-align: center; line-height: 40px; text-decoration: none; border: 1px solid #555; border-radius: 4px; }
.grid a.active { background: #070; border-color: #0f0; font-weight: bold; }
pre { background: #222; padding: 10px; color: #ccc; border-radius: 4px; }
img { border: 1px solid #444; margin-bottom: 10px; image-rendering: pixelated; }
</style>
</head>
<body>
<h3>Debug Célula (%d, %d)</h3>
%s
<p>Raw (80x80):</p>
<img src="/debug_raw.bmp?t=%s" width="240" height="240">
<p>Input IA (28x28):</p>
<img src="/debug_cell.bmp?t=%s" width="240" height="240">
<pre>Pred: %s
Scores [X, E, O]: %s</pre>
</body>
</html>""" % (
            DEBUG_ROW,
            DEBUG_COL,
            grid_html,
            time.ticks_ms(),
            time.ticks_ms(),
            prediction,
            scores,
        )

    def _send_file(self, client, path, content_type):
        try:
            size = os.stat(path)[6]
            f = open(path, "rb")
            if isinstance(content_type, bytes):
                content_type = content_type.decode()
            header = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: %s\r\n"
                "Content-Length: %d\r\n"
                "Cache-Control: no-store\r\n"
                "Connection: close\r\n\r\n" % (content_type, size)
            )
            self._send_all(client, header.encode())
            while True:
                data = f.read(1024)
                if not data:
                    break
                self._send_all(client, data)
            f.close()
        except Exception:
            try:
                self._send_all(
                    client, b"HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
                )
            except:
                pass


def trimmed_mean(data, proportion_to_cut=0.1):
    # Ordenar os dados
    sorted_data = sorted(data)

    # Calcular quantos elementos remover
    n = len(sorted_data)
    k = int(n * proportion_to_cut)

    # Fatiar a lista (remover os extremos)
    if k > 0:
        trimmed = sorted_data[k:-k]
    else:
        trimmed = sorted_data

    return sum(trimmed) / len(trimmed)


class BoardBlobDetector:
    def __init__(self):
        sensor.reset()
        sensor.set_pixformat(sensor.GRAYSCALE)
        sensor.set_framesize(sensor.B128X128)
        sensor.set_auto_exposure(True)

        self.clock = time.clock()
        self.save_debug_cells = False
        self.saved_debug_cells = False
        self.last_debug_row = None
        self.last_debug_col = None
        self.last_debug_prediction = None
        self.last_debug_scores = None

        self.threshold = (80, 255)

        gc.collect()

        try:
            self.model = ml.Model(
                "model.tflite",
                load_to_fb=True,
                always_console_output=False,
            )

        except Exception as e:

            print("Error2:", e)
            exit(1)

        gc.collect()

    def preprocess_cell(self, cell_img, row=None, col=None):
        w = cell_img.width()
        h = cell_img.height()

        margin = 4
        cropped = cell_img.copy(
            roi=(margin, margin, w - (2 * margin), h - (2 * margin))
        )

        # 1. Guarda o original (raw)

        # 2. Otimização: Abertura morfológica para limpar ruído (blobs pequenos)
        # O erode seguido de dilate elimina pontos isolados (ruído)
        # Kernel 3x3: um filtro passa-baixo simples (suavização) 
        # que ajuda a eliminar ruído "sal e pimenta"
        cropped.morph(1, [0, 0, 0,
                        0, 1, 0,
                        0, 0, 0])
        raw_debug = cropped.copy()

        # 3. Calcular média para thresholding dinâmico
        stats = cropped.get_statistics()
        mean_val = stats.mean()

        # 4. Binarização focada no que é mais claro que a média
        # Usamos 'zero=True' para garantir fundo preto puro
        cropped.binary([(0,int(mean_val*0.8))])

        # 5. Esvaziamento de blobs pequenos (Noise removal final)
        # removemos ilhas de pixeis com menos de 20 unidades de área
        cropped.median(1)
        cropped.dilate(1)

        # 6. Redimensionamento
        resized = image.Image(28, 28, sensor.GRAYSCALE)
        resized.draw_image(
            cropped, 0, 0, x_scale=28 / cropped.width(), y_scale=28 / cropped.height()
        )

        # Se for o target de debug, salva
        if row == DEBUG_ROW and col == DEBUG_COL:
            raw_debug.save("debug_raw.bmp")
            cropped.save("debug_cell.bmp")

        arr = resized.to_ndarray("f").reshape((1, 1, 28, 28)) / 255.0

        # print("image:", arr[0][0])
        pred = self.model.predict([arr])
        out = pred[0][0]

        class_names = ["cross", "empty", "round"]
        best_idx = 0
        best_val = out[0]

        for i in range(1, len(out)):
            if out[i] > best_val:
                best_val = out[i]
                best_idx = i

        if row == DEBUG_ROW and col == DEBUG_COL:
            self.last_debug_row = row
            self.last_debug_col = col
            self.last_debug_prediction = class_names[best_idx]
            self.last_debug_scores = [out[0], out[1], out[2]]

        return class_names[best_idx], out

    def extract_grid(self, board_img):

        w_board = board_img.width()
        h_board = board_img.height()

        cell_w = w_board // 3
        cell_h = h_board // 3

        predictions = []

        for row in range(3):
            for col in range(3):

                cx = col * cell_w
                cy = row * cell_h

                cell = board_img.copy(roi=(cx, cy, cell_w, cell_h))

                out, scores = self.preprocess_cell(cell, row, col)

                predictions.append(out)
                print("cell", row, col, "scores:", scores)

                del cell

            gc.collect()

        self.saved_debug_cells = True

        return predictions

    def scan(self):
        self.clock.tick()

        img = sensor.snapshot()
        img.gaussian(1)

        w = img.width()
        h = img.height()

        cell_w = w // 3
        cell_h = h // 3

        for row in range(3):
            for col in range(3):
                cx = col * cell_w
                cy = row * cell_h

                # desenhar cada célula no frame original
                img.draw_rectangle((cx, cy, cell_w, cell_h), color=200, thickness=1)

        # agora inferência separada na imagem toda
        results = self.extract_grid(img)

        fps = self.clock.fps()

        return results, fps


scanner = BoardBlobDetector()
http_server = DebugHttpServer()

while True:
    # Verificar se a ligação ainda está ativa
    wlan = network.WLAN(network.STA_IF) if network else None
    if wlan and not wlan.isconnected():
        print("Wi-Fi perdido! A religar...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    try:
        http_server.poll(scanner)
        results, fps = scanner.scan()
        http_server.poll(scanner)
        print("FPS:", fps, "Predictions:", results)
    except Exception as e:
        print("Erro1:", e)
        gc.collect()
        raise e

    time.sleep_ms(100)
e.sleep_ms(100)
