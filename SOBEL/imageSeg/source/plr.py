from phe import paillier

initP1024 = 12487210913669987076526020022976573194319993993938252811898710142157989090511036069867469640339577134874850216109999644669109610468775603453160589565121637
initQ1024 = 10727087481820311139845870783035236841841366041752215236488534771730036991602720006434662374951629717830061790530004004422493013233346257615261398282277671

initP2048 = 142771884146716563507042201149688900594663109365515913888304654209499259567179777344199627574338382271941618669627867893167662348949574464430111278579880566915070493955836899370768821799823799449424466305281797266799181298536904422644124892169858644585341019352652890609876772612620780508033370615879697109053
initQ2048 = 113444369271967446525934593589084658339568920358652561879293463472686261811741539518093814378734374042025149474568020197679770150141191508802382770511871421863661661187634923414766327954758239627408603161766435475813443521279301039585541865880292067026286260240282018427581793540534174374551856106498680234931

def plrInit(KEY_SIZE = 64):
    pk, sk = paillier.generate_paillier_keypair(n_length = KEY_SIZE)
    return pk, sk
    
def plrInitWithPQ(p = initP1024, q = initQ1024):
    pk, sk = paillier.generate_paillier_keypair_1(p, q)

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