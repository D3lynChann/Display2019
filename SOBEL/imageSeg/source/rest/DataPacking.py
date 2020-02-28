from plr import *
import math

def divideImg(matrix, sm, sn, ll):
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
            res[i].append(pack(tempRes[i][j], ll))
    return res, m, n
    
def divideImgSpecial(matr, sm, sn, ll):
    matrix = []; zeroo = [1 for ctr in range(len(matr[0]) + 2)]
    matrix.append(zeroo[:])
    for i in range(len(matr)):
        temp = []
        temp.append(1)
        temp.extend(matr[i])
        temp.append(1)
        matrix.append(temp)
    matrix.append(zeroo[:])    
    m = len(matr); n = len(matr[0])
    tempRes = [[] for ctr in range(m // sm)]
    res = [[] for ctr in range(sm + 2)]
    for i in range(m // sm):
        for j in range(n // sn):
            startIndeX = i * sm + 1; startIndeY = j * sn + 1
            temp = []; ctr = 0
            for k in range(startIndeX - 1, startIndeX + sm + 1):
                temp.append([])
                for l in range(startIndeY - 1, startIndeY + sn + 1):
                    temp[ctr].append(matrix[k][l])
                ctr += 1  
            tempRes[i].append(temp)    
    for i in range(sm + 2):
        for j in range(sn + 2):
            tempRes0 = []
            for k in range(m // sm):
                for l in range(n // sn):
                    tempRes0.append(tempRes[k][l][i][j])
            res[i].append(pack(tempRes0, ll))  
    return res, m, n 
    
def divideImgSpecialWithPlr(matr, sm, sn, ll, pk):
    ooone = encrypt(1, pk)
    matrix = []; zeroo = [ooone for ctr in range(len(matr[0]) + 2)]
    matrix.append(zeroo[:])
    for i in range(len(matr)):
        temp = []
        temp.append(ooone)
        temp.extend(matr[i])
        temp.append(ooone)
        matrix.append(temp)
    matrix.append(zeroo[:])    
    m = len(matr); n = len(matr[0])
    tempRes = [[] for ctr in range(m // sm)]
    res = [[] for ctr in range(sm + 2)]
    for i in range(m // sm):
        for j in range(n // sn):
            startIndeX = i * sm + 1; startIndeY = j * sn + 1
            temp = []; ctr = 0
            for k in range(startIndeX - 1, startIndeX + sm + 1):
                temp.append([])
                for l in range(startIndeY - 1, startIndeY + sn + 1):
                    temp[ctr].append(matrix[k][l])
                ctr += 1  
            tempRes[i].append(temp)    
    for i in range(sm + 2):
        for j in range(sn + 2):
            tempRes0 = []
            for k in range(m // sm):
                for l in range(n // sn):
                    tempRes0.append(tempRes[k][l][i][j])
            res[i].append(pack(tempRes0, ll))  
    return res, m, n 
    
def divideImgWithPlr(matrix, sm, sn, ll, pk):
    '''
        input: matrix is encrypted data
    '''
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
    
def carryUpImg(matrix, ll, m, n, sm, sn):
    res = [[0 for itr in range(n)] for ctr in range(m)]
    tempRes = [[] for ctr in range(sm)]
    for ctr in range(sm):
        for num in matrix[ctr]:
            tempRes[ctr].append(unpack(num, ll))
    
    tempH = m // sm; tempW = n // sn    
    for i in range(sm):
        for j in range(sn): 
            for k in range(0, tempH):
                for l in range(0, tempW):
                    temp = tempRes[i][j][k * tempW + l]
                    res[i + k * sm][j + l * sn] = temp   
    del tempRes
    return res
    
def carryUpImgSpecial(matrix, ll, m, n, sm, sn):
    temp = matrix[:]
    del temp[0]
    del temp[-1]
    for i in range(sm):
        del temp[i][-1]
        del temp[i][0]
    res = carryUpImg(temp, ll, m, n, sm, sn) 
    return res
    
def carryUpImgSpecialWithPlr(matrix, ll, m, n, sm, sn, pk, sk):
    temp = matrix[:]
    del temp[0]
    del temp[-1]
    for i in range(sm):
        del temp[i][-1]
        del temp[i][0]
    res = carryUpImgWithPlr(temp, ll, m, n, sm, sn, pk, sk) 
    return res

def carryUpImgWithPlr(matrix, ll, m, n, sm, sn, pk, sk):
    '''
        input: matrix is encypted data
    '''
    res = [[0 for itr in range(n)] for ctr in range(m)]
    tempRes = [[] for ctr in range(sm)]
    for ctr in range(sm):
        for num in matrix[ctr]:
            tempRes[ctr].append(unpackWithPlr(num, ll, pk, sk))
    
    tempH = m // sm; tempW = n // sn    
    for i in range(sm):
        for j in range(sn): 
            for k in range(0, tempH):
                for l in range(0, tempW):
                    temp = tempRes[i][j][k * tempW + l]
                    res[i + k * sm][j + l * sn] = temp   
    del tempRes
    return res    

def init(scale, gaussian_l):
    return 1 + scale + math.ceil(math.log10(gaussian_l))
    
def pack(inputList, l):
    L = len(inputList)
    res = 0
    for ctr in range(L):
        res += inputList[ctr] * pow(10, ctr * l)
    return res    
    
def newPack(inputList, l):
    L = len(inputList)
    res = 0
    for ctr in range(L):
        res += (inputList[ctr] * pow(10, ctr * l) + pow(10, l - 1) * pow(10, ctr * l))
    return res        

def newUnPack(inputNum, l):
    inputStr = str(inputNum)
    L = len(inputStr) // l
    res = []
    res.append(int(inputStr[-1 * l + 1: ]))
    for ctr in range(1, L):
        res.append(int(inputStr[l * -1 * (ctr + 1) + 1: l * -1 * ctr]))
    return res     
    
def packWithPlr(inputList, l, pk):
    L = len(inputList)
    res = encrypt(0, pk)
    for ctr in range(L):
        res = addCipher(res, mulClear(inputList[ctr], pow(10, ctr * l)))
    return res  
    
def unpack(inputNum, l):
    inputStr = str(inputNum)
    L = len(inputStr) // l + 1
    res = []
    res.append(int(inputStr[-1 * l: ]))
    for ctr in range(1, L):
        res.append(int(inputStr[l * -1 * (ctr + 1): l * -1 * ctr]))
    return res  

def unpackWithPlr(inputNum, l, pk, sk):
    tempRes = unpack(decrypt(inputNum, sk), l)
    res = []
    for ctr in range(len(tempRes)):
        res.append(encrypt(tempRes[ctr], pk))
    return res  

def SubAbsForPack(pd1, pd2, pk, sk, l, L):
    '''
    打包加密数据的协议减法实现，输入为两个打包加密数据，输出两个之差的绝对值。
    l为每一个单位的长度，L为单位数目
    '''
    temp = encrypt(0, pk); thre = pow(10, l - 1)
    for ctr in range(L):
        temp = addCipher(temp, encrypt(pow(10, (ctr + 1) * l - 1), pk))
    res0 = subCipher(addCipher(pd1, temp), pd2)
    inputStr = str(decrypt(res0, sk))
    res = []
    res.append(encrypt(thre - int(inputStr[-1 * l + 1: ]) if int(inputStr[-1 * l + 1: ]) > thre // 2 else int(inputStr[-1 * l + 1: ]), pk))
    for ctr in range(1, L):
        cur = int(inputStr[l * -1 * (ctr + 1) + 1: l * -1 * ctr])
        res.append(encrypt(cur if cur < thre // 2 else thre - cur, pk))
    return packWithPlr(res, l, pk)     

def CompForPack(pd1, pd2, pk, sk, l, L):
    '''
    打包加密数据的协议减法实现，输入为两个打包加密数据，输出两个比较结果。
    l为每一个单位的长度，L为单位数目
    '''
    temp = encrypt(0, pk); thre = pow(10, l - 1)
    for ctr in range(L):
        temp = addCipher(temp, encrypt(pow(10, (ctr + 1) * l - 1), pk))
    res0 = subCipher(addCipher(pd1, temp), pd2)
    inputStr = str(decrypt(res0, sk))
    res = []
    res.append(encrypt(1 if int(inputStr[-1 * l + 1: ]) > thre // 2 else 2, pk))
    for ctr in range(1, L):
        cur = int(inputStr[l * -1 * (ctr + 1) + 1: l * -1 * ctr])
        res.append(encrypt(2 if cur < thre // 2 else 1, pk))
    return packWithPlr(res, l, pk)     
    
def test():
    li = [[1,2,3,4,5,6,7,8,9,10,11,12],[13,14,15,16,17,18,19,20,21,22,23,24],[25,26,27,28,29,30,31,32,33,34,35,36],[37,38,39,40,41,42,43,44,45,46,47,48],[49,50,51,52,53,54,55,56,57,58,59,60],[61,62,63,64,65,66,67,68,69,70,71,72],[73,74,75,76,77,78,79,80,81,82,83,84],[85,86,87,88,89,90,91,92,93,94,95,96],[97,98,99,100,101,102,103,104,105,106,107,108],[109,110,111,112,113,114,115,116,117,118,119,120]]
    res, m, n = divideImgSpecial(li, 5, 6, 4)
    carryUpImgSpecial(res, 4, m, n, 5, 6) 
        
if __name__ == '__main__':
    test()