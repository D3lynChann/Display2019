from threading import Thread
from mySocket import *
from time import sleep, time
import pickle

def palFunc(portNum, msg, res):
    sok = initWebEnvC(port = portNum)
    sleep(2)
    print(pickle.loads(sok.recv(2048)))
    sleep(1)
    sok.send(pickle.dumps(msg))
    res[portNum] = msg

def actPal(func, argList, threads):
    for arg in argList:
        thread = Thread(target = func, args = arg)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    return argList[-1][-1]
        
def main():
    threads = []; argList = []; place = {}
    for i in range(16):
        argList.append((10000 + i, 'this is mission ' + str(i), place))
    start = time()
    res = actPal(palFunc, argList, threads)
    end = time()
    print(end - start)
    print(res)

if __name__ == '__main__':
    main()
