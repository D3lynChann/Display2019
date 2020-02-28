from plr import *

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

def GaussianFilter(filter, filter_q, matrix):
    '''
    明文域高斯滤波，边缘忽略不计算
    '''
    assert type(matrix).__name__ == 'list'
    spaceIndex = len(filter) // 2
    res = [[] for ctr in range(len(matrix))]
    for ctr in range(spaceIndex):
        res[ctr] = matrix[ctr][:]
        res[-1 * (ctr + 1)] = matrix[-1 * (ctr + 1)][:]
    for i in range(spaceIndex, len(matrix) - spaceIndex):
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][ctr])
        for j in range(spaceIndex, len(matrix[0]) - spaceIndex):
            tempRes = 0
            for k in range(-1 * spaceIndex, spaceIndex + 1):
                for l in range(-1 * spaceIndex, spaceIndex + 1):
                    tempRes += matrix[i + k][j + l] * filter[spaceIndex + k][spaceIndex + l]
            res[i].append(tempRes // filter_q)
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][-1 * (ctr + 1)])  
    return res        

def GaussianFilterPlr(filter, filter_q, matrix, pk, sk): 
    '''
    密文域高斯滤波，边缘忽略不计算
    还需传输两组密钥
    输入输出均为加密矩阵
    '''  
    assert type(matrix).__name__ == 'list'
    res = [[] for ctr in range(len(matrix))]
    spaceIndex = len(filter) // 2
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
            res[i].append(divProtocol(tempRes, filter_q, pk, sk))
            del tempRes
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][-1 * (ctr + 1)])    
    return res   

def GaussianFilterPal(filter, filter_q, matrix, num, resDict):
    '''
    并行化高斯滤波，输入的num和resDict用来定位输出
    '''
    assert type(matrix).__name__ == 'list'
    spaceIndex = len(filter) // 2
    res = [[] for ctr in range(len(matrix))]
    for ctr in range(spaceIndex):
        res[ctr] = matrix[ctr][:]
        res[-1 * (ctr + 1)] = matrix[-1 * (ctr + 1)][:]
    for i in range(spaceIndex, len(matrix) - spaceIndex):
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][ctr])
        for j in range(spaceIndex, len(matrix[0]) - spaceIndex):
            tempRes = 0
            for k in range(-1 * spaceIndex, spaceIndex + 1):
                for l in range(-1 * spaceIndex, spaceIndex + 1):
                    tempRes += matrix[i + k][j + l] * filter[spaceIndex + k][spaceIndex + l]
            res[i].append(tempRes // filter_q)
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][-1 * (ctr + 1)])  
    resDict[num] = res     
    
def GaussianFilterPackPlr(filter, filter_q, matrix, pk):
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

def GaussianFilterPack(filter, filter_q, matrix):
    '''
    DP的加密数据的高斯滤波
    输入输出均为DP加密矩阵
    此时没有进行除法运算
    '''
    assert type(matrix).__name__ == 'list'
    res = [[] for ctr in range(len(matrix))]
    spaceIndex = len(filter) // 2
    for ctr in range(spaceIndex):
        temp0 = matrix[ctr][:]
        for i in range(len(temp0)):
            temp0[i] *= filter_q
        res[ctr] = temp0[:]
        temp0 = matrix[-1 * (ctr + 1)][:]
        for i in range(len(temp0)):
            temp0[i] *= filter_q
        res[-1 * (ctr + 1)] = temp0[:]
    for i in range(spaceIndex, len(matrix) - spaceIndex):
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][ctr] * filter_q)
        for j in range(spaceIndex, len(matrix[0]) - spaceIndex):
            tempRes = 0
            for k in range(-1 * spaceIndex, spaceIndex + 1):
                for l in range(-1 * spaceIndex, spaceIndex + 1):
                    temp = matrix[i + k][j + l] * filter[spaceIndex + k][spaceIndex + l]
                    tempRes += temp
            res[i].append(tempRes)
            del tempRes
        for ctr in range(spaceIndex):
            res[i].append(matrix[i][-1 * (ctr + 1)] * filter_q)   
    return res    