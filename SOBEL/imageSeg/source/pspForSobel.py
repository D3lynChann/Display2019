from plr import *
from mySocket import *
from time import time
import os, numpy, pickle, AES, random, pyaes, socket
from time import time
import random
from damgard_jurik import keygen

TVTComp = [[0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1]]

TVTMux = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1]]

def generateRanKey(sign, l):
    return sign + os.urandom(l)
    
def initKeys(keySize = 1024):
    pk, sk = plrInit(keySize)
    #print('init keys finish...')
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
    
def unpackedFromCloudServer(conn, pk, sk, l, L):
    '''
        l, L通过外部获取,顺便解包了┗|｀O′|┛ 嗷~~
    '''
    inputStr = str(decrypt(pickle.loads(conn.recv(8192)), sk))
    res = []
    res.append(int(inputStr[-1 * l + 1: ]))
    for ctr in range(1, L):
        cur = int(inputStr[l * -1 * (ctr + 1) + 1: l * -1 * ctr])
        res.append(cur)
    return res       

def createGCTs(numOfGates, trueValueTable):
    #initial wires' garbled values
    sign = os.urandom(8)
    x = [[], []]
    y = [[], []]
    c = [[], []]
    GCT = []
    
    #genarate keys
    c[0].append(generateRanKey(sign, 8))
    c[1].append(generateRanKey(sign, 8))
    for i in range(numOfGates):
        for j in range(2):
            x[j].append(generateRanKey(bytes(0), 16))
            y[j].append(generateRanKey(bytes(0), 16))
            c[j].append(generateRanKey(sign, 8))
    
    #use true value table to genarate GCTs
    #GCT[gate No.][s_GCT or c_GCT][garbled value No.]

    for ctr in range(numOfGates):
        for ta in trueValueTable:
            GCT.append(AES.E(AES.generateAES(x[ta[0]][ctr]), AES.E(AES.generateAES(y[ta[1]][ctr]), AES.E(AES.generateAES(c[ta[2]][ctr]), c[ta[3]][ctr + 1]))))  
    
    #create an list sign
    sign = list(sign)
    
    return x, y, c, sign, GCT   
 
def getInputValue(inputList, x):
    res = []
    ctr = 0
    for i in inputList:
        res.append(x[i][ctr])
        ctr += 1
    return res 
 
def AliceDecryptCs(sk, c_e, one_e, zero_e):
    #if there is a 0 in c_e, return [1]
    for item in c_e:
        if int(sk.decrypt(item)) == 0:
            return zero_e
    return one_e 
 
def testComp():
    sok, conn, address = initWebEnvS(port = 10017) 
    
    pk0, sk0 = initKeys(2048)
    one_e0 = pk0.encrypt(1); zero_e0 = pk0.encrypt(0)
    _TestSendPkAndSkToCloudServer(conn, pk0, sk0)
    
    pk, sk = keygen(n_bits = 512)
    one_e = pk.encrypt(1); zero_e = pk.encrypt(0)
    _TestSendPkAndSkToCloudServer(conn, pk, sk)
    
    #from left to right
    d_hat = [0, 1, 1, 0, 1, 1, 1, 1]
    d_hat_e = [pk.encrypt(item) for item in d_hat]
    
    conn.sendall(pickle.dumps(len(d_hat_e)))
    conn.recv(1)
    for item in d_hat_e:
        conn.sendall(pickle.dumps(item))
        conn.recv(1)
    
    lenOfC_e = pickle.loads(conn.recv(8192))
    conn.sendall(bytes(1))
    c_e = []
    
    for ctr in range(lenOfC_e):
        c_e.append(pickle.loads(conn.recv(8092)))
        conn.sendall(bytes(1))
        
    lamda_e = AliceDecryptCs(sk, c_e, one_e0, zero_e0)
    
    conn.sendall(pickle.dumps(lamda_e))
    conn.recv(1)
    conn.close()
 
def test():
    numOfGates = 8
    pk, sk = initKeys(1024)
    _TestSendPkAndSkToCloudServer(pk, sk)
    sok, conn, address = initWebEnvS(port = 10010) 
    lL = pickle.loads(conn.recv(8192))  #l and L
    conn.sendall(bytes(1))
    sa_x = unpackedFromCloudServer(conn, pk, sk, lL[0], lL[1])
    conn.sendall(bytes(1))
    sa_y = unpackedFromCloudServer(conn, pk, sk, lL[0], lL[1])
    conn.sendall(bytes(1))
    
    print('psp')
    
    ch = random.randint(0, 100) % 2
    delta = []
    
    for ctr in range(lL[1]):
        delta.append((sa_x[ctr] - sa_y[ctr]) if ch == 0 else (sa_y[ctr] - sa_x[ctr]))
    
    print('delta:', delta)
    #OT
    conn.sendall(pickle.dumps(ch))
    
    deltaB = [bin(item, numOfGates) for item in delta]
    
    print('s_x + arfa_x:', sa_x, '\ns_y + arfa_y:', sa_y)
    print('delta:', delta)
    
    for ctr in range(lL[1]):
        start = time()
        x, y, c, sign, GCT = createGCTs(numOfGates, TVTComp)	
        #print(GCT)       
        end = time()
        #print('time:', end - start)
        #send GCT
        for gts in GCT: 
            conn.sendall(pickle.dumps(gts))
            conn.recv(1)
        #send sign
        conn.sendall(pickle.dumps(sign))
        conn.recv(1)
        #send y
        conn.sendall(pickle.dumps(y))
        conn.recv(1)
        #send initC
        conn.sendall(pickle.dumps(c[0][0]))
        conn.recv(1)
        #send c0
        conn.sendall(pickle.dumps(c[0][numOfGates]))
        conn.recv(1)
        
        inputXs = getInputValue(deltaB[ctr], x)
        for itr in range(numOfGates):
            conn.sendall(pickle.dumps(inputXs))
            conn.recv(1)
        
        
        finalC = pickle.loads(conn.recv(8192))
        conn.sendall(bytes(1))
        
        h1 = [deltaB[ctr][-1]]
        fx, fy, fc, fsign, fGCT = createGCTs(1, TVTMux)
        
        conn.sendall(pickle.dumps(fGCT))
        conn.recv(1)
        
        conn.sendall(pickle.dumps(fsign))
        conn.recv(1)
        
        conn.sendall(pickle.dumps(fy))
        conn.recv(1)
        
        conn.sendall(pickle.dumps(fc[finalC][0]))
        conn.recv(1)
        
        conn.sendall(pickle.dumps(fc[0][1]))
        conn.recv(1)
        
        finputXs = getInputValue(h1, fx)
        
        conn.sendall(pickle.dumps(finputXs))
        conn.recv(1)  
        
        conn.sendall(pickle.dumps(delta[ctr]))
        conn.recv(1)
        print('h1:', h1, 'cin:', finalC)
        
def testMul():
    sok, conn, address = initWebEnvS(port = 10017)
    pk, sk = initKeys(2048)
    _TestSendPkAndSkToCloudServer(conn, pk, sk)
    a_hat = pickle.loads(conn.recv(8192))
    conn.sendall(bytes(1))
    b_hat = pickle.loads(conn.recv(8192))
    conn.sendall(pickle.dumps(pk.encrypt(sk.decrypt(a_hat) * sk.decrypt(b_hat))))
    conn.close()
    
if __name__ == '__main__':
    #testComp()
    testMul()
