import pickle, socket
from plr import *
from mySocket import *
import ReadAndWriteImage 
import struct
import os
import sys
    
#filePath = 'I:/codes/imageSeg/source'    
#filePath = ''
filePath = 'C:/Users/D3lynChann/Desktop/imageSeg/source'
    
def getPkAndSkFromPsp():
    sok = initWebEnvC()
    print('ask for pk...')
    sok.send('ask..'.encode())
    pk_str = sok.recv(2048)
    print('ask for sk...')
    sok.send('ask..'.encode())
    sk_str = sok.recv(2048)
    pk = pickle.loads(pk_str)
    sk = pickle.loads(sk_str)
    
    print('get pk and sk from psp...')
    print('now socket is closing...')
    sok.close() 
    return pk, sk   

def sendImageToCloudServer(fileName, pk):
    print('reading the image...')
    image = ReadAndWriteImage.color2matrixWithPlr(fileName, pk)
    print('upload to file...')
    imgFile = open(filePath + '/file/testImg.txt', 'wb')
    pickle.dump(image, imgFile)
    imgFile.close()
    print('upload finish, connect to cloud server...')
    ADDR = (localIp, 10086)
    BUFSIZE = 1024
    FILEINFO_SIZE=struct.calcsize('128s32sI8s')
    sendSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendSock.connect(ADDR)
    fhead = struct.pack('128s11I', bytes(os.path.basename(filePath + '/file/testImg.txt').encode('utf-8')), 0, 0, 0, 0, 0, 0, 0, 0, os.stat(filePath + '/file/testImg.txt').st_size, 0, 0)
    sendSock.send(fhead)
    fp = open(filePath + '/file/testImg.txt', 'rb')
    print('file transmitting...')
    while 1:
        filedata = fp.read(BUFSIZE)
        if not filedata: 
            break
        sendSock.send(filedata)
    print("transmittion finish...")
    fp.close()
    sendSock.close()
    print("socket is closed...")

def hybridSystem():
    pk, sk = getPkAndSkFromPsp() 
    sendImageToCloudServer(filePath + '/pic/coins.jpg', pk)
    print('ez job, goodbye!')      
    
if __name__ == '__main__':  
    hybridSystem()