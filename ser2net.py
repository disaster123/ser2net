#!/usr/bin/python3

import socket
import sys
import serial

#open serial port
ser = serial.Serial('/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_EACGn19A322-if00-port0', 9600, timeout=120)
#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

server_address = ('172.17.0.1', 12055)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

#listen
sock.listen(1)

#loop
while True:
    print("REEINTER Connect True")
    #waits for a new connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)
        tcpbuf = b''
        serbuf = b''
        clientdead = False
        connection.settimeout(0.1)
        while True:
            data = b''

            # handle tcp data
            try:
                while True:
                    # this is pretty strange if we cannot read any data because no is available it raises an error like socket.timeout
                    # in case the connection is dead we get b'' back
                    data = connection.recv(1024) # read at most 1024 bytes - but timeout is set to 0.1
                    if data == b'':
                        connection.close()
                        clientdead = True
                        break
                    tcpbuf = tcpbuf + data
            except KeyboardInterrupt:
                connection.close()
                sys.exit()
            except socket.timeout:
                pass
            except Exception as e:
                print("tcp recv" + str(e))
                pass

            if clientdead:
                break

            # check if tcpbuf contains \n
            if len(data) == 0 and len(tcpbuf) > 0:
                print("Sending to serial: " + tcpbuf.hex())
                ser.write(tcpbuf)
                tcpbuf = b''

            # handle serial data
            data = ser.read(ser.inWaiting())
            serbuf = serbuf + data
            if len(data) == 0 and len(serbuf) > 0:
                sendstr = serbuf
                print("Sending to tcp: " + sendstr.hex())
                x = connection.sendall(sendstr)
                print(str(x))
                serbuf = b''

    except Exception as e:
        print(e)

    finally:
        #clean up connection
        connection.close()
