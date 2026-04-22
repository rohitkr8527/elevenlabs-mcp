import subprocess
import json
import threading


class MCPClient:
    def __init__(self, python_path: str, server_script: str, cwd: str):
        self.process = subprocess.Popen(
            [python_path, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
            bufsize=1,
        )

        self.lock = threading.Lock()
        self.id_counter = 0
        self._initialize()

    def _next_id(self) -> int:
        self.id_counter += 1
        return self.id_counter

    def _write_message(self, message: dict) -> None:
        if not self.process.stdin:
            raise RuntimeError("Server stdin is not available")
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def _read_until_response(self, request_id: int) -> dict:
        if not self.process.stdout:
            raise RuntimeError("Server stdout is not available")

        while True:
            line = self.process.stdout.readline()
            if not line:
                stderr_output = ""
                if self.process.stderr:
                    try:
                        stderr_output = self.process.stderr.read()
                    except Exception:
                        pass
                raise RuntimeError(f"Server closed connection. Stderr:\n{stderr_output}")

            line = line.strip()
            if not line:
                continue

            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue

            if response.get("id") == request_id:
                if "error" in response:
                    raise RuntimeError(response["error"])
                return response["result"]

    def _request(self, method: str, params: dict | None = None) -> dict:
        with self.lock:
            request_id = self._next_id()
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params or {},
            }
            self._write_message(request)
            return self._read_until_response(request_id)

    def _notify(self, method: str, params: dict | None = None) -> None:
        with self.lock:
            notification = {
                "jsonrpc": "2.0",
                "method": method,
            }
            if params:
                notification["params"] = params
            self._write_message(notification)

    def _initialize(self) -> None:
        self._request(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {
                    "name": "streamlit-mcp-client",
                    "version": "0.1.0",
                },
            },
        )
        self._notify("notifications/initialized")

    def list_tools(self) -> dict:
        return self._request("tools/list", {})

    def call_tool(self, name: str, arguments: dict | None = None) -> dict:
        result = self._request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

        if result.get("isError"):
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                raise RuntimeError(content[0].get("text", "Unknown MCP tool error"))
            raise RuntimeError("Unknown MCP tool error")

        content = result.get("content", [])
        if not content:
            return {}

        first = content[0]
        if first.get("type") == "text":
            text = first.get("text", "")
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}

        return {"raw": content}

    def close(self) -> None:
        try:
            if self.process.stdin:
                self.process.stdin.close()
        except Exception:
            pass
        try:
            self.process.terminate()
        except Exception:
            pass