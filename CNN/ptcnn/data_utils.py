# -*- coding: utf-8 -*-
import pickle 
import numpy as np
import os

#from scipy.misc import imread

def load_CIFAR_batch(filename):
    """ load single batch of cifar """
    with open(filename, 'rb') as f:
        datadict = pickle.load(f, encoding='bytes')
        #datadict为尺寸为4的字典:b'labels', b'data', b'filenames', b'batch_label'
        X = datadict[b'data']
        Y = datadict[b'labels']
        #X的尺寸为10000*3072（10000张图片，每个图片尺寸为32*32，三通道），reshape为10000*32*32*3，再通过transpose令索引值(x',y',z',w')=(x,z,w,y)，最后转为float类型
        #三个channel分别为rgb
        #索引为（图片编号，x索引，y索引，rgb三通道）
        X = X.reshape(10000, 3, 32, 32).transpose(0,2,3,1).astype("float")
        Y = np.array(Y)
        return X, Y

def load_CIFAR10(ROOT):
    """ load all of cifar """
    xs = []
    ys = []
    for b in range(1,2):
        f = os.path.join(ROOT, 'data_batch_%d' % b)
        X, Y = load_CIFAR_batch(f)
        xs.append(X)
        ys.append(Y)   
    #利用np.concatenate将xs、ys弄成一行
    Xtr = np.concatenate(xs)
    Ytr = np.concatenate(ys)
    del X, Y
    #获取测试集
    Xte, Yte = load_CIFAR_batch(os.path.join(ROOT, 'test_batch'))
    return Xtr, Ytr, Xte, Yte


def get_CIFAR10_data(num_training = 200, num_validation = 50, num_test = 50):
    #训练集，验证集，测试集
    #加载数据
    cifar10_dir = 'G:/codes/2020new/ptcnn/cifar-10-batches-py'
    X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)
    print (X_train.shape)
    #划分数据
    mask = range(num_training, num_training + num_validation)
    X_val = X_train[mask]
    y_val = y_train[mask]
    mask = range(num_training)
    X_train = X_train[mask]
    y_train = y_train[mask]
    mask = range(num_test)
    X_test = X_test[mask]
    y_test = y_test[mask]
    #标准化数据，求样本均值，然后 样本 - 样本均值，作用：使样本数据更收敛一些，便于后续处理
    #如果2维空间 m*n np.mean()后 => 1*n
    #对于4维空间 m*n*k*j np.mean()后 => 1*n*k*j
    
    mean_image = np.mean(X_train, axis=0)
    X_train -= mean_image
    X_val -= mean_image
    X_test -= mean_image
    

    #把通道channel提前
    X_train = X_train.transpose(0, 3, 1, 2).copy()
    X_val = X_val.transpose(0, 3, 1, 2).copy()
    X_test = X_test.transpose(0, 3, 1, 2).copy()
    #将数据打包为一个字典并返回
    return {
      'X_train': X_train, 'y_train': y_train,
      'X_val': X_val, 'y_val': y_val,
      'X_test': X_test, 'y_test': y_test,
    }