import json
import sys
import os
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api._scanner import get_scan_results

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        def get(key, default=None):
            return params.get(key, [default])[0]

        def get_bool(key):
            return get(key, "false").lower() in ("true", "1", "yes")

        scan_type = get("type", "")
        target = get("target", "")

        if not target:
            return self._json({"error": "Missing required parameter: target"}, 400)
        if scan_type not in ("username", "email"):
            return self._json({"error": "Parameter 'type' must be 'username' or 'email'"}, 400)

        try:
            results = get_scan_results(
                target=target,
                is_email=(scan_type == "email"),
                category=get("category"),
                module=get("module"),
                only_found=get_bool("only_found"),
                no_nsfw=get_bool("no_nsfw"),
                hudson=get_bool("hudson"),          # ← New
            )
            self._json({
                "target": target,
                "type": scan_type,
                "count": len(results),
                "results": results,
            })
        except ValueError as e:
            self._json({"error": str(e)}, 400)
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
