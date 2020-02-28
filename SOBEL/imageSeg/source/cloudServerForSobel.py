from plr import *
from mySocket import *
import os, numpy, pickle, AES, random, pyaes, socket, math, time
import random
from damgard_jurik import keygen

def init(scale, gaussian_l):
    return 1 + scale + math.ceil(math.log10(gaussian_l)) 

def _testGetPkAndSkFromPsp(sok):
    print('ask for pk...')
    sok.send('ask..'.encode())
    pk_str = sok.recv(8192)
    print('ask for sk...')
    sok.send('ask..'.encode())
    sk_str = sok.recv(8192)
    pk = pickle.loads(pk_str)
    sk = pickle.loads(sk_str)
    
    print('get pk and sk from psp...')
    print('now socket is closing...')
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
  
def packWithPlr(inputList, l, pk):
    L = len(inputList)
    res = encrypt(0, pk)
    for ctr in range(L):
        res = addCipher(res, mulClear(inputList[ctr], pow(10, ctr * l)))
    return res  

def decryptGCTs(sign, inputValueY, inputValueX, GCT, numOfGate, c_init, c0):
    subC = c_init; finalC = []
    for ctr in range(numOfGate):
        res = []
        for line in GCT:
            res = AES.D(AES.generateAES(bytes(subC)), AES.D(AES.generateAES(inputValueY[ctr]), AES.D(AES.generateAES(inputValueX[ctr]), line)))
            if res[: 8] == sign:
                subC = bytes(res)
                break    
                
    finalC = (0 if subC == c0 else 1)
                
    return finalC    

def getInputValue(inputList, x):
    res = []
    ctr = 0
    for i in inputList:
        res.append(x[i][ctr])
        ctr += 1
    return res 

def BobGenerateCsAndS(d_hat_e, r_hat, r_hat_e, one_e, zero_e, pk):
    #if s == 1: no 0 in c if d > r
    w_e = []; l = len(d_hat_e)
    
    #w = d XOR r
    for ctr in range(len(r_hat)):
        if r_hat[ctr] == 0:
            w_e.append(d_hat_e[ctr])
        else:
            w_e.append(one_e - d_hat_e[ctr])
    
    #sum^{l - 1}_{j = i + 1}{w_j}
    sum_w_e = [None for ctr in range(l)]
    sum_w_e[l - 1] = zero_e
    for ctr in range(l - 2, -1, -1):
        sum_w_e[ctr] = sum_w_e[ctr + 1] + w_e[ctr + 1]
    
    #s in {-1, 1}    
    s = 1 if random.randint(0, 100) % 2 else -1
    s_e = pk.encrypt(s)
    
    #c = d - r + s + 3*sum_w
    c_e = []
    for ctr in range(l):
        r = random.randint(0, 1024)
        c_e.append(r * (d_hat_e[ctr] - r_hat_e[ctr] + s_e + (3 * sum_w_e[ctr])))
        
    return c_e, s    

def BobGetTheRes(s, lamda_e, one_e):
    return one_e - lamda_e if s == -1 else lamda_e
    
def testComp():
    sok = initWebEnvC(port = 10017)
    
    start = time.time()
    pk0, sk0 = _testGetPkAndSkFromPsp(sok)
    one_e0 = pk0.encrypt(1); zero_e0 = pk0.encrypt(0)
    
    pk, sk = _testGetPkAndSkFromPsp(sok)
    one_e = pk.encrypt(1); zero_e = pk.encrypt(0)
    
    #from left to right
    r_hat = [1, 0, 1, 1, 0, 0, 0, 1]
    r_hat_e = [pk.encrypt(item) for item in r_hat]
    
    lenOfD_Hat_e = pickle.loads(sok.recv(8192))
    sok.send(bytes(1))
    d_hat_e = []
    for ctr in range(lenOfD_Hat_e):
        d_hat_e.append(pickle.loads(sok.recv(8092)))
        sok.sendall(bytes(1))
    
    c_e, s = BobGenerateCsAndS(d_hat_e, r_hat, r_hat_e, one_e, zero_e, pk)
    
    sok.send(pickle.dumps(len(c_e)))
    sok.recv(1)
    for item in c_e:
        sok.send(pickle.dumps(item))
        sok.recv(1)
    
    lamda_e = pickle.loads(sok.recv(8192))
    sok.send(bytes(1))
    
    res = BobGetTheRes(s, lamda_e, one_e0)
    end = time.time()
    print(sk0.decrypt(res))
    print('time:', end - start)
    
def test():
    numOfGates = 8
    pk, sk = _testGetPkAndSkFromPsp()
    
    s_x = [encrypt(item, pk) for item in [3, 1, 4]]
    a_x = random.randint(1, 100)
    a_xc = encrypt(a_x, pk)
    s_y = [encrypt(item, pk) for item in [5, 2, 1]]
    a_y = random.randint(1, 100)
    a_yc = encrypt(a_y, pk)
    
    l = init(3, 16 * 255)
    L = len(s_x)
    
    sa_x = addCipher(packWithPlr(s_x, l, pk), packWithPlr([a_xc for ctr in range(L)], l, pk))
    sa_y = addCipher(packWithPlr(s_y, l, pk), packWithPlr([a_yc for ctr in range(L)], l, pk))
    sok = initWebEnvC(port = 10010)
    sok.send(pickle.dumps([l, L]))
    sok.recv(1)
    sok.send(pickle.dumps(sa_x))
    sok.recv(1)
    sok.send(pickle.dumps(sa_y))
    sok.recv(1)
    
    starttime = time.time()
    
    ch = pickle.loads(sok.recv(8192))
    beta = a_x - a_y if ch == 0 else a_y - a_x
    b_b = bin(beta, numOfGates)
    
    #print('ok!')
    #print('arfa_x:', a_x, '\narfa_y:', a_y)
    print('beta_b:', b_b)
    finalRes = []
    
    for ctr in range(L):
        #get GCT
        GCT = []
        for itr in range(8 * numOfGates):
            GCT.append(pickle.loads(sok.recv(8192)))
            sok.send(bytes(1))	
        #print(GCT)        
        start = time.time()     
        #get sign
        sign = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        #get y
        y = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        #get initC
        subC = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        #get c0
        c0 = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        inputValueY = getInputValue(b_b, y)
        res = []
        
        #x - delta, y - beta
        startGCT = time.time() 
        for itr in range(numOfGates):
            inputValueX = pickle.loads(sok.recv(8192))
            sok.send(bytes(1))
            for line in GCT:
                res = AES.D(AES.generateAES(bytes(subC)), AES.D(AES.generateAES(inputValueY[itr]), AES.D(AES.generateAES(inputValueX[itr]), line)))
                if res[: 8] == sign:
                    subC = bytes(res)
                    break            
        finalC = (0 if subC == c0 else 1)
        print('res:', finalC)
        endGCT = time.time()
        print('decrypt time:', endGCT - startGCT)
        sok.send(pickle.dumps(finalC))
        sok.recv(1)
        
        h2 = [b_b[-1]]
        fGCT = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        fsign = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        fy = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        fsubC = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        fc0 = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        finputValueY = getInputValue(h2, fy)
        fres = []
        
        finputValueX = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        
        for line in fGCT:
            fres = AES.D(AES.generateAES(bytes(fsubC)), AES.D(AES.generateAES(finputValueY[0]), AES.D(AES.generateAES(finputValueX[0]), line)))
            if fres[: 8] == fsign:
                fsubC = bytes(fres)
                break    
                
        ffinalC = (0 if fsubC == fc0 else 1)   
        print('h2:', h2, 'finalC:', finalC, 'ffinalC:', ffinalC)
        
        
        end = time.time()
        print('time:', end - start)
        delta = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        finalRes.append(delta - beta if ffinalC == 1 else beta - delta)
        
    print(finalRes) 
         
    endtime = time.time()
    print(endtime - starttime)
       
def testMul():
    sok = initWebEnvC(port = 10017)
    pk, sk = _testGetPkAndSkFromPsp(sok)
    a = pk.encrypt(8); b = pk.encrypt(9); r1 = pk.encrypt(2); r2 = pk.encrypt(3)
    start = time.time()
    a_hat = a - r1; b_hat = b - r2
    sok.send(pickle.dumps(a_hat))
    sok.recv(1)
    sok.send(pickle.dumps(b_hat))
    ab_hat = pickle.loads(sok.recv(8192))
    ab = ab_hat + a * 3 + b * 2 - pk.encrypt(6)
    end = time.time()
    print(sk.decrypt(ab), end - start)  
     
    
if __name__ == '__main__':
    #testComp()
    testMul()
