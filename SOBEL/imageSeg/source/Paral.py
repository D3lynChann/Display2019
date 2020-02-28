from threading import Thread
from time import sleep, time
import math

def testPalFunc(a, b):
    print(a + b)
    
def palFunc(func, argList, threads):
    for arg in argList:
        thr = Thread(target = func, args = arg)
        thr.start()
        threads.append(thr)
    for thr in threads:
        thr.join()    

def test():
    threads = []; argList = []
    for i in range(20):
        argList.append((i, i))
    palFunc(testPalFunc, argList, threads)    
        
   
if __name__ == '__main__' :
    test()
