import subprocess
import sys
import socket
import os
import time
import threading
import json

PORT = 32100 # port for client connections
nworkers = 1

# set up workers
pyprocs = []
socknames = []
wsocks = []
wisbusy = []
for i in range(0,nworkers):
    socknames.append(f'pyworker{i:02d}')
    s = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    try:
        s.bind(socknames[i])
    except OSError:
        os.unlink(socknames[i])
        s.bind(socknames[i])
    s.listen()
    
    wsocks.append(s)

    pyprocs.append(subprocess.Popen([sys.executable, "pyworker.py", socknames[i]]))
    wisbusy.append(False)

wconns = []
for s in wsocks:
    conn,addr = s.accept()
    wconns.append(conn)
    read = conn.recv(2)
    print('Pyserver read from worker: ', read)

# Set up port for clients
csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
csock.bind((socket.gethostname(), PORT))
csock.listen()

gbusylock = threading.Lock()
def request_thread(clientconn):

    # Find non-busy worker - store in wi
    while True:
        gbusylock.acquire()
        wi = wisbusy.index(False)
        if wi == -1:
            gbusylock.release()
            time.sleep(0.1)
        else:
            wisbusy[wi] = True
            gbusylock.release()
            break
    
    try:
        # read message from client and pass to worker
        lenbytes = clientconn.recv(4)
        nbr = int.from_bytes(lenbytes,'little',signed=True)
        objbytes = clientconn.recv(nbr)
        wconns[wi].send(lenbytes)
        wconns[wi].send(objbytes)

        # read response from worker and pass on to client
        lenbytes = wconns[wi].recv(4)
        nbr = int.from_bytes(lenbytes,'little',signed=True)
        objbytes = wconns[wi].recv(nbr)
        clientconn.send(lenbytes)
        clientconn.send(objbytes)
    except Exception as e:
        print("Error occurred while talking to client(/or worker): ", e)
        raise
    finally:
        wisbusy[wi] = False
    

# Loop to wait for client connections
while True:
    try:
        cconn, caddr = csock.accept()
        print("Pyserver got contacted by: ", str(caddr))
    except KeyboardInterrupt as e:
        print('Blah, will try to ignore...')
        raise(e)
    else:
        t = threading.Thread(target=request_thread,args=(cconn,))
        t.start()
