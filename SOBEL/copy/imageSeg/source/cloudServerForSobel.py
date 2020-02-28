from plr import *
from mySocket import *
import os, numpy, pickle, AES, random, pyaes, socket, math, time

def init(scale, gaussian_l):
    return 1 + scale + math.ceil(math.log10(gaussian_l)) 

def _testGetPkAndSkFromPsp():
    sok = initWebEnvC()
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
    sok.close() 
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
    
def test():
    numOfGates = 8
    pk, sk = _testGetPkAndSkFromPsp()
    
    s_x = [encrypt(item, pk) for item in [88, 122, 112, 144, 88, 122, 112, 144]]
    a_x = random.randint(1, 100)
    a_xc = encrypt(a_x, pk)
    s_y = [encrypt(item, pk) for item in [99, 188, 102, 222, 88, 122, 112, 144]]
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
    b_b = bin(a_x - a_y if ch == 0 else a_y - a_x, numOfGates)
    
    #print('ok!')
    #print('arfa_x:', a_x, '\narfa_y:', a_y)
    #print('beta_b:', b_b)
    finalRes = []
    
    for ctr in range(L):
        #get GCT
        print('getting', ctr, 'th GCTs!') 
        GCT = []
        for itr in range(numOfGates):
            GCT.append(pickle.loads(sok.recv(8192)))
            sok.send(bytes(1))		       
            print(itr) 
        print('get GCT')
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
        
        for itr in range(numOfGates):
            inputValueX = pickle.loads(sok.recv(8192))
            sok.send(bytes(1))
            for line in GCT:
                res = AES.D(AES.generateAES(bytes(subC)), AES.D(AES.generateAES(inputValueY[ctr]), AES.D(AES.generateAES(inputValueX[ctr]), line)))
                if res[: 8] == sign:
                    subC = bytes(res)
                    break    
        finalC = (0 if subC == c0 else 1)
        #print(finalC)
        
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
        #print('h2:', h2, 'finalC:', finalC, 'ffinalC:', ffinalC)
        
        finalRes.append(ffinalC) 
    #print(finalRes) 
         
    endtime = time.time()
    print(endtime - starttime)
    
if __name__ == '__main__':
    test()
