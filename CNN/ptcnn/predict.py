# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pickle
'''同路径下py模块引用'''
try:
    from . import data_utils
    from . import solver
    from . import cnn
except Exception:
    import data_utils
    import solver
    import cnn

import numpy as np
# 获取样本数据
data = data_utils.get_CIFAR10_data()
modelFile = open('G:/codes/2020new/ptcnn/model.txt', 'rb')
best_model = pickle.load(modelFile)
modelFile.close()
print('ok')
y_test_pred = np.argmax(best_model.loss(data['X_test']), axis=1)
y_val_pred = np.argmax(best_model.loss(data['X_val']), axis=1)
print('Validation set accuracy: ',(y_val_pred == data['y_val']).mean())
print('Test set accuracy: ', (y_test_pred == data['y_test']).mean())