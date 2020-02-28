from plr import *
import ReadAndWriteImage, time, GaussianFilter, Sobel, Binary, DataPacking, Paral, TwoPassAlg

def test():
    l = DataPacking.init(3, 6825)
    pk, sk = plrInit(512)
    li = [[1,2,3,4,5,6,7,8,9,10,11,12],[13,14,15,16,17,18,19,20,21,22,23,24],[25,26,27,28,29,30,31,32,33,34,35,36],[37,38,39,40,41,42,43,44,45,46,47,48],[49,50,51,52,53,54,55,56,57,58,59,60],[61,62,63,64,65,66,67,68,69,70,71,72],[73,74,75,76,77,78,79,80,81,82,83,84],[85,86,87,88,89,90,91,92,93,94,95,96],[97,98,99,100,101,102,103,104,105,106,107,108],[109,110,111,112,113,114,115,116,117,118,119,120]]
    li0 = [[0 for itr in range(len(li[0]))] for ctr in range(len(li))]
    for i in range(len(li)):
        for j in range(len(li[0])):
            li0[i][j] = encrypt(li[i][j], pk)
            
    res, m, n = DataPacking.divideImgWithPlr(li0, 5, 4, l, pk)    
    res = GaussianFilter.GaussianFilterPackPlr(GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, res, pk, sk)
    res0 = DataPacking.carryUpImgWithPlr(res, l, m, n, 5, 4, pk, sk)    
    for i in res0:
        for j in i:
            print(decrypt(j, sk), end = '\t')
        print()    
            

    start = time.time()
    end = time.time()
    print('1024 size 100000 adds time:\t' + str(end - start))
    
    start = time.time()
    for ctr in range(100000):
       mulClear(a, 4)
    end = time.time()
    print('1024 size 100000 muls time:\t' + str(end - start))

def clearHandle():
    img = ReadAndWriteImage.color2matrix('pic/coins.jpg')
    img = GaussianFilter.GaussianFilter(GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, img)
    img = Sobel.SobelIt(img)
    img = Binary.binary(img)
    ReadAndWriteImage.matrix2img(img, 'pic/testOutput1.bmp')
    print('clear finish')
  
def hybridSys():
    img = ReadAndWriteImage.color2matrix('pic/coins.jpg')
    img = GaussianFilter.GaussianFilter(GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, img)
    ReadAndWriteImage.matrix2img(img, 'pic/testOutput2.bmp')
  
def hybridSysPlr():
    start = time.time()
    pk, sk = plrInit(1024)
    img = ReadAndWriteImage.color2matrixWithPlr('pic/coins.jpg', pk) 
    end = time.time()   
    print('Read finish\t time: ' + str(end - start)) 
    
    start = time.time()
    img = GaussianFilter.GaussianFilterPlr(GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, img, pk, sk) 
    end = time.time()   
    print('Gaussian finish\t time: ' + str(end - start))
    
    start = time.time()
    img = Sobel.SobelItWithPlr(img, pk, sk) 
    end = time.time()   
    print('Sobel finish\t time: ' + str(end - start))
    
    start = time.time()
    img = Binary.binaryWithPlr(img, pk, sk) 
    end = time.time()   
    print('Binary finish\t time: ' + str(end - start))
    '''
    start = time.time()
    c, img = TwoPassAlg.twoPassWithPlr(img, encrypt(255, pk), encrypt(100, pk), pk, sk) 
    end = time.time()   
    print('Two pass finish\t time: ' + str(end - start))
    '''
    start = time.time()
    ReadAndWriteImage.matrix2imgWithPlr(img, 'pic/testOutput000.bmp', sk) 
    end = time.time()   
    print('Write finish\t time: ' + str(end - start)) 
    end = time.time()    

def hybridSysDataPackingPlr():
    start = time.time()
    pk, sk = plrInit(1024)
    l = DataPacking.init(3, 6825)
    img = ReadAndWriteImage.color2matrixWithPlr('pic/coins.jpg', pk) 
    end = time.time()   
    print('Read finish\t time: ' + str(end - start))
    
    start = time.time()
    packRes, m, n = DataPacking.divideImgSpecialWithPlr(img, 32, 16, l, pk) 
    end = time.time()   
    print('Packing finish\t time: ' + str(end - start))
    
    start = time.time()
    GaussianRes = GaussianFilter.GaussianFilterPackPlr(GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, packRes, pk) 
    end = time.time()   
    print('Gaussian finish\t time: ' + str(end - start))
    
    start = time.time()
    SobelRes = Sobel.SobelItWithPlrAndPack(GaussianRes, pk, sk, l, 32) 
    end = time.time()   
    print('Sobel finish\t time: ' + str(end - start))
    
    start = time.time()
    BinaryRes = Binary.binaryWithPlrAndDp(SobelRes, Binary.getSimpleThres() * GaussianFilter.GAUSSIAN_LARGE_Q, pk, sk, l, 32) 
    end = time.time()   
    print('Binary finish\t time: ' + str(end - start))
    
    start = time.time()
    unpackRes = DataPacking.carryUpImgSpecialWithPlr(BinaryRes, l, m, n, 32, 16, pk, sk)
    res = []; onee = encrypt(1, pk)
    for ctr in range(m):
        res.append([])
        for itr in range(n):
            res[ctr].append(subCipher(unpackRes[ctr][itr], onee))  
    end = time.time()   
    print('Unpacking finish\t time: ' + str(end - start))  
    '''
    start = time.time()
    c, img = TwoPassAlg.twoPassWithPlr(res, encrypt(255, pk), encrypt(100, pk), pk, sk) 
    end = time.time()   
    print('Two pass finish\t time: ' + str(end - start))
    '''
    start = time.time()
    ReadAndWriteImage.matrix2imgWithPlr(res, 'pic/testOutput001.bmp', sk) 
    end = time.time()   
    print('Write finish\t time: ' + str(end - start))
    
    end = time.time()    

def hybridSysDataPacking():
    l = DataPacking.init(3, 6825)
    img = ReadAndWriteImage.color2matrix('pic/coins.jpg')
    print('read finish')
    packRes, m, n = DataPacking.divideImgSpecial(img, 75, 140, l)
    print('packing finish')
    GaussianRes = GaussianFilter.GaussianFilterPack(GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, packRes)
    unpackRes = DataPacking.carryUpImgSpecial(GaussianRes, l, m, n, 75, 140) 
    print('unpacking finish')    
    res = []
    for ctr in range(m):
        res.append([])
        for itr in range(n):
            res[ctr].append(unpackRes[ctr][itr] // GaussianFilter.GAUSSIAN_LARGE_Q)
    
    ReadAndWriteImage.matrix2img(res, 'pic/testOutput5.bmp')
    print('write finish')        

def hybridSysPal():
    img = ReadAndWriteImage.color2matrix('pic/coins.jpg')
    threads = []; res = {}; argTuList = []
    res0 = Paral.divMis(img, 4, 4)  
    
    for i in range(16):
        argTuList.append((GaussianFilter.GAUSSIAN_LARGE, GaussianFilter.GAUSSIAN_LARGE_Q, res0[i], i, res))
        
    rez = Paral.palIt(GaussianFilter.GaussianFilterPal, argTuList, threads)     
    res1 = Paral.carryMis(rez, 4, 4) 
    ReadAndWriteImage.matrix2img(res1, 'pic/testOutput3.bmp')  
    
if __name__ == '__main__':
    #hybridSysPlr()
    hybridSysDataPackingPlr()