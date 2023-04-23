import socket
import json
import pdb

device_id = 'ea28b9e0e20e45b9b85553a878baaa2d'
groupid = '5bf2005d7cd447998bccac61464f4b72'
type = 'led'
state = 0

def readMsg(sock):
    reply = sock.recv(1024)
    return json.loads(reply.decode())

def client_loop(sock):
    global state

    command = 'CONNECT'
    payload = {'c': command, 'id': device_id, 'gid': groupid, 't': type, 's': state}
    sock.send(json.dumps(payload).encode())
    reply = readMsg(sock)
    print('server >> ' + reply['m'])

    while True:
        reply = readMsg(sock)
        command = reply['c']
        print('server >> %s' % command)

        if command == 'PING':
            sock.send(json.dumps({'m': 'ok', 's': state}).encode())
        elif command == 'UPDATE_STATE':
            state = reply['s']
            sock.send(json.dumps({'m': 'updated state to %d' % state, 's': state}).encode())
        elif command == 'EXIT':
            return


if __name__ == "__main__":
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    sock.connect(('localhost', 8081))

    client_loop(sock)

    print('closing client')
    sock.close()
