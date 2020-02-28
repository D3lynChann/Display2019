from plr import *
from pyaes import *
from mySocket import *
import os, numpy, pickle, AES

#psp

def getRes(li):
    return int(sum(li) / len(li))

def OTBob(sok, s):
    sok.send(pickle.dumps(s))
    return pickle.loads(sok.recv(2048))

def decryptGCT(GCT, keyA, keyB):
    for line in GCT:
        if getRes(AES.D(keyB, AES.D(keyA, line))) == 0:
            return 0
        if getRes(AES.D(keyB, AES.D(keyA, line))) == 1:
            return 1
    
def fullAdderBob(input_b, input_c1):
    sok = initWebEnvC()
    #XOR01
    gct1 = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfAlice = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfBob = OTBob(sok, input_b)
    w1 = decryptGCT(gct1, keyOfAlice, keyOfBob)
    #AND01
    gct2 = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfAlice = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfBob = OTBob(sok, input_b)
    w2 = decryptGCT(gct2, keyOfAlice, keyOfBob)
    #XOR03
    gct3 = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfc1 = OTBob(sok, input_c1)
    keyOfw1 = OTBob(sok, w1)
    w3 = decryptGCT(gct3, keyOfc1, keyOfw1)
    #AND04
    gct4 = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfc1 = OTBob(sok, input_c1)
    keyOfw1 = OTBob(sok, w1)
    w4 = decryptGCT(gct4, keyOfc1, keyOfw1)
    #OR05
    gct5 = pickle.loads(sok.recv(2048))
    sok.send(bytes(1))
    keyOfw4 = OTBob(sok, w4)
    keyOfw2 = OTBob(sok, w2)
    w5 = decryptGCT(gct5, keyOfw4, keyOfw2)
    #finish
    res = w3; c2 = w5
    sok.close()
    return res, c2
    
if __name__ == '__main__':
    inputs = [1, 0, 0, 0+]
    ress = []
    c = 0
    for input in inputs:
        res, c = fullAdderBob(input, c)
        ress.append(res)
    print(ress, c)
        