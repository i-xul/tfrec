
#!/usr/bin/env python3
"""HTTP API for the latest TFA COSY BARO measurement."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "cosy_baro_latest.json"

HOST = "0.0.0.0"
PORT = 8765


class CosyBaroHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/api/cosy-baro":
            self.send_error(404, "Not found")
            return

        try:
            measurement = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self.send_error(503, "No measurement available")
            return
        except (OSError, json.JSONDecodeError):
            self.send_error(500, "Unable to read measurement")
            return

        response = json.dumps(measurement).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response)


def main():
    server = ThreadingHTTPServer((HOST, PORT), CosyBaroHandler)
    print(f"COSY BARO HTTP API listening on port {PORT}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nHTTP server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
