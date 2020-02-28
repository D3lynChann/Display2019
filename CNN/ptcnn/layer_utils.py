# -*- coding: utf-8 -*-
try:
    from . import layers
except Exception:
    import layers
  
# 这layer_utils是整合了layers中的操作

# 第一层，卷积加激活加池化，conv_param, pool_param等参数在cnn处给出
# 形如a1, cache1 = layer_utils.conv_relu_pool_forward(X, W1, b1, conv_param, pool_param)
# 输入为 x：输入数据，b和conv_param：权重以及卷积参数，layerpool_param：池化参数
# 输出为 out：池化层的输出，cache：用于后向传播的object
def conv_relu_pool_forward(x, w, b, conv_param, pool_param):
    # 前向的卷积
    a, conv_cache = layers.conv_forward_naive(x, w, b, conv_param)
    # 前向的relu
    s, relu_cache = layers.relu_forward(a)
    # 前向的池化
    out, pool_cache = layers.max_pool_forward_naive(s, pool_param)
    # 打包结果
    cache = (conv_cache, relu_cache, pool_cache)
    return out, cache

# 为全连接加激活函数，其中x为输入，w和b是权重
def affine_relu_forward(x, w, b):
    # 前向的全连接
    a, fc_cache = layers.affine_forward(x, w, b)
    # 前向的relu
    out, relu_cache = layers.relu_forward(a)
    cache = (fc_cache, relu_cache)
    return out, cache

# 后向传输的三个层次
def affine_relu_backward(dout, cache):
    """
    Backward pass for the affine-relu convenience layer
    """
    fc_cache, relu_cache = cache
    da = layers.relu_backward(dout, relu_cache)
    dx, dw, db = layers.affine_backward(da, fc_cache)
    return dx, dw, db

def conv_relu_backward(dout, cache):
    """
    Backward pass for the conv-relu convenience layer.
    """
    conv_cache, relu_cache = cache
    da = layers.relu_backward(dout, relu_cache)
    dx, dw, db = layers.conv_backward_fast(da, conv_cache)
    return dx, dw, db

def conv_relu_pool_backward(dout, cache):
    """
    Backward pass for the conv-relu-pool convenience layer
    """
    conv_cache, relu_cache, pool_cache = cache
    ds = layers.max_pool_backward_naive(dout, pool_cache)
    da = layers.relu_backward(ds, relu_cache)
    dx, dw, db = layers.conv_backward_naive(da, conv_cache)
    return dx, dw, db
  
pass