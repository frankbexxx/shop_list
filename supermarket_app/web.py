import json
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs

from .config import STATIC_DIR


class HTTPError(Exception):
    def __init__(self, status: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def json_response(start_response, payload, status: str = "200 OK"):
    body = json.dumps(payload).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def file_response(start_response, file_path: Path):
    content = file_path.read_bytes()
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    start_response("200 OK", [("Content-Type", content_type), ("Content-Length", str(len(content)))])
    return [content]


def parse_json_body(environ) -> dict:
    length = int(environ.get("CONTENT_LENGTH") or 0)
    if length == 0:
        return {}
    raw = environ["wsgi.input"].read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def parse_path_params(path: str) -> list[str]:
    return [segment for segment in path.strip("/").split("/") if segment]


def get_query(environ) -> dict[str, list[str]]:
    return parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)


def serve_static(path: str, start_response):
    file_path = STATIC_DIR / path.removeprefix("/static/")
    if not file_path.exists() or not file_path.is_file():
        raise HTTPError("404 Not Found", "Static file not found")
    return file_response(start_response, file_path)
