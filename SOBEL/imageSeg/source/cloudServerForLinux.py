from plr import *
from mySocket import *
import GaussianFilter, ReadAndWriteImage, struct, math, random, time, pickle, socket, GCT, AES

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
   
def init(scale, gaussian_l):
    return 1 + scale + math.ceil(math.log10(gaussian_l))   
   
def getSimpleThres():
    '''
    获得经验阈值
    '''
    Gmax = 255; Gmin = 0
    return Gmax - (Gmax - Gmin) // 3
   
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

def DivideImg(matrix, sm, sn, ll, pk):
    #将图片打包为sm*sn的packed data
    m = len(matrix); n = len(matrix[0])
    assert divmod(m, sm)[1] == 0
    assert divmod(n, sn)[1] == 0
    tempRes = [[] for ctr in range(sm)]
    res = [[] for ctr in range(sm)]
    for i in range(sm):
        for j in range(sn):
            temp = []
            for k in range(m // sm):
                for l in range(n // sn):
                    temp.append(matrix[i + k * sm][j + l * sn])
            tempRes[i].append(temp)
    for i in range(sm):
        for j in range(sn):
            res[i].append(packWithPlr(tempRes[i][j], ll, pk))
    return res, m, n    

def packWithPlr(inputList, l, pk):
    L = len(inputList)
    res = encrypt(0, pk)
    for ctr in range(L):
        res = addCipher(res, mulClear(inputList[ctr], pow(10, ctr * l)))
    return res       

def GaussianImagePack(filter, filter_q, matrix, pk):
    '''
    DP的加密数据的高斯滤波
    输入输出均为DP加密矩阵
    此时没有进行除法运算
    '''
    assert type(matrix).__name__ == 'list'
    res = [[] for ctr in range(len(matrix))]
    spaceIndex = len(filter) // 2
    for ctr in range(spaceIndex):
        res[ctr] = mulListClear(matrix[ctr][:], filter_q)
        res[-1 * (ctr + 1)] = mulListClear(matrix[-1 * (ctr + 1)][:], filter_q)
    for i in range(spaceIndex, len(matrix) - spaceIndex):
        for ctr in range(spaceIndex):
            res[i].append(mulClear(matrix[i][ctr], filter_q))
        for j in range(spaceIndex, len(matrix[0]) - spaceIndex):
            tempRes = encrypt(0, pk)
            for k in range(-1 * spaceIndex, spaceIndex + 1):
                for l in range(-1 * spaceIndex, spaceIndex + 1):
                    temp = mulClear(matrix[i + k][j + l], filter[spaceIndex + k][spaceIndex + l])
                    tempRes = addCipher(tempRes, temp)
            res[i].append(tempRes)
            del tempRes
        for ctr in range(spaceIndex):
            res[i].append(mulClear(matrix[i][-1 * (ctr + 1)], filter_q))    
    return res

def SubAbsForPackWithPsp(sok, pd1, pd2, pk, l, L):
    temp = encrypt(0, pk)
    for ctr in range(L):
        temp = addCipher(temp, encrypt(pow(10, (ctr + 1) * l - 1), pk))
    res0 = subCipher(addCipher(pd1, temp), pd2)
    sok.send(pickle.dumps(res0))
    res = pickle.loads(sok.recv(8192))   
    return res    
    
def SobelForPackWithPsp(sok, matrix, pk, l, L, numOfGate, scale):
    assert type(matrix).__name__ == 'list'
    sok.send(pickle.dumps((l, L, (len(matrix) - 2) * (len(matrix[0]) - 2))))
    sok.recv(1)
    Res = [[0 for itr in range(len(matrix[0]))] for ctr in range(len(matrix))]
    for i in range(1, len(matrix) - 1):
        for j in range(1, len(matrix[0]) - 1):
            s_x_0 = addListCipher([matrix[i - 1][j + 1], mulClear(matrix[i][j + 1], 2), matrix[i + 1][j + 1]])
            s_y_0 = addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i][j - 1], 2), matrix[i + 1][j - 1]])
            s_x_1 = addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i - 1][j], 2), matrix[i - 1][j + 1]])
            s_y_1 = addListCipher([matrix[i + 1][j - 1], mulClear(matrix[i + 1][j], 2), matrix[i + 1][j + 1]])
            #A_x = SubAbsForPackWithPsp(sok, s_x_0, s_y_0, pk, l, L)
            #A_y = SubAbsForPackWithPsp(sok, s_x_1, s_y_1, pk, l, L)
            A_x = SubAbsForPackWithGCT(sok, s_x_0, s_y_0, pk, numOfGate, l, L, scale)
            A_y = SubAbsForPackWithGCT(sok, s_x_1, s_y_1, pk, numOfGate, l, L, scale)
            temp = []
            for ctr in range(len(A_x)):
                temp.append(addCipher(A_x[ctr], A_y[ctr]))
            Res[i][j] = temp
    return Res        

def carryUpImgWithPlr(matrix, m, n, sm, sn, pk):
    '''
        input: matrix is encypted data
    '''
    res = [[0 for itr in range(n)] for ctr in range(m)]
    tempH = m // sm; tempW = n // sn  
    
    for i in range(1, sm - 1):
        for j in range(1, sn - 1): 
            for k in range(1, tempH - 1):
                for l in range(1, tempW - 1):
                    temp = matrix[i][j][k * tempW + l]
                    res[i + k * sm][j + l * sn] = temp  
    zzeroo = encrypt(0, pk)
    for ctr in range(len(res)):
        for itr in range(len(res[0])):
            if type(res[ctr][itr]).__name__ == 'int':
                res[ctr][itr] = zzeroo
    return res    
    
def GaussianImage(filter, filter_q, matrix, pk, sok):
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
            tempRes = encrypt(0, pk)
            for k in range(-1 * spaceIndex, spaceIndex + 1):
                for l in range(-1 * spaceIndex, spaceIndex + 1):
                    temp = mulClear(matrix[i + k][j + l], filter[spaceIndex + k][spaceIndex + l])
                    tempRes = addCipher(tempRes, temp)
            res[i].append(tempRes)
            del tempRes
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][-1 * (ctr + 1)]) 
    actH = len(matrix) - 2 * spaceIndex
    actW = len(matrix[0]) - 2 * spaceIndex
    sok.send(pickle.dumps(actH * actW))
    print('need to do', str(actH * actW), 'division with psp...')
    for i in range(1, actH + spaceIndex):
        for j in range(1, actW + spaceIndex):
            res[i][j] = divPtcWithPsp(sok, res[i][j], filter_q)          
    return res        

def SobelIt(matrix, pk, sok):
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
            A_x = subCipher(compPtcWithPsp(sok, A_x_1, A_x_2, pk, 1), compPtcWithPsp(sok, A_x_1, A_x_2, pk, 0))
            A_y = subCipher(compPtcWithPsp(sok, A_y_1, A_y_2, pk, 1), compPtcWithPsp(sok, A_y_1, A_y_2, pk, 0))
            
            res[i].append(addCipher(A_x, A_y))
        res[i].append(matrix[i][-1])         
    return res 

def BinIt(matrix, thres, pk, sok, multiple):
    thres *= multiple
    print('Bina start...')
    times = len(matrix) * len(matrix[0])
    sok.send(pickle.dumps(times))
    print('need to do', str(times), 'comparison with psp...')
    sok.recv(1)
    T = encrypt(thres, pk)
    sok.send(pickle.dumps(T))
    sok.recv(1)
    res = [[] for i in range(len(matrix))]
    print('go!')
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[0])):
            res[ctr].append(subBinaWithPsp(sok, matrix[ctr][itr], pk))
    return res            
    
def divPtcWithPsp(sok, inputA, inputB):
    sok.send(pickle.dumps(inputA))
    sok.recv(1)
    sok.send(pickle.dumps(inputB))
    res = pickle.loads(sok.recv(8192))
    return res

def compPtcWithPsp(sok, inputA, inputB, pk, flag):
    '''
       1 for returning the bigger one, 0 for returning the smaller one, r is mask
    '''
    sok.send(pickle.dumps(flag))
    sok.recv(1)
    r = encrypt(random.randint(1, 99), pk)
    sok.send(pickle.dumps(addCipher(inputA, r)))
    sok.recv(1)
    sok.send(pickle.dumps(addCipher(inputB, r)))
    res = subCipher(pickle.loads(sok.recv(8192)), r)
    return res   

def subBinaWithPsp(sok, input, pk):
    '''
       1 for returning the bigger one, 0 for returning the smaller one, r is mask
       1 for >, 0 for =, -1 for <
    '''
    sok.send(pickle.dumps(input))
    res = pickle.loads(sok.recv(8192))
    return res  
    
def firstPassWithPsp(sok, matrix, pk):
    h = len(matrix); w = len(matrix[0]) 
    labels = [[encrypt(0, pk) for ctr in range(w)] for itr in range(h)] 
    sok.send(pickle.dumps((h - 1) * (w - 1))) 
    for ctr in range(1, h):
        for itr in range(1, w):
            msg = [matrix[ctr][itr - 1], matrix[ctr - 1][itr], matrix[ctr][itr]]
            sok.send(pickle.dumps(msg))  
            sok.recv(1)
            lbl = [labels[ctr][itr - 1], labels[ctr - 1][itr]]    
            sok.send(pickle.dumps(lbl))
            labels[ctr][itr] = pickle.loads(sok.recv(8192))
    return labels      

def secondPassWithPsp(sok, labels):
    h = len(labels); w = len(labels[0])
    sok.send(pickle.dumps(h * w))
    sok.recv(1)    
    for ctr in range(h):
        for itr in range(w):
            sok.send(pickle.dumps(labels[ctr][itr]))
            labels[ctr][itr] = pickle.loads(sok.recv(8192))
    return labels

def thirdPassWithPsp(sok, labels):
    print('third pass start!')
    h = len(labels); w = len(labels[0])
    sok.send(pickle.dumps(h * w))
    sok.recv(1)
    for ctr in range(h):
        for itr in range(w):
            sok.send(pickle.dumps(labels[ctr][itr]))
            sok.recv(1)
    res = [[0 for ctr in range(w)] for itr in range(h)]
    for ctr in range(h):
        for itr in range(w):
            res[ctr][itr] = pickle.loads(sok.recv(8192))
            sok.send(bytes(1))
    return res        

def TwoPassAlgWithPsp(sok, matrix, pk):
    res1 = firstPassWithPsp(sok, matrix, pk)
    res2 = secondPassWithPsp(sok, res1)
    res3 = thirdPassWithPsp(sok, res2)
    return res3

def SubAbsForPackWithGCT(sok, s_x, s_y, pk, numOfGate, l, L, scale):
    a_x = random.randint(1, 100) * scale
    a_xc = encrypt(a_x, pk)
    a_y = random.randint(1, 100) * scale
    a_yc = encrypt(a_y, pk)
    
    sa_x = addCipher(s_x, packWithPlr([a_xc for ctr in range(L)], l, pk))
    sa_y = addCipher(s_y, packWithPlr([a_yc for ctr in range(L)], l, pk))
    sok.send(pickle.dumps(sa_x))
    sok.recv(1)
    sok.send(pickle.dumps(sa_y))
    ch = pickle.loads(sok.recv(8192))
    beta = (a_x - a_y) // scale if ch == 0 else (a_y - a_x) // scale
    b_b = bina8(beta)
    beta = encrypt(beta, pk)
    finalRes = []
    for ctr in range(L):
        GCTs = []
        for itr in range(8 * numOfGate):
            GCTs.append(pickle.loads(sok.recv(8192)))
            sok.send(bytes(1))

        package = pickle.loads(sok.recv(32768))
        sok.send(bytes(1))
        sign = package[0]
        y = package[1]
        subC = package[2]
        c0 = package[3]
        inputValueY = GCT.getInputValue(b_b, y)
        res = []
        for itr in range(numOfGate):
            inputValueX = pickle.loads(sok.recv(8192))
            sok.send(bytes(1))
            for line in GCTs:
                res = AES.D(AES.generateAES(bytes(subC)), AES.D(AES.generateAES(inputValueY[itr]), AES.D(AES.generateAES(inputValueX[itr]), line)))
                if res[: 8] == sign:
                    subC = bytes(res)
                    break            
        finalC = (0 if subC == c0 else 1)
        sok.send(pickle.dumps(finalC))
        sok.recv(1)
        h2 = [b_b[-1]]
        fPackage = pickle.loads(sok.recv(32768))
        sok.send(bytes(1))
        fGCT = fPackage[0]
        fsign = fPackage[1]
        fy = fPackage[2]
        fsubC = fPackage[3]
        fc0 = fPackage[4]
        finputValueY = GCT.getInputValue(h2, fy)
        fres = []
        finputValueX = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        for line in fGCT:
            fres = AES.D(AES.generateAES(bytes(fsubC)), AES.D(AES.generateAES(finputValueY[0]), AES.D(AES.generateAES(finputValueX[0]), line)))
            if fres[: 8] == fsign:
                fsubC = bytes(fres)
                break    
        ffinalC = (0 if fsubC == fc0 else 1) 
        delta = pickle.loads(sok.recv(8192))
        sok.send(bytes(1))
        finalRes.append(subCipher(delta, beta) if ffinalC == 1 else subCipher(beta, delta))
    return finalRes
    
def secMulWithPsp(sok, a, b):
    sok.send(pickle.dumps((a, b)))
    return pickle.loads(sok.recv(8192))
    
def secDivWithPsp(sok, m1, m2):
    r = random.randint(0, 100); Q = random.randint(0, 100); S = r * Q
    c6 = mulClear(m2, r)
    sok.send(pickle.dumps([c6, S]))
    c4 = pickle.loads(sok.recv(8192))
    c3 = secMulWithPsp(sok, m1, c4)
    return c3, Q

def GenerateCS(pk, d_hat_e, r_hat, r_hat_e, constValue):
    #if s == 1: no 0 in c if d > r
    w_e = []; l = len(d_hat_e); zero_e = constValue[0]; one_e = constValue[1]
    
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
    
def DKGCompWithPsp(sok, keyRing, constValues, r_hat, r_hat_e):
    lenOfD_Hat_e = pickle.loads(sok.recv(8192))
    sok.send(bytes(1))
    d_hat_e = []
    for ctr in range(lenOfD_Hat_e):
        d_hat_e.append(pickle.loads(sok.recv(8092)))
        sok.sendall(bytes(1))
    c_e, s = GenerateCS(pk, d_hat_e, r_hat, r_hat_e, constValues)
    sok.send(pickle.dumps(len(c_e)))
    sok.recv(1)
    for item in c_e:
        sok.send(pickle.dumps(item))
        sok.recv(1)
    lamda_e = pickle.loads(sok.recv(8192))
    sok.send(bytes(1))
    res = constValues[1] - lamda_e if s == -1 else lamda_e
    return res
    
def hybridSystem(): 
    #pk = getPkFromPsp()
    sok = initWebEnvC(port = 10010)
    pk, sk = _testGetPkAndSkFromPsp(sok)
    image = ReadAndWriteImage.color2matrixWithPlr(filePath + '/pic/coins.jpg', pk)
    print('connect finish')
    start = time.time()
    GRes = GaussianImage(GaussianFilter.GAUSSIAN_LITTLE, GaussianFilter.GAUSSIAN_LITTLE_Q, image, pk, sok)
    end = time.time()
    print('Gaussian finish...', 'time:', end - start)
    start = time.time()
    SRes = SobelIt(GRes, pk, sok)
    end = time.time()
    print('Sobel finish...', 'time:', end - start)
    start = time.time()
    BRes = BinIt(SRes, getSimpleThres(), pk, sok, 1)
    end = time.time()
    print('Bina finish...', 'time:', end - start)
    start = time.time()
    TRes = TwoPassAlgWithPsp(sok, BRes, pk)
    end = time.time()
    print('Two -pass finish..', 'time:', end - start)
    start = time.time()
    ReadAndWriteImage.matrix2imgWithPlr(TRes, filePath + '/pic/testOutPut0817.bmp', sk) 
    end = time.time()
    print('writing finish...', 'time:', end - start)
    sok.close()   

def hybridSystemWithDataPacking():
    #sm、sn为打包后的尺寸
    sok = initWebEnvC(port = 12345)
    pk, sk = _testGetPkAndSkFromPsp(sok)
    image = ReadAndWriteImage.color2matrixWithPlr(filePath + '/pic/coinsSmall.jpg', pk)
    dsm = 2; dsn = 2
    sm = len(image) // dsm; sn = len(image[0]) // dsn
    numOfGate = 8
    l = init(3, GAUSSIAN_LITTLE_L)
    print('connect finish...\nnow divide the image...')
    start = time.time()
    DRes, m, n = DivideImg(image, sm, sn, l, pk)
    end = time.time()
    L = m * n // sm // sn    
    print('divide finish... time:', end - start, '\nnow Gauss the packed image...')
    start = time.time()
    GResP = GaussianImagePack(GAUSSIAN_LITTLE, GAUSSIAN_LITTLE_Q, DRes, pk)
    end = time.time()
    print('Gaussian finish... time:', end - start, '\nnow Sobel the packed image...')
    start = time.time()
    SResP = SobelForPackWithPsp(sok, GResP, pk, l, L, numOfGate, GAUSSIAN_LITTLE_Q)
    end = time.time()
    print('Sobel finish... time:', end - start, '\nnow carrying up the image...')
    SRes = carryUpImgWithPlr(SResP, m, n, sm, sn, pk)
    print('carrying finish...\nnow binarize the image...')
    BRes = BinIt(SRes, getSimpleThres(), pk, sok, GAUSSIAN_LITTLE_L)    
    print('binarization finish...\nnow apply two-pass alg on image...')
    TRes = TwoPassAlgWithPsp(sok, BRes, pk)
    print('two-pass alg finish...\nnow writing the image...')
    ReadAndWriteImage.matrix2imgWithPlr(TRes, filePath + '/pic/test0908.bmp', sk) 
    print('')
    
    sok.close()    
    
def test():
    sok = initWebEnvC(port = 7356)  
    pk, sk = _testGetPkAndSkFromPsp(sok) 
    a = encrypt(160, pk); b = encrypt(5, pk)
    start = time.time()
    res, Q = secDivWithPsp(sok, a, b)
    end = time.time()
    print(decrypt(res, sk) / Q)
    print(end - start)
    
if __name__ == '__main__':
    #hybridSystem()
    #hybridSystemWithDataPacking()
    test()
