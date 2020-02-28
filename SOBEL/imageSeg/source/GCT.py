import os, numpy, pickle, AES, random, pyaes, socket
from plr import *

TVTComp = [[0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1]]
TVTMux = [[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 1, 1], [1, 0, 0, 0], [1, 0, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1]]

def generateRanKey(sign, l):
    return sign + os.urandom(l)

def binS(num):
    temp = abs(num)
    res = []
    while temp != 0:
        temp, remainder = divmod(temp, 2)
        res.append(remainder)
    while len(res) < 10:
        res.append(0)
    
    res = res[-7: ]
    res.append(0 if num <= 0 else 1)
    return res    

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

def createGCTs(numOfGates, trueValueTable):
    #initial wires' garbled values
    sign = os.urandom(8)
    x = [[], []]
    y = [[], []]
    c = [[], []]
    GCT = []
    
    #genarate keys
    c[0].append(generateRanKey(sign, 8))
    c[1].append(generateRanKey(sign, 8))
    for i in range(numOfGates):
        for j in range(2):
            x[j].append(generateRanKey(bytes(0), 16))
            y[j].append(generateRanKey(bytes(0), 16))
            c[j].append(generateRanKey(sign, 8))
    
    #use true value table to genarate GCTs
    #GCT[gate No.][s_GCT or c_GCT][garbled value No.]

    for ctr in range(numOfGates):
        for ta in trueValueTable:
            GCT.append(AES.E(AES.generateAES(x[ta[0]][ctr]), AES.E(AES.generateAES(y[ta[1]][ctr]), AES.E(AES.generateAES(c[ta[2]][ctr]), c[ta[3]][ctr + 1]))))  
    
    #create an list sign
    sign = list(sign)
    
    return x, y, c, sign, GCT   
    
def unpacked(conn, pk, sk, l, L):
    '''
        l, L通过外部获取,顺便解包了┗|｀O′|┛ 嗷~~
    '''
    inputStr = str(decrypt(pickle.loads(conn.recv(8192)), sk))
    res = []
    res.append(int(inputStr[-1 * l + 1: ]))
    for ctr in range(1, L):
        cur = int(inputStr[l * -1 * (ctr + 1) + 1: l * -1 * ctr])
        res.append(cur)
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
    '''
    file = open('C:/Users/D3lyn/Desktop/imageSeg/source/bina.txt', 'w')
    for ctr in range(-1023, 1023):
        temp = binS(ctr)
        tempStr = ''
        for num in temp:
            tempStr += str(num)
        file.write(tempStr + '\n')
    file.close()
    '''
    file = open('C:/Users/D3lyn/Desktop/imageSeg/source/bina.txt', 'r')
    lines = file.readlines()
    file.close()    
    res = []
    for line in lines:
        temp = []
        for ctr in range(8):
            temp.append(int(line[ctr]))
        res.append(temp)
    return res
    
if __name__ == '__main__':
    test()