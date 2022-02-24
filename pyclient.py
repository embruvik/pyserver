import socket
import json
import time
import os

HOST = os.getenv('GP_PYSERVER_HOST')
if not HOST:
    HOST = 'localhost'

PORT = os.getenv('GP_PYSERVER_HOST_PORT')
if not PORT:
    PORT = '32100'
PORT = int(PORT)


def call_pyserver(function_name, **kwargs):

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #s.connect(('localhost', PORT))
    s.connect((HOST, PORT))

    remotecall = {'function':function_name, 'args': kwargs}

    jsoncall = bytes(json.dumps(remotecall).encode('utf-8'))
    s.sendall(int.to_bytes(len(jsoncall),4,'little',signed=True))
    s.sendall(jsoncall)

    nbr = int.from_bytes(s.recv(4),'little',signed=True)
    print("Client got response of length: ",nbr)
    bytesr = s.recv(nbr)
    while len(bytesr) < nbr:
        bytesr = bytesr + s.recv(nbr-len(bytesr))
    pyobj = json.loads(bytesr)
    #print("Client got back: ", pyobj)

    s.close()
    return pyobj

if __name__ == '__main__':
    t1 = time.time()
    for n in range(0,500):
        rv = call_pyserver('greeter',name='Erik',greeting="it works!")
        rv2 = call_pyserver('obsgreeter',name='Erik')
    t2 = time.time()
    print('It took: ', t2-t1)