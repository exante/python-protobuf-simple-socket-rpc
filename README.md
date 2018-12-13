# Protobuf Socket RPC

Simple helper to send and read protobuf messages to/from socket.

## Example

```python
import socket

from google.protobuf.message import Message

socket = SocketRPC(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))

# in case if server requires handshake call
socket.handshake(b'AWESOME_RESPONSE', b'AWESOME_SERVER_PROTOCOL')

request = Message()
socket.send_message(request)
response = Message()
socket.read_message(response)

print(response)
```