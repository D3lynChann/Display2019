from plr import *
from mySocket import *
from time import time
import os, numpy, pickle, AES, random, pyaes, socket, GCT

GAUSSIAN_LITTLE_Q = 16
GAUSSIAN_LARGE_Q = 273
totalCtr = 0

#filePath = 'G:/codes/imageSeg/source'    
filePath = '.'
#filePath = 'C:/Users/D3lyn/Desktop/imageSeg/source'

def getBinFile():
    file = open(filePath + '/bina.txt', 'r')
    lines = file.readlines()
    file.close()    
    res = []
    for line in lines:
        temp = []
        for ctr in range(8):
            temp.append(int(line[ctr]))
        res.append(temp)
    return res
    
#binFile = getBinFile()

def bina8(input):
    return binFile[1023 + input]

def initKeys(keySize = 1024):
    pk, sk = plrInit(keySize)
    print('init keys finish...')
    return pk, sk

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

def divPtcWithCloudServer(conn, pk, sk):
    inputA = decrypt(pickle.loads(conn.recv(8192)), sk)
    conn.sendall(bytes(1))
    inputB = pickle.loads(conn.recv(8192))
    conn.sendall(pickle.dumps(encrypt(inputA // inputB, pk)))  

def GaussianWithCloudServer(conn, pk, sk):
    print('Gaussian start...')
    times = pickle.loads(conn.recv(8192))
    print('need to do', str(times), 'division with cloud server...')
    for ctr in range(times):
        divPtcWithCloudServer(conn, pk, sk)
    print('Gaussian finish...') 

def compPtcWithCloudServer(conn, pk, sk):
    flag = pickle.loads(conn.recv(8192))
    conn.sendall(bytes(1))
    inputA = decrypt(pickle.loads(conn.recv(8192)), sk)
    conn.sendall(bytes(1))
    inputB = decrypt(pickle.loads(conn.recv(8192)), sk)
    if flag == 1:
        conn.sendall(pickle.dumps(encrypt(inputA if inputA >= inputB else inputB, pk)))
    elif flag == 0:
        conn.sendall(pickle.dumps(encrypt(inputA if inputB >= inputA else inputB, pk)))
        
def SubBinaWithCloudServer(black, white, T, conn, pk, sk):
    input = decrypt(pickle.loads(conn.recv(8192)), sk)
    if input >= T:
        conn.sendall(pickle.dumps(white))
    else:
        conn.sendall(pickle.dumps(black))

def BinWithCloudServer(black, white, conn, pk, sk):
    print('Bina start...')
    times = pickle.loads(conn.recv(8192))
    print('need to do', str(times), 'comparison with cloud server...')
    conn.sendall(bytes(1))
    T = decrypt(pickle.loads(conn.recv(8192)), sk)
    conn.sendall(bytes(1))
    for ctr in range(times):
        SubBinaWithCloudServer(black, white, T, conn, pk, sk)
    print('Bina finish...')
        
def SobelWithCloudServer(conn, pk, sk):
    print('Sobel start...')
    times = pickle.loads(conn.recv(8192))
    print('need to do', str(times), 'comparison with cloud server...')
    conn.sendall(bytes(1))
    for ctr in range(times):
        compPtcWithCloudServer(conn, pk, sk)
        compPtcWithCloudServer(conn, pk, sk)
        compPtcWithCloudServer(conn, pk, sk)
        compPtcWithCloudServer(conn, pk, sk)
    print('Sobel finish...')         

def firstPassWithCloudServer(conn, pk, sk):
    cur = 0; sts = []; te = 0
    size = pickle.loads(conn.recv(8192))
    numsOfConnectedArea = [1 for ctr in range(size)]
    for ctr in range(size):
        msg = pickle.loads(conn.recv(8192))
        leftP = decrypt(msg[0], sk); upP = decrypt(msg[1], sk); nowP = decrypt(msg[2], sk)
        conn.sendall(bytes(1))
        lbl = pickle.loads(conn.recv(8192))
        leftL = decrypt(lbl[0], sk); upL = decrypt(lbl[1], sk)
        if nowP == 0:
            conn.sendall(pickle.dumps(encrypt(0, pk)))
        elif nowP != 0:    
            if leftP == upP == 0:
                cur += 1
                conn.sendall(pickle.dumps(encrypt(cur, pk)))
            elif leftP == 0 and upP != 0:
                conn.sendall(pickle.dumps(lbl[1]))
            elif leftP != 0 and upP == 0:
                conn.sendall(pickle.dumps(lbl[0]))
            else:
                te += 1
                minL = min(leftL, upL)
                maxL = max(leftL, upL)
                conn.sendall(pickle.dumps(encrypt(minL, pk)))
                if minL != maxL:
                    sts.append((minL, maxL))
    return cur, sts

def secondPassWithCloudServer(conn, pk, sk, cur, sts):
    dads = [ctr for ctr in range(cur + 1)]
    for pair in sts:
        dads[pair[1]] = pair[0]
    for ctr in range(cur + 1):
        while dads[dads[ctr]] != dads[ctr]:
            dads[ctr] = dads[dads[ctr]]
    size = pickle.loads(conn.recv(8192))
    conn.sendall(bytes(1))
    for ctr in range(size):
        pix = decrypt(pickle.loads(conn.recv(8192)), sk)
        conn.sendall(pickle.dumps(encrypt(dads[pix], pk)))  

def thirdPassWithCloudServer(conn, pk, sk, minArea, cur):
    print('third pass start!')
    colors = [random.randint(127, 255) for ctr in range(cur)]
    dic = {}; pool = []
    size = pickle.loads(conn.recv(8192))
    conn.sendall(bytes(1))
    for ctr in range(size):
        pix = decrypt(pickle.loads(conn.recv(8192)), sk)
        conn.sendall(bytes(1))
        pool.append(pix)
        if pix in dic.keys():
            dic[pix] += 1
        else:
            dic[pix] = 1
    for pix in pool:
        if dic[pix] <= minArea or pix == 0:
            conn.sendall(pickle.dumps(encrypt(0, pk)))
        if dic[pix] > minArea and pix > 0:
            conn.sendall(pickle.dumps(encrypt(colors[pix], pk)))
        conn.recv(1)   
    
def TwoPassAlgWithCloudServer(conn, pk, sk, minArea):
    cur, sts = firstPassWithCloudServer(conn, pk, sk)
    secondPassWithCloudServer(conn, pk, sk, cur, sts)
    thirdPassWithCloudServer(conn, pk, sk, minArea, cur)    
    
def SubAbsForPackWithPsp(conn, pk, sk, l, L):
    '''
        l, L通过外部获取,顺便解包了┗|｀O′|┛ 嗷~~
    '''
    thre = pow(10, l - 1)
    inputStr = str(decrypt(pickle.loads(conn.recv(4096)), sk))
    res = []
    res.append(encrypt(thre - int(inputStr[-1 * l + 1: ]) if int(inputStr[-1 * l + 1: ]) > thre // 2 else int(inputStr[-1 * l + 1: ]), pk))
    for ctr in range(1, L):
        cur = int(inputStr[l * -1 * (ctr + 1) + 1: l * -1 * ctr])
        res.append(encrypt(cur if cur < thre // 2 else thre - cur, pk))
    conn.sendall(pickle.dumps(res))    

def SobelForPackWithCloudServer(conn, pk, sk, numOfGate, scale):
    msg = pickle.loads(conn.recv(4096))
    l = msg[0]; L = msg[1]; size = msg[2]
    conn.sendall(bytes(1))
    for ctr in range(size):
        #SubAbsForPackWithPsp(conn, pk, sk, l, L)
        #SubAbsForPackWithPsp(conn, pk, sk, l, L)
        SubAbsForPackWithGCT(conn, pk, sk, l, L, numOfGate, scale, None)
        SubAbsForPackWithGCT(conn, pk, sk, l, L, numOfGate, scale, None)


def SubAbsForPackWithGCT(conn, pk, sk, l, L, numOfGate, scale, preGCT):
    global totalCtr
    sa_x = GCT.unpacked(conn, pk, sk, l, L)
    conn.sendall(bytes(1))
    sa_y = GCT.unpacked(conn, pk, sk, l, L)
    ch = random.randint(0, 100) % 2
    delta = []
    for ctr in range(L):
        delta.append((sa_x[ctr] - sa_y[ctr]) // scale if ch == 0 else (sa_y[ctr] - sa_x[ctr]) // scale)
    conn.sendall(pickle.dumps(ch))
    deltaB = [bina8(item) for item in delta]
    print(deltaB)
    for ctr in range(L):
        start = time()
        if preGCT == None:
            x, y, c, sign, GCTs = GCT.createGCTs(numOfGate, GCT.TVTComp)    
        else:
            print(totalCtr)
            x, y ,c, sign, GCTs = preGCT[totalCtr]
            totalCtr += 1
        for gts in GCTs: 
            conn.sendall(pickle.dumps(gts))
            conn.recv(1)
        conn.sendall(pickle.dumps([sign, y, c[0][0], c[0][numOfGate]])) 
        conn.recv(1)    
        inputXs = GCT.getInputValue(deltaB[ctr], x)
        for itr in range(numOfGate):
            conn.sendall(pickle.dumps(inputXs))
            conn.recv(1)
        
        finalC = pickle.loads(conn.recv(8192))
        conn.sendall(bytes(1))
        h1 = [deltaB[ctr][-1]]
        fx, fy, fc, fsign, fGCT = GCT.createGCTs(1, GCT.TVTMux)
        conn.sendall(pickle.dumps([fGCT, fsign, fy, fc[finalC][0], fc[0][1]]))
        conn.recv(1)
        finputXs = GCT.getInputValue(h1, fx)
        conn.sendall(pickle.dumps(finputXs))
        conn.recv(1)  
        conn.sendall(pickle.dumps(encrypt(delta[ctr], pk)))
        conn.recv(1)

def preCreateGct(num, TVT, numOfGate):
    res = []
    for ctr in range(num):
        x, y, c, sign, GCTs = GCT.createGCTs(numOfGate, TVT)
        res.append([x, y, c, sign, GCTs])
    return res    

def secMulWithCloudServer(conn, pk, sk):
    package = pickle.loads(conn.recv(8192))
    conn.sendall(pickle.dumps(encrypt(decrypt(package[0], sk) * decrypt(package[1], sk), pk)))

def secDivWithCloudServer(conn, pk, sk):
    c6, S = pickle.loads(conn.recv(8192))
    c4 = encrypt(S // decrypt(c6, sk), pk)
    conn.sendall(pickle.dumps(c4))
    secMulWithCloudServer(conn, pk, sk)

def DKGCompWithCloudServer(conn, keypair, constValues, d_hat, d_hat_e):
    pk = keypair[0]; sk = keypair[1]; pk0 = keypair[2]; sk0 = keypair[3]
    one_e0 = constValues[0]; zero_e0 = constValues[1]; one_e = constValues[2]; zero_e = constValues[3]
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
        
    flag = True    
    for item in c_e:
        if int(sk.decrypt(item)) == 0:
            flag = False
    conn.sendall(pickle.dumps(one_e if flag else zero_e))   
    
    conn.recv(1)
    
def hybridSystem():
    sok, conn, address = initWebEnvS(port = 10010)
    print('!')
    pk, sk = initKeys(keySize = 2048) 
    white = encrypt(255, pk)
    black = encrypt(0, pk)   
    _TestSendPkAndSkToCloudServer(conn, pk, sk)
    #sendPkToCloudServer(pk)s
    
    print('waiting for cloud server...')
    GaussianWithCloudServer(conn, pk, sk)
    SobelWithCloudServer(conn, pk, sk)
    BinWithCloudServer(black, white, conn, pk, sk)
    TwoPassAlgWithCloudServer(conn, pk, sk, 100)
    conn.close()

def hybridSystemWithDataPacking():
    pk, sk = initKeys(keySize = 1024)   
    sok, conn, address = initWebEnvS(port = 12345)
    numOfGate = 8
    white = encrypt(255, pk); black = encrypt(0, pk)   
    _TestSendPkAndSkToCloudServer(conn, pk, sk)
    print('waiting for cloud server...')
    SobelForPackWithCloudServer(conn, pk, sk, numOfGate, GAUSSIAN_LITTLE_Q)
    print('1')
    BinWithCloudServer(black, white, conn, pk, sk)
    print('2')
    TwoPassAlgWithCloudServer(conn, pk, sk, 100)
    print('3')
    
    conn.close()
    
def test():
    pk, sk = initKeys(keySize = 1024)   
    sok, conn, address = initWebEnvS(port = 7356)
    _TestSendPkAndSkToCloudServer(conn, pk, sk)
    secDivWithCloudServer(conn, pk, sk)
    
if __name__ == '__main__':
    #hybridSystem()
    #hybridSystemWithDataPacking()
    test()
