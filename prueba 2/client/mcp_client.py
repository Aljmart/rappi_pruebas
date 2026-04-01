import json
import socket

class MCPClient:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port

    def call_tool(self, tool_name, args):
        message = {
            "type": "call_tool",
            "tool": tool_name,
            "arguments": args
        }

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(json.dumps(message).encode("utf-8"))

            data = s.recv(65535)
            return json.loads(data.decode("utf-8"))
