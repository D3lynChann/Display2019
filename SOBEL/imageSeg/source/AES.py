from pyaes import *
import os, numpy

def generateAes(keySize = 16):
    key = os.urandom(keySize)
    return AES(key)
    
def generateAES(key):
    return AES(key)    

def E(aes, plaintext):
    return aes.encrypt(plaintext)
    
def D(aes, ciphertext):
    return aes.decrypt(ciphertext)  

def getRes(li):
    return int(sum(li) / len(li))

def OT(input1, input2, s):
    return input1 if s == 0 else input2