import pdb
import time
import json
import socket
import threading
import socketserver

command_seperator = ' '
registered_groups = ['5bf2005d7cd447998bccac61464f4b72']
active_group = {}

class Group:
    def __init__(self, id):
        self.id = id
        self.users = {}
        self.devices = {}
        self.active_devices = 0
        self.active_users = 0
        self.name = 'Group1'

    def addUser(self, id, connection):
        if id in self.users:
            print('user %s already registerd in group' % id)
            return

        user = User(id, connection)
        self.users[id] = user
        self.active_users += 1

    def removeUser(self, id):
        if id not in self.users:
            return

        del self.users[id]
        self.active_users -= 1

    def addDevice(self, id, type, state, connection):
        if id in self.devices:
            print('device %s already registerd in group' % id)
            return

        device = Device(id, type, state, connection)
        self.devices[id] = device
        self.active_devices += 1

    def removeDevice(self, id):
        if id not in self.devices:
            return

        del self.devices[id]
        self.active_devices -= 1

    def updateDeviceState(self, id, s):
        pdb.set_trace()
        if id in self.devices:
            self.devices[id].state = s

    def msgDevice(self, id, state):
        pdb.set_trace()
        if id in self.devices:
            device = self.devices[id]
            device.connection.sendall(json.dumps({'c': 'UPDATE_STATE', 's': state}).encode())

            data = device.connection.recv(1024).strip()
            data = json.loads(data.decode())
            print('%s >> %s' % (id, data['m']))

            self.updateDeviceState(id, data['s'])

    def getStatus(self):
        devices = {}
        for d in self.devices:
            devices[d] = self.devices[d].state

        return {
            'c': self.active_devices,
            'ad': devices
        }


class User:
    def __init__(self, id, connection):
        self.id = id
        self.connection = connection

class Device:
    def __init__(self, id, type, state, connection):
        self.id = id
        self.type = type
        self.state = state
        self.connection = connection


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def updateGroup(self, type, group_id, id, state, connection):
        if group_id in registered_groups:
            group = None
            try:
                group = active_group[group_id]
            except KeyError as e:
                print('Group %s is inactive' % group_id)

            if group == None:
                group = Group(group_id)
                active_group[group_id] = group
                print('Group %s activated' % group_id)

            if type == 'user':
                group.addUser(id, connection)
            else:
                group.addDevice(id, type, state, connection)

            return group
        else:
            return None

    def device_handler(self, data, type):
        self.group = self.updateGroup(type, data['gid'], data['id'], data['s'], self.request)
        if self.group == None:
            self.request.sendall(json.dumps({'m': 'group unknow'}).encode())
            return

        self.request.sendall(json.dumps({'m': 'device connected'}).encode())

        # A big loop that sends/receives data until told not to.
        while True:

            time.sleep(5 * 60)

            self.request.sendall(json.dumps({'c': 'PING'}).encode())

            data = self.request.recv(1024).strip()
            data = json.loads(data.decode())
            self.group.updateDeviceState(id, data['s'])
            print('%s >> PING %s State %d' % (self.client_address[0], data['m'], data['s']))

    def user_handler(self, data, type):
        self.group = self.updateGroup(type, data['gid'], data['id'], None, self.request)
        if self.group == None:
            self.request.sendall(json.dumps({'m': 'group unknow'}).encode())
            return

        self.request.sendall(json.dumps({'m': 'user connected'}).encode())

        # A big loop that sends/receives data until told not to.
        while True:
            reply = ''
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode())
            print('%s >> %s %s' % (self.client_address[0], data['c'], data['id']))

            dataMessage = data['c'].split(command_seperator)
            command = dataMessage[0]

            if command == 'STATUS':
                reply = self.group.getStatus()
            elif command == 'EXIT':
                self.group.removeUser(self.data['id'])
                break
            elif command == 'UPDATE_STATE':
                if len(dataMessage) > 2:
                    device_id = dataMessage[1]
                    state = data['s']

                    self.group.msgDevice(device_id, state)
                    reply = 'device %s state updated' % device_id
                else:
                    reply = 'invalid update state command'
            else:
                self.reply = 'unknown command'

            # Send the reply back to the client
            self.request.sendall(json.dumps({'m': reply}).encode())

    def handle(self):
        print('connection from', self.client_address[0])
        try:

            data = self.request.recv(1024).strip()
            data = json.loads(data.decode())
            print('%s >> %s %s' % (self.client_address[0], data['c'], data['id']))

            dataMessage = data['c'].split(' ')
            command = dataMessage[0]
            type = data['t']

            if command != 'CONNECT':
                self.request.sendall(json.dumps({'m': 'command unknow'}).encode())

            else:
                if type != 'user':
                    self.device_handler(data, type)
                else:
                    self.user_handler(data, type)

        finally:
            # Clean up the connection
            print('closing current connection')
            self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    try:
        with ThreadedTCPServer(('localhost', 8081), ThreadedTCPRequestHandler) as server:
            print('waiting for a connection')
            server.serve_forever()
    except KeyboardInterrupt:
        print('closing server')
