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
# model初始化（权重因子以及对应偏置 w1,b1 ,w2,b2 ,w3,b3，数量取决于网络层数）
model = cnn.ThreeLayerConvNet(reg=0.9)
solver = solver.Solver(model, data,
                lr_decay=0.95,                
                print_every=10, num_epochs=5, batch_size=2, 
                update_rule='sgd_momentum',                
                optim_config={'learning_rate': 5e-4, 'momentum': 0.9})
# 训练，获取最佳model
solver.train()         
best_model = model
modelFile = open('G:/codes/2020new/ptcnn/model.txt', 'wb')
pickle.dump(best_model, modelFile)
modelFile.close()
print('ok')