from phe import paillier

def plrInit(KEY_SIZE = 64):
    pk, sk = paillier.generate_paillier_keypair(n_length = KEY_SIZE)
    return pk, sk

def plrInitPlus(KEY_SIZE = 64):
    pk, sk = paillier.generate_paillier_keypair(n_length = KEY_SIZE)
    return pk, sk, pk.n    
    
def addCipher(a, b):
    assert type(a).__name__ == 'EncryptedNumber'
    assert type(b).__name__ == 'EncryptedNumber'
    return a + b

def addListCipher(lis):
    res = lis[0]
    for i in range(1, len(lis)):
        res = addCipher(res, lis[i])
    return res  

def mulListClear(lis, b):
    res = []
    for i in lis:
        res.append(mulClear(i, b))
    return res    

def subCipher(a, b):
    assert type(a).__name__ == 'EncryptedNumber'
    assert type(b).__name__ == 'EncryptedNumber'
    return a - b      
    
def mulClear(a, b):
    assert type(a).__name__ == 'EncryptedNumber'
    assert type(b).__name__ == 'int'
    return a * b

def getCipherText(a):
    assert type(a).__name__ == 'EncryptedNumber' 
    return a.ciphertext()    

def encrypt(a, pk):
    assert type(a).__name__ == 'int'
    return pk.encrypt(a)

def decrypt(a, sk):
    assert type(a).__name__ == 'EncryptedNumber' 
    return sk.decrypt(a)
    
def decryptPlus(a, sk, n):
    assert type(a).__name__ == 'EncryptedNumber' 
    return (n + sk.decrypt(a)) if sk.decrypt(a) < 0 else sk.decrypt(a)
    
def divProtocol(a, b, pk, sk):
    '''
    the protocol has not accomplished yet
    '''
    assert type(a).__name__ == 'EncryptedNumber'
    assert type(b).__name__ == 'int' 
    return encrypt(decrypt(a, sk) // b, pk)  
    
def absProtocol(a, pk, sk):
    '''
    the protocol has not accomplished yet
    '''
    assert type(a).__name__ == 'EncryptedNumber'
    return encrypt(abs(decrypt(a, sk)), pk)   

def compProtocol(a, b, sk):
    '''
    the protocol has not accomplished yet
    '''
    assert type(a).__name__ == 'EncryptedNumber'
    assert type(b).__name__ == 'EncryptedNumber'
    aa = decrypt(a, sk); bb = decrypt(b, sk)
    if aa > bb:
        return 1
    elif aa == bb:
        return 0
    else:
        return -1