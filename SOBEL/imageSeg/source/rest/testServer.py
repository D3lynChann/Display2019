from mySocket import *
import pickle

sok, conn, address = initWebEnvS()

conn.sendall(pickle.dumps((12, 23)))

conn.recv(1)

for ctr in range(100):
    conn.sendall(pickle.dumps((12, 23)))
    conn.recv(1)

print('finish!')
