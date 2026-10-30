# HTTP library

`http_lib.fr` is a small HTTP/1.1 server/client library implemented in Fr. It
uses only sockets and string/list operations, so the same source runs on the
Python VM, the C VM, and the native backend.

## Run

```sh
# Python VM
python3 src/cli.py examples/http/server_demo.fr -py
python3 src/cli.py examples/http/client_demo.fr -py

# C VM
python3 src/cli.py compile examples/http/server_demo.fr -o /tmp/server.bc
python3 src/cli.py /tmp/server.bc -c

# Native
python3 src/cli.py native /tmp/server.bc -o /tmp/server
/tmp/server
```

The demo server listens on `127.0.0.1:18081`, handles one request, and exits.
`GET /hello` returns the user agent, `POST /echo` returns the request body, and
everything else returns 404.

## API

- `http_parse_request(raw) -> HttpRequest`
- `http_parse_response(raw) -> HttpResponse`
- `http_serialize_response(response) -> str`
- `http_serialize_request(host, method, path, body) -> str`
- `http_read_request(sock) -> HttpRequest`
- `http_read_response(sock) -> HttpResponse`
- `http_send_request(sock, host, method, path, body)`
- `http_send_response(sock, response)`
- `http_get(host, port, path) -> HttpResponse`
- `http_post(host, port, path, body) -> HttpResponse`
- `http_get_header(headers, name) -> str`

Headers are a list of `"Name: value"` strings so the library works with the
native reference-counted struct fields without a special dict layout.
