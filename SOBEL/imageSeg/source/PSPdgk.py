from plr import *
from mySocket import *
from time import time
#from damgard_jurik import keygen
import os, numpy, pickle, AES, random, pyaes, socket, GCT

GAUSSIAN_LITTLE_Q = 16
GAUSSIAN_LARGE_Q = 273
totalCtr = 0
bits = 20

def initKeys(keySize = 1024):
    pk, sk = plrInit(keySize)
    print('init keys finish...')
    return pk, sk

def bin(num, l):
    temp = abs(num)
    res = []
    while temp != 0:
        temp, remainder = divmod(temp, 2)
        res.append(remainder)
    while len(res) < l - 1:
        res.append(0)
    res.append(0 if num <= 0 else 1)   
    
    return res

def _TestSendPkAndSkToCloudServer(conn, pk, sk):
    pk_str = pickle.dumps(pk)
    sk_str = pickle.dumps(sk)
    print('sending pk to cs...')
    ask = conn.recv(2048)
    conn.sendall(pk_str)
    print('sending pk to cs...')
    ask = conn.recv(2048)
    conn.sendall(sk_str)
    print('sending finish, socket close...')  
'''    
def secCmpWithCs(pk0, sk0, pk1, sk1, conn, flags):
    a = decrypt(pickle.loads(conn.recv(4096)), sk0)
    conn.sendall(bytes(1))
    b = pickle.loads(conn.recv(4096))
    if flags == 0:
        res = encrypt(1, pk0) if a >= b else encrypt(-1, pk0)  
        conn.sendall(pickle.dumps(res))  
    elif flags == 1:
        res = encrypt(255, pk0) if a >= b else encrypt(0, pk0)
        conn.sendall(pickle.dumps(res))  
    elif flags == 2:
        res0 = encrypt(0, pk0); res1 = encrypt(1, pk0)
        res = [res1, res0] if a >= b else [res0, res1]
        conn.sendall(pickle.dumps(res))
'''        
def secCmpWithCs(pk0, sk0, pk1, sk1, conn, flags):
    a = decrypt(pickle.loads(conn.recv(4096)), sk0)
    a_b_p = bin(a, bits)
    for ctr in range(bits):
        conn.sendall(pickle.dumps(pk1.encrypt(a_b_p[ctr])))
        conn.recv(1)
    tempRes = []    
    for ctr in range(bits):
        tempRes.append(pickle.loads(conn.recv(4096)))
        conn.sendall(bytes(1))
    if flags == 0:
        res = encrypt(1, pk0)    
        for item in tempRes:
            if int(sk1.decrypt(item)) == 0:
                res = encrypt(-1, pk0)  
        conn.sendall(pickle.dumps(res))  
    elif flags == 1:
        res = encrypt(255, pk0)    
        for item in tempRes:
            if int(sk1.decrypt(item)) == 0:
                res = encrypt(0, pk0)  
        conn.sendall(pickle.dumps(res))  
    elif flags == 2:
        res0 = encrypt(0, pk0); res1 = encrypt(1, pk0); res = [res1, res0]
        for item in tempRes:
            if int(sk1.decrypt(item)) == 0:
                res = [res0, res1]  
        conn.sendall(pickle.dumps(res)) 

def secMulWithCS(conn, pk, sk):
    package = pickle.loads(conn.recv(8192))
    conn.sendall(pickle.dumps(encrypt(decrypt(package[0], sk) * decrypt(package[1], sk), pk)))

def secDivWithCS(conn, pk, sk):
    c6, S = pickle.loads(conn.recv(8192))
    c4 = encrypt(S // decrypt(c6, sk), pk)
    conn.sendall(pickle.dumps(c4))
    secMulWithCS(conn, pk, sk) 
        
def SobelWithCloudServer(conn, pk0, sk0, pk1, sk1):
    print('Sobel start...')
    times = pickle.loads(conn.recv(8192))
    print('need to do', str(times), 'comparison with cloud server...')
    conn.sendall(bytes(1))
    for ctr in range(times):
        secCmpWithCs(pk0, sk0, pk1, sk1, conn, 0)
        secCmpWithCs(pk0, sk0, pk1, sk1, conn, 0)
        secMulWithCS(conn, pk0, sk0)
        secMulWithCS(conn, pk0, sk0)
    print('Sobel finish...')           

def getThreshold(conn, pk0, sk0, pk1, sk1):
    maxTime = 2
    times = pickle.loads(conn.recv(2048))
    conn.sendall(bytes(1))
    while maxTime > 0:
        for ctr in range(times):
            secCmpWithCs(pk0, sk0, pk1, sk1, conn, 2)
            secMulWithCS(conn, pk0, sk0)
            secMulWithCS(conn, pk0, sk0)
        secDivWithCS(conn, pk0, sk0)
        secDivWithCS(conn, pk0, sk0)
        secCmpWithCs(pk0, sk0, pk1, sk1, conn, 0)
        secMulWithCS(conn, pk0, sk0)
        tube = pickle.loads(conn.recv(4096))
        maxTime -= 1
        if decrypt(tube[0], sk0) < tube[1]:
            conn.sendall(pickle.dumps('yes!'))
            break
        else:
            conn.sendall(pickle.dumps('continue!'))
        if maxTime == 0:
            print('meet maxTime!')
        
def BinIt(conn, pk0, sk0, pk1, sk1):
    times = pickle.loads(conn.recv(2048))
    conn.sendall(bytes(1))
    for ctr in range(times):
        secCmpWithCs(pk0, sk0, pk1, sk1, conn, 1)
        
def hybridSystem():
    #construct sok
    sok, conn, address = initWebEnvS(port = 10010)
    #Paillier keys generation and distribution
    pk0, sk0 = initKeys(keySize = 128) 
    _TestSendPkAndSkToCloudServer(conn, pk0, sk0)
    #DGK keys generation and distribution
    pk1, sk1 = keygen(n_bits = 32)
    _TestSendPkAndSkToCloudServer(conn, pk1, sk1)
    #Sobel it
    SobelWithCloudServer(conn, pk, sk)
    #get thres
    getThreshold(conn, pk0, sk0, pk1, sk1)
    #Bina it
    BinWithCloudServer(conn, pk0, sk0, pk1, sk1)
    #close it
    conn.close()      

if __name__ == '__main__':
    hybridSystem()
