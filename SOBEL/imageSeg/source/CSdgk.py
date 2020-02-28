from plr import *
from mySocket import *
#from damgard_jurik import keygen
import GaussianFilter, ReadAndWriteImage, struct, math, random, time, pickle, socket, GCT, AES, copy

#小的卷积核
GAUSSIAN_LITTLE = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
#大的卷积核
GAUSSIAN_LARGE = [[1, 4, 7, 4, 1], [4, 16, 26, 16, 4], [7, 26, 41, 26, 7], [4, 16, 26, 16, 4], [1, 4, 7, 4, 1]]
#大的和小的量化系数，即卷积核元素之和
GAUSSIAN_LITTLE_Q = 16
GAUSSIAN_LARGE_Q = 273
#卷积核内的最大值
GAUSSIAN_LITTLE_L = 16 * 255
GAUSSIAN_LARGE_L = 273 * 255
bits = 20

filePath = 'I:/codes/imageSeg/source'    
#filePath = '.'
#filePath = 'C:/Users/D3lyn/Desktop/imageSeg/source'

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

def getPkFromPsp():
    sok = initWebEnvC()
    print('ask for pk...')
    sok.send('ask..'.encode())
    pk_str = sok.recv(2048)
    pk = pickle.loads(pk_str)
    
    print('get pk from psp...')
    print('now socket is closing...')
    sok.close() 
    return pk
    
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

def init(scale, gaussian_l):
    return 1 + scale + math.ceil(math.log10(gaussian_l))  
    
def GaussianImage(filter, filter_q, matrix, zero_Plr):
    '''
        div with filter_q
    '''
    spaceIndex = len(filter) // 2
    #除法次数并非图像尺
    print('Gaussian start...')
    res = [[] for ctr in range(len(matrix))]
    for ctr in range(spaceIndex):
        res[ctr] = matrix[ctr][:]
        res[-1 * (ctr + 1)] = matrix[-1 * (ctr + 1)][:]
    for i in range(spaceIndex, len(matrix) - spaceIndex):
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][ctr])
        for j in range(spaceIndex, len(matrix[0]) - spaceIndex):
            tempRes = copy.deepcopy(zero_Plr)
            for k in range(-1 * spaceIndex, spaceIndex + 1):
                for l in range(-1 * spaceIndex, spaceIndex + 1):
                    temp = mulClear(matrix[i + k][j + l], filter[spaceIndex + k][spaceIndex + l])
                    tempRes = addCipher(tempRes, temp)
            res[i].append(tempRes)
            del tempRes
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][-1 * (ctr + 1)])        
    return res 
    
def SobelIt(matrix, pk0, pk1, sok):
    print('Sobel start...')
    res = [[] for i in range(len(matrix))]
    res[0] = matrix[0][:]
    res[-1] = matrix[-1][:]
    times = (len(matrix) - 2) * (len(matrix[0]) - 2)
    sok.send(pickle.dumps(times))
    print('need to do', str(times), 'comparison with psp...')
    sok.recv(1)
    for i in range(1, len(matrix) - 1):
        res[i].append(matrix[i][0])
        for j in range(1, len(matrix[0]) - 1):
            A_x_1 = addListCipher([matrix[i - 1][j + 1], mulClear(matrix[i][j + 1], 2), matrix[i + 1][j + 1]])
            A_x_2 = addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i][j - 1], 2), matrix[i + 1][j - 1]])
            A_y_1 = addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i - 1][j], 2), matrix[i - 1][j + 1]])
            A_y_2 = addListCipher([matrix[i + 1][j - 1], mulClear(matrix[i + 1][j], 2), matrix[i + 1][j + 1]])
            tempA_x = subCipher(A_x_1, A_x_2); tempA_y = subCipher(A_y_1, A_y_2)
            res_x = secCmpWithPsp(tempA_x, 0, sok, pk0, pk1, 0)
            res_y = secCmpWithPsp(tempA_y, 0, sok, pk0, pk1, 0)
            A_x = secMulWithPsp(sok, tempA_x, res_x, pk0)
            A_y = secMulWithPsp(sok, tempA_y, res_y, pk0)
            res[i].append(addCipher(A_x, A_y))
        res[i].append(matrix[i][-1])         
    return res 

def secCmpWithPsp1(x, y, sok, pk0, pk1, flags):
    sok.send(pickle.dumps(x))
    sok.recv(1)
    sok.send(pickle.dumps(y))
    lamda_e = pickle.loads(sok.recv(8192))
    return lamda_e
  
def secCmpWithPsp(x, y, sok, pk0, pk1, flags):
    alpha = random.randint(0, 1024)
    alpha_p = encrypt(alpha, pk0)
    x_p = addCipher(x, alpha_p)
    y_p = y + alpha; one_e1 = pk1.encrypt(1); zero_e1 = pk1.encrypt(0)
    sok.send(pickle.dumps(x_p))
    x_b = []; y_b_p = bin(y_p, bits); y_b = []
    for ctr in range(bits):
        x_b.append(pickle.loads(sok.recv(4096)))
        y_b.append(pk1.encrypt(y_b_p[ctr]))
        sok.send(bytes(1))
    #w = d XOR r
    w_e = []
    for ctr in range(bits):
        if y_b_p[ctr] == 0:
            w_e.append(x_b[ctr])
        else:
            w_e.append(one_e1 - x_b[ctr])
    sum_w_e = [None for ctr in range(bits)]
    sum_w_e[bits - 1] = zero_e1
    for ctr in range(bits - 2, -1, -1):
        sum_w_e[ctr] = sum_w_e[ctr + 1] + w_e[ctr + 1]
    
    #s in {-1, 1}    
    s = 1 if random.randint(0, 100) % 2 else -1
    s_e = encrypt(s, pk1)
    
    #c = d - r + s + 3*sum_w
    c_e = []
    for ctr in range(bits):
        r = random.randint(0, 1024)
        c_e.append(r * (x_b[ctr] - y_b[ctr] + s_e + (3 * sum_w_e[ctr])))  

    for item in c_e:
        sok.send(pickle.dumps(item))
        sok.recv(1)    
            
    lamda_e = pickle.loads(sok.recv(8192))
    sok.send(bytes(1))
    
    if flags == 0:
        res = encrypt(0, pk0) - lamda_e if s == -1 else lamda_e  
    elif flags == 1:
        res = encrypt(255, pk0) - lamda_e if s == -1 else lamda_e   
    elif flags == 2:
        res = [lamda_e[1], lamda_e[0]] if s == -1 else lamda_e
    return res    

def secDivWithPsp(sok, a, b, pk, sk):
    r1 = random.randint(1, 100000000)
    r2 = random.randint(1, 100000000)
    r1_p = encrypt(r1, pk); r2_p = encrypt(r2, pk)
    b_h = mulClear(b, r1); s = r1 * r2
    sok.send(pickle.dumps((b_h, s)))
    c = pickle.loads(sok.recv(4096))
    return encrypt(round(decrypt(secMulWithPsp(sok, a, c, pk) / r2, sk)), pk)

def secMulWithPsp(sok, a, b, pk):
    r1 = random.randint(1, 1000)
    r2 = random.randint(1, 1000)
    r1_p = encrypt(r1, pk); r2_p = encrypt(r2, pk)
    a_p = a - r1_p; b_p = b - r2_p
    sok.send(pickle.dumps((a_p, b_p)))
    ab_p = pickle.loads(sok.recv(4096))
    return ab_p + mulClear(a, r2) + mulClear(b, r1) - encrypt(r1 * r2, pk)

def getThreshold(sok, pk0, pk1, sk0, delta, matrix):
    sok.send(pickle.dumps(len(matrix) * len(matrix[0])))
    sok.recv(1)
    tii = encrypt(GAUSSIAN_LITTLE_Q * 127, pk0); maxTime = 2
    while maxTime > 0:
        ti = tii
        Sb = encrypt(0, pk0); Sf = encrypt(0, pk0); Nb = encrypt(0, pk0); Nf = encrypt(0, pk0)
        for ctr in range(len(matrix)):
            for itr in range(len(matrix[0])):
                tube = secCmpWithPsp(subCipher(matrix[ctr][itr], ti), 0, sok, pk0, pk1, 2)
                Sb = addCipher(Sb, secMulWithPsp(sok, tube[0], matrix[ctr][itr], pk0))
                Sf = addCipher(Sf, secMulWithPsp(sok, tube[1], matrix[ctr][itr], pk0))
                Nb = addCipher(Nb, tube[0])
                Nf = addCipher(Nf, tube[1])
        print(decrypt(Sb, sk0), decrypt(Sf, sk0), decrypt(Nb, sk0), decrypt(Nf, sk0))        
        tii = addCipher(secDivWithPsp(sok, Sb, mulClear(Nb, 2), pk0, sk0), secDivWithPsp(sok, Sf, mulClear(Nf, 2), pk0, sk0))
        print(decrypt(tii, sk0))
        temp = secCmpWithPsp(subCipher(tii, ti), 0, sok, pk0, pk1, 0)
        temp = secMulWithPsp(sok, temp, subCipher(tii, ti), pk0)
        r = random.randint(1, 1000)
        sok.send(pickle.dumps((addCipher(temp, encrypt(r, pk0)), delta + r)))
        res = pickle.loads(sok.recv(2048))
        maxTime -= 1
        if res == 'yes!':
            print('meets delta!')
            break
        if maxTime == 0:
            print('meet maxTime!')
        
    return tii
                
def BinIt(matrix, thres, pk0, pk1, sok):
    print('Bina start...')
    sok.send(pickle.dumps(len(matrix) * len(matrix[0])))
    sok.recv(1)
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[0])):
            matrix[ctr][itr] = secCmpWithPsp(subCipher(matrix[ctr][itr], thres), 0, sok, pk0, pk1, 1)
    return matrix 
    
def hybridSystem(): 
    #construct sok
    sok = initWebEnvC(port = 10010)
    #get Paillier keys
    pk0, sk0 = _testGetPkAndSkFromPsp(sok)
    #get DGK keys
    pk1, sk1 = _testGetPkAndSkFromPsp(sok)
    #read image and encrypt it
    image = ReadAndWriteImage.color2matrixWithPlr(filePath + '/pic/coinsSmall.jpg', pk0)
    #get some const
    zero_Plr = encrypt(0, pk0)
    #Gaussian it, no division
    GRes = GaussianImage(GaussianFilter.GAUSSIAN_LITTLE, GaussianFilter.GAUSSIAN_LITTLE_Q, image, zero_Plr)
    #Sobel it
    SRes = SobelIt(matrix, pk0, pk1, sok)
    #get threshold
    thres = getThreshold(sok, pk0, pk1, sk0, 10, SRes)
    #Bina it
    BRes = BinIt(SRes, thres, pk0, pk1, sok)
    #Write it
    ReadAndWriteImage.matrix2imgWithPlr(TRes, filePath + '/pic/testOutPut0817.bmp', sk0) 
    #close it
    sok.close()     

if __name__ == '__main__':
    hybridSystem()
