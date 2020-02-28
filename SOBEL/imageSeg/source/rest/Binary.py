from plr import *
import DataPacking

#二值化

def getSimpleThres():
    '''
    获得经验阈值
    '''
    Gmax = 255; Gmin = 0
    return Gmax - (Gmax - Gmin) // 3
    
def binary(matrix):
    '''
    根据经验阈值对明文域内图像进行二值化，输入输出均为矩阵
    '''
    T = getSimpleThres()
    res = [[] for ctr in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            res[i].append(0 if matrix[i][j] < T else 255)
    return res   

def binaryWithPlr(matrix, pk, sk):
    '''
    根据经验阈值对密文域内图像进行二值化，输入输出均为矩阵，还需要传输两份密钥
    '''
    T = encrypt(getSimpleThres(), pk)
    res = [[] for ctr in range(len(matrix))]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            res[i].append(encrypt(255, pk) if compProtocol(matrix[i][j], T, sk) >= 0 else encrypt(0, pk))
    return res    

def subBinaryWithPlrAndDp(dp, Ts, pk, sk, l, L):
    '''
    二值化，利用datapack的比较，注意结果加上一以防侧漏
    '''    
    res1 = DataPacking.CompForPack(dp, Ts, pk, sk, l, L)
    res2 = DataPacking.unpackWithPlr(res1, l, pk, sk)
    res3 = []; onee = encrypt(1, pk)
    for ctr in range(len(res2)):
        res3.append(encrypt(256, pk) if compProtocol(res2[ctr], onee, sk) >= 0 else encrypt(1, pk)) 
    res4 = DataPacking.packWithPlr(res3, l, pk) 
    return res4

def binaryWithPlrAndDp(matrix, T, pk, sk, l, L): 
    res0 = [encrypt(T, pk) for jtr in range(L)]
    res0 = DataPacking.packWithPlr(res0, l, pk)
    res = [[] for ctr in range(len(matrix))] 
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[0])):
            res[ctr].append(subBinaryWithPlrAndDp(matrix[ctr][itr], res0, pk, sk, l, L))
    return res        

if __name__ == '__main__':
    pk, sk = plrInit(512)
    li0 = [244, 34, 67, 100]
    li01 = []
    for num in li0:
        li01.append(encrypt(num, pk))
    res1 = DataPacking.packWithPlr(li01, 8, pk)
    res2 = [[res1]]
    res3 = binaryWithPlrAndDp(res2, 125, pk, sk, 8, 4)
    print(decrypt(res3[0][0], sk))