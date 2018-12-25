#-*- coding:utf-8 -*-
import socket


def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    client(HOST, PORT, "Hello World 1")
    client(HOST, PORT, "Hello World 2")
    client(HOST, PORT, "Hello World 3")
