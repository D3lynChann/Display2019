from mySocket import *
import pickle

sok = initWebEnvC()

tup = pickle.loads(sok.recv(4096))
print(tup)
sok.send(bytes(1))

for ctr in range(100):
    print(pickle.loads(sok.recv(4096)))
    sok.send(bytes(1))

print('finish!')
