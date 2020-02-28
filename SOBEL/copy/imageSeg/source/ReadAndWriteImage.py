import numpy as np
from PIL import Image
from plr import *
import numpy as np

'''
一个读图片和写图片的模块
'''
def rgb2gray(rgb):
  return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
  
def color2matrix_abd(fileName):
    '''
    利用cv2读取图片，得到列表
    '''
    img = rgb2gray(mpimg.imread(fileName)).tolist()
    for ctr in range(len(img)):
        for itr in range(len(img[0])):
            img[ctr][itr] = int(img[ctr][itr])
    #img = cv2.imread(fileName, cv2.IMREAD_GRAYSCALE).tolist()
    return img
    
def color2matrix(fileName):
    return np.array(Image.open(fileName).convert('I')).tolist()
    
def matrix2img(matrix, fileName):
    assert type(matrix).__name__ == 'list'
    tempArr = np.array(matrix)
    tempArr = np.array(tempArr, dtype = 'uint8')
    tempArr = Image.fromarray(tempArr)
    tempArr.save(fileName, 'bmp')

def color2matrixWithPlr(fileName, pk):
    image = color2matrix(fileName)
    for ctr in range(len(image)):
        for itr in range(len(image[ctr])):
            image[ctr][itr] = encrypt(image[ctr][itr], pk)
    return image     

def matrix2imgWithPlr(matrix, fileName, sk):
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[ctr])):
            matrix[ctr][itr] = decrypt(matrix[ctr][itr], sk)
    matrix2img(matrix, fileName)
    
