from plr import *
from mySocket import *
import os, numpy, pickle, AES, random, pyaes

def generateRanKey(sign, l):
    return sign + os.urandom(l)

def createGCTs(numOfGates):
    #initial wires' garbled values
    sign = os.urandom(8)
    x = [[], []]
    y = [[], []]
    s = [[], []]
    c = [[], []]
    GCT = []
    
    #genarate keys
    c[0].append(generateRanKey(sign, 8))
    c[1].append(generateRanKey(sign, 8))
    for i in range(numOfGates):
        for j in range(2):
            x[j].append(generateRanKey(bytes(0), 16))
            y[j].append(generateRanKey(bytes(0), 16))
            s[j].append(generateRanKey(bytes(0), 16))
            c[j].append(generateRanKey(sign, 8))
    
    #use true value table to genarate GCTs
    #GCT[gate No.][s_GCT or c_GCT][garbled value No.]
    
    trueValueTable = [[0, 0, 0, 0, 0], [0, 0, 1, 1, 1], [0, 1, 0, 1, 1], [0, 1, 1, 0, 1], [1, 0, 0, 1, 0], [1, 0, 1, 0, 0], [1, 1, 0, 0, 0], [1, 1, 1, 1, 1]]
    #add TVT
    #trueValueTable = [[0, 0, 0, 0, 0], [0, 0, 1, 1, 0], [0, 1, 0, 1, 0], [0, 1, 1, 0, 1], [1, 0, 0, 1, 0], [1, 0, 1, 0, 1], [1, 1, 0, 0, 1], [1, 1, 1, 1, 1]]
    for ctr in range(numOfGates):
        s_GCT = []; c_GCT = []
        for ta in trueValueTable:
            s_GCT.append(AES.E(AES.generateAES(x[ta[0]][ctr]), AES.E(AES.generateAES(y[ta[1]][ctr]), AES.E(AES.generateAES(c[ta[2]][ctr]), s[ta[3]][ctr]))))
            c_GCT.append(AES.E(AES.generateAES(x[ta[0]][ctr]), AES.E(AES.generateAES(y[ta[1]][ctr]), AES.E(AES.generateAES(c[ta[2]][ctr]), c[ta[4]][ctr + 1]))))   
        GCT.append([s_GCT, c_GCT]) 
    
    #create an list sign
    sign = list(sign)
    
    return x, y, s, c, sign, GCT 
    
def getInputValue(inputList, x):
    res = []
    ctr = 0
    for i in inputList:
        res.append(x[i][ctr])
        ctr += 1
    return res 

def decryptGCTs(sign, inputValueY, inputValueX, GCT, numOfGate, c_init, s, c0):
    subC = c_init; finalC = []; finalS = []; Cs = [c_init] 
    for ctr in range(numOfGate):
        c_GCT = GCT[ctr][1]; res = []
        for line in c_GCT:
            res = AES.D(AES.generateAES(bytes(subC)), AES.D(AES.generateAES(inputValueY[ctr]), AES.D(AES.generateAES(inputValueX[ctr]), line)))
            if res[: 8] == sign:
                subC = bytes(res)
                Cs.append(subC)
                break    
                
    finalC = (0 if subC == c0 else 1)
        
    for ctr in range(numOfGate):
        s_GCT = GCT[ctr][0]; res = []
        for line in s_GCT:
            res = AES.D(AES.generateAES(Cs[ctr]), AES.D(AES.generateAES(inputValueY[ctr]), AES.D(AES.generateAES(inputValueX[ctr]), line)))
            if list(s[0][ctr]) == res:
                finalS.append(0)
                break
            if list(s[1][ctr]) == res:
                finalS.append(1)
                break
                
    return finalS, finalC   
        
if __name__ == '__main__':
    numOfGate = 6
    x, y, s, c, sign, GCT = createGCTs(numOfGate)
    inputValueX = getInputValue([1, 1, 1, 1, 1, 1], x)
    inputValueY = getInputValue([0, 1, 0, 1, 0, 1], y)
    c_init = c[0][0]
    finalS, finalC = decryptGCTs(sign, inputValueY, inputValueX, GCT, numOfGate, c_init, s, c[0][numOfGate])
    print(finalS, finalC)