import json
import sys
import os
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api._scanner import get_modules


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        def get(key, default=None):
            return params.get(key, [default])[0]

        def get_bool(key):
            return get(key, "false").lower() in ("true", "1", "yes")

        scan_type = get("type", "")

        if scan_type not in ("username", "email"):
            return self._json({"error": "Parameter 'type' must be 'username' or 'email'"}, 400)

        try:
            data = get_modules(is_email=(scan_type == "email"), no_nsfw=get_bool("no_nsfw"))
            total = sum(len(v) for v in data.values())
            self._json({
                "type": scan_type,
                "total_modules": total,
                "categories": data,
            })
        except Exception as e:
            self._json({"error": f"Internal error: {str(e)}"}, 500)

    def _json(self, data, status=200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass
