from mySocket import *
import pickle

sok = initWebEnvC()

tup = pickle.loads(sok.recv(4096))
print(tup)