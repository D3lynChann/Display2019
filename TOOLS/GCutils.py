from phe import *
def GCcomp2(a, b, pk, sk):
    return pk.encrypt(1) if sk.decrypt(a) >= sk.encrypt(b) else pk.encrypt(-1)
    
def GCequa2(a, b, pk, sk):
    return pk.encrypt(1) if sk.decrypt(a) == sk.encrypt(b) else pk.encrypt(-1)
    
def divClear(a, b, pk, sk):
    return pk.encrypt(sk.decrypt(a) // b)