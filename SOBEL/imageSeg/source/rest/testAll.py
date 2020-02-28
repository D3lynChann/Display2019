import pickle
import ReadAndWriteImage
from plr import *

pk, sk = plrInit(256)
print('reading...')
img = ReadAndWriteImage.color2matrixWithPlr('pic/coins.jpg', pk)
print('dumping...')
imgFile = open('file/testImg.txt', 'wb')
pickle.dump(img, imgFile)
imgFile.close()
print('loading...')
imgFile = open('file/testImg.txt', 'rb')
imgSecond = pickle.load(imgFile)
imgFile.close()
print('writing')
ReadAndWriteImage.matrix2imgWithPlr(imgSecond, 'pic/testOutPut00000002.bmp', sk) 
print('finish')