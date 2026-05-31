import serial
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

SERIAL_PORT = '/dev/ttyACM'
BAUD_RATE = 115200

for i in range(9):
    try:
        ser = serial.Serial(f"{SERIAL_PORT}{i}", BAUD_RATE, timeout=0.1)
        time.sleep(2)
        print(f"Conectado a {SERIAL_PORT}{i}")
        break
    except Exception as e:
        print(f"Erro Serial: {e}")
        ser = None

def read_from_arduino():
    while ser and ser.is_open:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line: print(f"ARDUINO: {line}")
        except: break

if ser: threading.Thread(target=read_from_arduino, daemon=True).start()

class ControlHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Robot Control Center</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: sans-serif; text-align: center; padding: 20px; background: #f4f4f9; color: #333; }
                    .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin: 20px auto; max-width: 600px; }
                    .slider-container { margin: 20px 0; }
                    input[type=range] { width: 100%; height: 30px; }
                    .val { font-size: 1.4em; color: #4CAF50; font-weight: bold; }
                    
                    /* Grelha para as posições espaciais */
                    .pos-grid { 
                        display: grid; 
                        grid-template-columns: 1fr 1fr 1fr; 
                        gap: 10px; 
                        margin-top: 15px; 
                    }
                    
                    /* Grelha para bases e comandos gerais */
                    .base-grid { 
                        display: grid; 
                        grid-template-columns: 1fr 1fr; 
                        gap: 10px; 
                        margin-top: 15px; 
                    }

                    button { padding: 15px; font-size: 0.9em; border: none; border-radius: 8px; background: #2196F3; color: white; cursor: pointer; transition: 0.2s; font-weight: bold; }
                    button:hover { background: #1976D2; transform: translateY(-2px); }
                    
                    button.top { background: #4CAF50; }
                    button.center { background: #FF9800; }
                    button.bottom { background: #E91E63; }
                    button.base { background: #607D8B; }
                    
                    h2 { border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 0; }
                    .section-label { font-size: 0.8em; color: #888; text-transform: uppercase; margin-top: 15px; display: block; }
                </style>
            </head>
            <body>
                <h1>Robot Control Center</h1>
                
                <div class="card">
                    <h2>Sequences Grid</h2>
                    
                    <span class="section-label">Top Positions</span>
                    <div class="pos-grid">
                        <button class="top" onclick="play(8)">TL</button>
                        <button class="top" onclick="play(6)">TC</button>
                        <button class="top" onclick="play(7)">TR</button>
                    </div>

                    <span class="section-label">Center Positions</span>
                    <div class="pos-grid">
                        <button class="center" onclick="play(5)">CL</button>
                        <button class="center" onclick="play(3)">CC</button>
                        <button class="center" onclick="play(4)">CR</button>
                    </div>

                    <span class="section-label">Bottom Positions</span>
                    <div class="pos-grid">
                        <button class="bottom" onclick="play(2)">BL</button>
                        <button class="bottom" onclick="play(0)">BC</button>
                        <button class="bottom" onclick="play(1)">BR</button>
                    </div>

                    <span class="section-label">Home / Calibration</span>
                    <div class="base-grid">
                        <button class="base" onclick="play(9)">BASE 1</button>
                        <button class="base" onclick="play(10)">BASE 2</button>
                        <button class="base" style="background:#9C27B0;" onclick="sendWait()">WAIT</button>
                    </div>
                </div>

                <div class="card">
                    <h2>Manual Motor Control</h2>
                    <div class="slider-container">
                        <label>Motor 1 (Slow): <span id="vm1" class="val">90</span>°</label>
                        <input type="range" min="0" max="180" step="1" value="90" id="sm1" oninput="updateAngles()">
                    </div>
                    <div class="slider-container">
                        <label>Motor 2: <span id="vm2" class="val">90</span>°</label>
                        <input type="range" min="0" max="180" step="1" value="90" id="sm2" oninput="updateAngles()">
                    </div>
                    <div class="slider-container">
                        <label>Motor 3: <span id="vm3" class="val">90</span>°</label>
                        <input type="range" min="0" max="180" step="1" value="90" id="sm3" oninput="updateAngles()">
                    </div>
                </div>

                <script>
                    let lastSend = 0;
                    function updateAngles() {
                        let m1 = document.getElementById('sm1').value;
                        let m2 = document.getElementById('sm2').value;
                        let m3 = document.getElementById('sm3').value;
                        document.getElementById('vm1').innerText = m1;
                        document.getElementById('vm2').innerText = m2;
                        document.getElementById('vm3').innerText = m3;
                        send(`/moveAngles?m1=${m1}&m2=${m2}&m3=${m3}`);
                    }
                    function play(id) {
                        console.log("Playing sequence ID:", id);
                        fetch(`/play?id=${id}`);
                    }
                    function sendWait() {
                        console.log("Sending WAIT command");
                        fetch(`/wait`);
                    }
                    function send(url) {
                        let now = Date.now();
                        if (now - lastSend > 50) {
                            fetch(url);
                            lastSend = now;
                        }
                    }
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/play'):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            idx = params.get('id', ['0'])[0]
            if ser: 
                ser.write(f"S:{idx}\n".encode())
                print(f"Enviado para Arduino: S:{idx}")
            self.send_response(200); self.end_headers()

        elif self.path.startswith('/wait'):
            if ser:
                ser.write(b"W:\n")
                print("Enviado para Arduino: W:")
            self.send_response(200); self.end_headers()

        elif self.path.startswith('/moveAngles'):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            m1 = params.get('m1', ['90'])[0]
            m2 = params.get('m2', ['90'])[0]
            m3 = params.get('m3', ['90'])[0]
            if ser: ser.write(f"M:{m1},{m2},{m3}\n".encode())
            self.send_response(200); self.end_headers()

def run_server():
    HTTPServer(('0.0.0.0', 8080), ControlHandler).serve_forever()

if __name__ == '__main__':
    print("Dashboard Ativo em http://localhost:8080")
    run_server()
