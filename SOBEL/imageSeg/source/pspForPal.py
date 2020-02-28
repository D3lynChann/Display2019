from threading import Thread
from mySocket import *
import pickle

def palFunc(portNum, msg):
    sok, conn, address = initWebEnvS(port = portNum)
    conn.sendall(pickle.dumps(msg))
    print(pickle.loads(conn.recv(2048)))

def actPal(func, argList, threads):
    for arg in argList:
        thread = Thread(target = func, args = arg)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
        
def main():
    threads = []; argList = []
    for i in range(16):
        argList.append((10000 + i, 'this is mission ' + str(i)))
    actPal(palFunc, argList, threads)

if __name__ == '__main__':
    main()
