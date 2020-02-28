from mySocket import *
import pickle

sok, conn, address = initWebEnvS()

conn.sendall(pickle.dumps((12, 23)))