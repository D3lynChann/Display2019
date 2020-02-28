import pickle, socket
from plr import *
from mySocket import *
import random

def initKeys(keySize = 1024):
    pk, sk = plrInit(keySize)
    print('init keys finish...')
    return pk, sk
    
def sendPkAndSkToUser(pk, sk):
    sok, conn, address = initWebEnvS()
    pk_str = pickle.dumps(pk)
    sk_str = pickle.dumps(sk)
    print('sending pk to user...')
    ask = conn.recv(2048)
    conn.sendall(pk_str)
    print('sending sk to user...')
    ask = conn.recv(2048)
    conn.sendall(sk_str)
    conn.close()    
    print('sending finish, socket close...')
        
def sendPkToCloudServer(pk):
    sok, conn, address = initWebEnvS()
    pk_str = pickle.dumps(pk)
    print('sending pk to cloud server...')
    ask = conn.recv(2048)
    conn.sendall(pk_str)
    conn.close()    
    print('sending finish, socket close...')

def _TestSendPkAndSkToCloudServer(pk, sk):
    sok, conn, address = initWebEnvS()
    pk_str = pickle.dumps(pk)
    sk_str = pickle.dumps(sk)
    print('sending pk to cs...')
    ask = conn.recv(2048)
    conn.sendall(pk_str)
    print('sending pk to cs...')
    ask = conn.recv(2048)
    conn.sendall(sk_str)
    conn.close()    
    print('sending finish, socket close...')    

def divPtcWithCloudServer(conn, pk, sk):
    inputA = decrypt(pickle.loads(conn.recv(2048)), sk)
    conn.sendall(bytes(1))
    inputB = pickle.loads(conn.recv(2048))
    conn.sendall(pickle.dumps(encrypt(inputA // inputB, pk)))  

def GaussianWithCloudServer(conn, pk, sk):
    print('Gaussian start...')
    times = pickle.loads(conn.recv(2048))
    print('need to do', str(times), 'division with cloud server...')
    for ctr in range(times):
        divPtcWithCloudServer(conn, pk, sk)
    print('Gaussian finish...') 

def compPtcWithCloudServer(conn, pk, sk):
    flag = pickle.loads(conn.recv(2048))
    conn.sendall(bytes(1))
    inputA = decrypt(pickle.loads(conn.recv(2048)), sk)
    conn.sendall(bytes(1))
    inputB = decrypt(pickle.loads(conn.recv(2048)), sk)
    if flag == 1:
        conn.sendall(pickle.dumps(encrypt(inputA if inputA >= inputB else inputB, pk)))
    elif flag == 0:
        conn.sendall(pickle.dumps(encrypt(inputA if inputB >= inputA else inputB, pk)))
        
def SubBinaWithCloudServer(black, white, T, conn, pk, sk):
    input = decrypt(pickle.loads(conn.recv(2048)), sk)
    conn.sendall(bytes(1))
    if input >= T:
        conn.sendall(pickle.dumps(white))
    else:
        conn.sendall(pickle.dumps(black))

def BinWithCloudServer(black, white, conn, pk, sk):
    print('Bina start...')
    times = pickle.loads(conn.recv(2048))
    print('need to do', str(times), 'comparison with cloud server...')
    conn.sendall(bytes(1))
    T = decrypt(pickle.loads(conn.recv(2048)), sk)
    conn.sendall(bytes(1))
    for ctr in range(times):
        SubBinaWithCloudServer(black, white, T, conn, pk, sk)
    print('Bina finish...')
        
def SobelWithCloudServer(conn, pk, sk):
    print('Sobel start...')
    times = pickle.loads(conn.recv(2048))
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
    size = pickle.loads(conn.recv(2048))
    numsOfConnectedArea = [1 for ctr in range(size)]
    for ctr in range(size):
        msg = pickle.loads(conn.recv(4096))
        leftP = decrypt(msg[0], sk); upP = decrypt(msg[1], sk); nowP = decrypt(msg[2], sk)
        conn.sendall(bytes(1))
        lbl = pickle.loads(conn.recv(4096))
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
    size = pickle.loads(conn.recv(2048))
    conn.sendall(bytes(1))
    for ctr in range(size):
        pix = decrypt(pickle.loads(conn.recv(2048)), sk)
        conn.sendall(pickle.dumps(encrypt(dads[pix], pk)))  

def thirdPassWithCloudServer(conn, pk, sk, minArea, cur):
    print('third pass start!')
    colors = [random.randint(127, 255) for ctr in range(cur)]
    dic = {}; pool = []
    size = pickle.loads(conn.recv(2048))
    conn.sendall(bytes(1))
    for ctr in range(size):
        pix = decrypt(pickle.loads(conn.recv(4096)), sk)
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

def SobelForPackWithCloudServer(conn, pk, sk):
    msg = pickle.loads(conn.recv(4096))
    l = msg[0]; L = msg[1]; size = msg[2]
    conn.sendall(bytes(1))
    for ctr in range(size):
        SubAbsForPackWithPsp(conn, pk, sk, l, L)
        SubAbsForPackWithPsp(conn, pk, sk, l, L)
    
def hybridSystem():
    pk, sk = initKeys(keySize = 64) 
    white = encrypt(255, pk)
    black = encrypt(0, pk)   
    _TestSendPkAndSkToCloudServer(pk, sk)
    #sendPkToCloudServer(pk)
    sendPkAndSkToUser(pk, sk)
    
    sok, conn, address = initWebEnvS(port = 10010)
    print('waiting for cloud server...')
    GaussianWithCloudServer(conn, pk, sk)
    SobelWithCloudServer(conn, pk, sk)
    BinWithCloudServer(black, white, conn, pk, sk)
    TwoPassAlgWithCloudServer(conn, pk, sk, 100)
    conn.close()

def hybridSystemWithDataPacking():
    pk, sk = initKeys(keySize = 256)   
    white = encrypt(255, pk); black = encrypt(0, pk)   
    _TestSendPkAndSkToCloudServer(pk, sk)
    sendPkAndSkToUser(pk, sk)
    sok, conn, address = initWebEnvS(port = 10010)
    print('waiting for cloud server...')
    SobelForPackWithCloudServer(conn, pk, sk)
    '''
    print('1')
    BinWithCloudServer(black, white, conn, pk, sk)
    print('2')
    TwoPassAlgWithCloudServer(conn, pk, sk, 100)
    print('3')
    '''
    conn.close()
    
def test():
    pk, sk = initKeys(keySize = 32)
    _TestSendPkAndSkToCloudServer(pk, sk)
    sok, conn, address = initWebEnvS(port = 10010) 
    twoPassAlgWithCloudServer(conn, pk, sk, 3)
    conn.close()
    
if __name__ == '__main__':
    hybridSystem()
    #hybridSystemWithDataPacking()
    #test()