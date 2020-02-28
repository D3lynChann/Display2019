from plr import *
from pyaes import *
import os, numpy

inputOnes = [1 for ctr in range(16)]
inputZeros = [0 for ctr in range(16)]

def genrateAes(keySize = 16):
    key = os.urandom(keySize)
    return AES(key)

def E(aes, plaintext):
    return aes.encrypt(plaintext)
    
def D(aes, ciphertext):
    return aes.decrypt(ciphertext)  

def getRes(li):
    return int(sum(li) / len(li))

def OT(input1, input2, s):
    return input1 if s == 0 else input2
    
class Alice(object):
    def __init__(self, gateType, input):
        #genarate 6 keys
        k_x_0 = genrateAes(); k_x_1 = genrateAes()
        k_y_0 = genrateAes(); k_y_1 = genrateAes()
        k_z_0 = [0 for ctr in range(16)]; k_z_1 = [1 for ctr in range(16)]
        self.keys = [k_x_0, k_x_1, k_y_0, k_y_1]
        #create GCT
        GCT = []
        if gateType == 'andGate':
            GCT.append(E(k_x_0, E(k_y_0, k_z_0)))
            GCT.append(E(k_x_0, E(k_y_1, k_z_0)))
            GCT.append(E(k_x_1, E(k_y_0, k_z_0)))
            GCT.append(E(k_x_1, E(k_y_1, k_z_1)))
        elif gateType == 'orGate':    
            GCT.append(E(k_x_0, E(k_y_0, k_z_0)))
            GCT.append(E(k_x_0, E(k_y_1, k_z_1)))
            GCT.append(E(k_x_1, E(k_y_0, k_z_1)))
            GCT.append(E(k_x_1, E(k_y_1, k_z_1)))
        elif gateType == 'xorGate':
            GCT.append(E(k_x_0, E(k_y_0, k_z_0)))
            GCT.append(E(k_x_0, E(k_y_1, k_z_1)))
            GCT.append(E(k_x_1, E(k_y_0, k_z_1)))
            GCT.append(E(k_x_1, E(k_y_1, k_z_0)))
        #rearrange GCT
        numpy.random.shuffle(GCT)
        self.GCT = GCT
        self.gateType = gateType
        self.input = input
    
    def aliceOT(self):
        return self.keys[2], self.keys[3]
    
    def sendKeysAndGCTToBob(self):
        return self.GCT, self.keys[self.input]
        
class Bob(object):
    def __init__(self, input):
        self.input = input
    def getKeysAndGCTFromAlice(self, GCT, aInput):
        self.GCT = GCT
        self.aInput = aInput
    def getInputFromAlice(self, bInput):
        self.bInput = bInput
    def bobOT(self):
        return self.input
    def decryptGCT(self):
        for line in self.GCT:
            if getRes(D(self.bInput, D(self.aInput, line))) == 0:
                return 0
            if getRes(D(self.bInput, D(self.aInput, line))) == 1:
                return 1
        print('wrong!')   

def process(alice, bob):
    assert type(alice).__name__ == 'Alice'  
    assert type(bob).__name__ == 'Bob'
    GCT, keyOfAlice = alice.sendKeysAndGCTToBob()
    bob.getKeysAndGCTFromAlice(GCT, keyOfAlice)
    keyOfBob = OT(alice.aliceOT()[0], alice.aliceOT()[1], bob.bobOT())
    bob.getInputFromAlice(keyOfBob)
    return bob.decryptGCT()
        
def fullAdder(a, b, c1):
    Alice01 = Alice('xorGate', a); Bob01 = Bob(b)
    w1 = process(Alice01, Bob01)
    
    Alice02 = Alice('andGate', a); Bob02 = Bob(b)
    w2 = process(Alice02, Bob02)
    
    Alice03 = Alice('xorGate', c1); Bob03 = Bob(w1)
    res = process(Alice03, Bob03)
    
    Alice04 = Alice('andGate', c1); Bob04 = Bob(w1)
    w4 = process(Alice04, Bob04)
    
    Alice05 = Alice('orGate', w4); Bob05 = Bob(w2)
    c2 = process(Alice05, Bob05)
    
    return res, c2
    
        
if __name__ == '__main__':
    a = 1; b = 1; c1 = 1
    print('b: ', a)
    print('a: ', b)
    print('c1: ', c1)
    res, c2 = fullAdder(a, b, c1)
    print('res: ', res)
    print('c2: ', c2)