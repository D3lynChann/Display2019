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
    
    trueValueTable = [[0, 0, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1]]
    for ctr in range(numOfGates):
        for ta in trueValueTable:
            GCT.append(AES.E(AES.generateAES(x[ta[0]][ctr]), AES.E(AES.generateAES(y[ta[1]][ctr]), AES.E(AES.generateAES(c[ta[2]][ctr]), c[ta[3]][ctr + 1]))))  
    
    #create an list sign
    sign = list(sign)
    
    return x, y, c, sign, GCT 
    
def getInputValue(inputList, x):
    res = []
    ctr = 0
    for i in inputList:
        res.append(x[i][ctr])
        ctr += 1
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
        
if __name__ == '__main__':
    numOfGate = 10
    x, y, c, sign, GCT = createGCTs(numOfGate)
    inputValueX = getInputValue([1, 1, 1, 1, 0, 1, 0, 0, 0, 0], x)
    inputValueY = getInputValue([0, 1, 0, 1, 1, 1, 0, 0, 0, 0], y)
    c_init = c[0][0]
    finalC = decryptGCTs(sign, inputValueY, inputValueX, GCT, numOfGate, c_init, c[0][numOfGate])
    print(finalC)