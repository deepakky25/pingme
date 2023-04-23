import socket
import json
import pdb

command_seperator = ' '
user_id = '3b8b396cb40b491fa85f9e8af3eb72a0'
groupid = '5bf2005d7cd447998bccac61464f4b72'
type = 'user'

def client_loop(sock):
    command = 'CONNECT'
    while True:
        payload = {'c': command, 'id': user_id, 'gid': groupid, 't': type}

        dataMessage = command.split(command_seperator)
        command = dataMessage[0]

        if command == 'EXIT':
            # Send out EXIT command and exit the loop
            sock.send(json.dumps(payload).encode())
            break
        elif command == 'UPDATE_STATE':
            if len(dataMessage) == 3:
                payload['s'] = int(dataMessage[2])
                sock.send(json.dumps(payload).encode())
        else:
            # Send command
            sock.send(json.dumps(payload).encode())

        # Wait for response from server and print it
        reply = sock.recv(1024)
        reply = json.loads(reply.decode())

        if command == 'STATUS':
            print('server >> active devices %d' % reply['m']['c'])
            print('server >> active device:')
            for i in reply['m']['ad']:
                print('       >> id:%s state:%d' % (i, reply['m']['ad'][i]))
        else:
            print('server >> ' + reply['m'])

        # Wait for a new command
        command = input('Enter your command\n')

if __name__ == "__main__":
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    sock.connect(('localhost', 8081))

    client_loop(sock)

    print('closing client')
    sock.close()
