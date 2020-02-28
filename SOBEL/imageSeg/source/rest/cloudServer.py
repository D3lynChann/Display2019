import pickle, socket
from plr import *
from mySocket import *
import GaussianFilter
import ReadAndWriteImage 
import struct
import math
import random
import time

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

#filePath = 'I:/codes/imageSeg/source'    
#filePath = ''
filePath = 'C:/Users/D3lynChann/Desktop/imageSeg/source'
   
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
    
def _testGetPkAndSkFromPsp():
    sok = initWebEnvC()
    print('ask for pk...')
    sok.send('ask..'.encode())
    pk_str = sok.recv(2048)
    print('ask for sk...')
    sok.send('ask..'.encode())
    sk_str = sok.recv(2048)
    pk = pickle.loads(pk_str)
    sk = pickle.loads(sk_str)
    
    print('get pk and sk from psp...')
    print('now socket is closing...')
    sok.close() 
    return pk, sk     

def getImageFromUser():
    ADDR = (localIp, 10086)
    BUFSIZE = 1024
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
    
    recvSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recvSock.bind(ADDR)
    recvSock.listen(500)
    print("waiting for connect...")
    conn, addr = recvSock.accept()
    print("user is in—> ", addr)
    fhead = conn.recv(FILEINFO_SIZE)
    filename, temp1, filesize, temp2 = struct.unpack('128s32sI8s', fhead)
    filename = 'new_' + filename.decode().strip('\00')
    fp = open(filePath + '/file/testImgPlr.txt', 'wb')
    restsize = filesize
    print ("receiving...")
    while 1:
        if restsize > BUFSIZE:
            filedata = conn.recv(BUFSIZE)
        else:
            filedata = conn.recv(restsize)
        if not filedata: 
            break
        fp.write(filedata)
        restsize = restsize - len(filedata)
        if restsize == 0:
            break
    print("receive finish, now closing the socket...")
    fp.close()
    conn.close()
    recvSock.close()
    print("socket is closed...")
    imgFile = open(filePath + '/file/testImgPlr.txt', 'rb')
    imgSecond = pickle.load(imgFile)
    imgFile.close()
    print('loading finish...')
    return imgSecond 

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
    res = pickle.loads(sok.recv(4096))   
    return res    
    
def SobelForPackWithPsp(sok, matrix, pk, l, L):
    assert type(matrix).__name__ == 'list'
    sok.send(pickle.dumps((l, L, (len(matrix) - 2) * (len(matrix[0]) - 2))))
    sok.recv(1)
    for i in range(1, len(matrix) - 1):
        for j in range(1, len(matrix[0]) - 1):
            A_x = SubAbsForPackWithPsp(sok, addListCipher([matrix[i - 1][j + 1], mulClear(matrix[i][j + 1], 2), matrix[i + 1][j + 1]]), addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i][j - 1], 2), matrix[i + 1][j - 1]]), pk, l, L)
            A_y = SubAbsForPackWithPsp(sok, addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i - 1][j], 2), matrix[i - 1][j + 1]]), addListCipher([matrix[i + 1][j - 1], mulClear(matrix[i + 1][j], 2), matrix[i + 1][j + 1]]), pk, l, L)
            temp = []
            for A_x_i, A_y_i in A_x, A_y:
                temp.append(addCipher(A_x_i, A_y_i))
                
                

def carryUpImgWithPlr(matrix, m, n, sm, sn):
    '''
        input: matrix is encypted data
    '''
    res = [[0 for itr in range(n)] for ctr in range(m)]
    tempH = m // sm; tempW = n // sn    
    for i in range(sm):
        for j in range(sn): 
            for k in range(0, tempH):
                for l in range(0, tempW):
                    temp = matrix[i][j][k * tempW + l]
                    res[i + k * sm][j + l * sn] = temp  
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
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[0])):
            res[ctr].append(subBinaWithPsp(sok, matrix[ctr][itr], pk))
    return res            
    
def divPtcWithPsp(sok, inputA, inputB):
    sok.send(pickle.dumps(inputA))
    sok.recv(1)
    sok.send(pickle.dumps(inputB))
    res = pickle.loads(sok.recv(2048))
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
    res = subCipher(pickle.loads(sok.recv(2048)), r)
    return res   

def subBinaWithPsp(sok, input, pk):
    '''
       1 for returning the bigger one, 0 for returning the smaller one, r is mask
       1 for >, 0 for =, -1 for <
    '''
    sok.send(pickle.dumps(input))
    sok.recv(1)
    res = pickle.loads(sok.recv(4096))
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
            labels[ctr][itr] = pickle.loads(sok.recv(4096))
    return labels      

def secondPassWithPsp(sok, labels):
    h = len(labels); w = len(labels[0])
    sok.send(pickle.dumps(h * w))
    sok.recv(1)    
    for ctr in range(h):
        for itr in range(w):
            sok.send(pickle.dumps(labels[ctr][itr]))
            labels[ctr][itr] = pickle.loads(sok.recv(4096))
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
            res[ctr][itr] = pickle.loads(sok.recv(4096))
            sok.send(bytes(1))
    return res        

def TwoPassAlgWithPsp(sok, matrix, pk):
    res1 = firstPassWithPsp(sok, matrix, pk)
    res2 = secondPassWithPsp(sok, res1)
    res3 = thirdPassWithPsp(sok, res2)
    return res3
    
def hybridSystem(): 
    #pk = getPkFromPsp()
    pk, sk = _testGetPkAndSkFromPsp()
    image = getImageFromUser()
    sok = initWebEnvC(port = 10010) 
    print('connect finish')
    start = time.time()
    GRes = GaussianImage(GaussianFilter.GAUSSIAN_LITTLE, GaussianFilter.GAUSSIAN_LITTLE_Q, image, pk, sok)
    end = time.time()
    tempG = GRes[:] 
    print('Gaussian finish...', 'time:', end - start)
    start = time.time()
    SRes = SobelIt(GRes, pk, sok) 
    end = time.time()
    tempS = SRes[:]
    print('Sobel finish...', 'time:', end - start)
    start = time.time()
    BRes = BinIt(SRes, getSimpleThres(), pk, sok, 1)
    end = time.time()
    tempB = BRes[:]
    print('Bina finish...', 'time:', end - start)
    start = time.time()
    TRes = TwoPassAlgWithPsp(sok, BRes, pk)
    end = time.time()
    print('Two -pass finish..', 'time:', end - start)
    start = time.time()
    ReadAndWriteImage.matrix2imgWithPlr(TRes, filePath + '/pic/testOutPutT.bmp', sk) 
    end = time.time()
    print('writing finish...', 'time:', end - start)
    sok.close()      
    ReadAndWriteImage.matrix2imgWithPlr(tempG, filePath + '/pic/testOutPutG.bmp', sk)
    ReadAndWriteImage.matrix2imgWithPlr(tempB, filePath + '/pic/testOutPutB.bmp', sk)
    ReadAndWriteImage.matrix2imgWithPlr(tempS, filePath + '/pic/testOutPutS.bmp', sk) 

def hybridSystemWithDataPacking():
    #sm、sn为打包后的尺寸
    sm = 128; sn = 64
    l = init(3, GAUSSIAN_LITTLE_L)
    pk, sk = _testGetPkAndSkFromPsp()
    image = getImageFromUser()
    sok = initWebEnvC(port = 10010)
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
    SobelForPackWithPsp(sok, GResP, pk, l, L)
    end = time.time()
    print('Sobel finish... time:', end - start, '\nnow carrying up the image...')
    
    SRes = carryUpImgSpecialWithPlr(SResP, l, m, n, sm, sn)
    print('carrying finish...\nnow binarize the image...')
    BRes = BinIt(SRes, getSimpleThres(), pk, sok, GAUSSIAN_LITTLE_L)    
    print('binarization finish...\nnow apply two-pass alg on image...')
    TRes = TwoPassAlgWithPsp(sok, BRes, pk)
    print('two-pass alg finish...\nnow writing the image...')
    ReadAndWriteImage.matrix2imgWithPlr(TRes, 'pic/test07041648.bmp', sk) 
    print('')
    
    sok.close()    
    
def test():
    pk, sk = _testGetPkAndSkFromPsp()
    sok = initWebEnvC(port = 10010) 
    testMatrix = [[0, 0, 0, 0, 0], [0, 1, 1, 0, 0], [0, 1, 0, 1, 0], [0, 0, 1, 0, 1], [0, 1, 1, 0, 1]]
    testMatrixPlr = [[encrypt(testMatrix[ctr][itr], pk) for itr in range(len(testMatrix[0]))] for ctr in range(len(testMatrix))]
    
    for line in testMatrixPlr:
        for pix in line:
            print(decrypt(pix, sk), end = '\t')
        print() 
    
    print('______________')
    
    res = twoPassAlgWithPsp(sok, testMatrixPlr, pk)
    
    for line in res:
        for pix in line:
            print(decrypt(pix, sk), end = '\t')
        print() 
    sok.close()        
    
if __name__ == '__main__':
    hybridSystem()
    #hybridSystemWithDataPacking()
    #test()