#!/usr/bin/env python3
import http.server
import http.client
from socket import SocketIO
import protocol
from mods import join_any_game, rickroll, count

HOST, PORT = "0.0.0.0", 80
MODS = [join_any_game]

REAL_IP = "96.127.165.218"  # nslookup api.playerio.com 8.8.8.8


class Proxy(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"GET request received for {self.path} to {self.headers['Host']}:")

        conn = http.client.HTTPConnection(REAL_IP)
        conn.request("GET", self.path, headers=self.headers)
        resp = conn.getresponse()
        body = resp.read()

        print(f"Response received for GET {self.path}:")
        self.send_response(resp.status)
        for header, value in resp.getheaders():
            if header.lower() == "content-length":
                self.send_header(header, len(body))
            else:
                self.send_header(header, value)
        self.end_headers()
        self.wfile.write(body)

    def get_real_response(self, body):
        conn = http.client.HTTPConnection(REAL_IP)
        conn.request("POST", self.path, body=body, headers=self.headers)
        resp = conn.getresponse()
        body = resp.read()
        return resp, body

    def empty_response(self):
        self.send_response(200)
        self.send_header("Content-Length", 0)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        print(f"POST request received for {self.path} to {self.headers['Host']}:")

        resp, body = self.get_real_response(body)
        print(f"Response received for POST {self.path}:")

        if self.path == "/api/30" and b"Game" in body:  # = Fetch games
            games = protocol.decode_all(body)  # Decode to object

            for mod in MODS:  # Apply mods
                games = mod.mod(games)

            body = protocol.encode_all(games)  # Encode back to bytes
        elif self.path == "/api/50":  # = Error
            print(body)
            self.empty_response()  # Don't send to server
            return

        self.send_response(resp.status)
        for header, value in resp.getheaders():
            if header.lower() == "content-length":
                self.send_header(header, len(body))
            else:
                self.send_header(header, value)
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    print(f"Starting proxy server on {HOST}:{PORT}")
    http.server.HTTPServer((HOST, PORT), Proxy).serve_forever()
