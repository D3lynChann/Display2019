# -*- coding: utf-8 -*-
try:
    from . import layer_utils
    from . import layers
except Exception:
    import layer_utils
    import layers
import numpy as np

class  ThreeLayerConvNet(object):
    """    
        三层的网络，结构如下       
        卷积层conv - 激活函数relu - 池化层2x2 max pool - 全连接affine - 激活函数relu - 全连接affine - 损失函数softmax
    """
    def __init__(self, input_dim = (3, 32, 32), num_filters = 32, filter_size = 7, hidden_dim = 100, num_classes = 10, weight_scale = 1e-3, reg = 0.0, dtype = np.float32):
        self.params = {}
        self.reg = reg
        self.dtype = dtype

        #初始化权重w和偏置b，randn函数返回一个或一组具有标准正态分布的样本（n维矩阵）
        C, H, W = input_dim
        #w1为32*3*7*7的权重矩阵，用于卷积层，即有32个滤波器，每个滤波器的尺寸为3*7*7
        self.params['W1'] = weight_scale * np.random.randn(num_filters, C, filter_size, filter_size)
        self.params['b1'] = np.zeros(num_filters)
        #w2为32*32*8*100的权重矩阵，用于第一个全连接层
        self.params['W2'] = weight_scale * np.random.randn(num_filters * H * W // 4, hidden_dim)
        self.params['b2'] = np.zeros(hidden_dim)
        #w3为100*10的权重矩阵，用于第二个全连接层
        self.params['W3'] = weight_scale * np.random.randn(hidden_dim, num_classes)
        self.params['b3'] = np.zeros(num_classes)

        #转换格式
        for k, v in self.params.items():    
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        #得到参数
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        W3, b3 = self.params['W3'], self.params['b3']

        #得到卷积参数（步长和边界补零规模），后面传给卷积层
        filter_size = W1.shape[2]
        conv_param = {'stride': 1, 'pad': (filter_size - 1) // 2}

        # pass pool_param to the forward pass for the max-pooling layer
        #得到池化参数（池子尺寸和步长），后面传给池化层
        pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

        # 开始计算前向传播过程：卷积层conv - 激活函数relu - 池化层2x2 max pool - 全连接affine - 激活函数relu - 全连接affine
        # 加密域主要看这里
        a1, cache1 = layer_utils.conv_relu_pool_forward(X, W1, b1, conv_param, pool_param)
        a2, cache2 = layer_utils.affine_relu_forward(a1, W2, b2)
        scores, cache3 = layers.affine_forward(a2, W3, b3)

        if y is None:    
            return scores

        #计算后向传播过程，先计算误差
        data_loss, dscores = layers.softmax_loss(scores, y)
        da2, dW3, db3 = layers.affine_backward(dscores, cache3)
        da1, dW2, db2 = layer_utils.affine_relu_backward(da2, cache2)
        dX, dW1, db1 = layer_utils.conv_relu_pool_backward(da1, cache1)

        #引入修正因子regularization ，重新计算损失，梯度
        dW1 += self.reg * W1
        dW2 += self.reg * W2
        dW3 += self.reg * W3
        reg_loss = 0.5 * self.reg * sum(np.sum(W * W) for W in [W1, W2, W3])

        loss = data_loss + reg_loss
        grads = {'W1': dW1, 'b1': db1, 'W2': dW2, 'b2': db2, 'W3': dW3, 'b3': db3}

        return loss, grads