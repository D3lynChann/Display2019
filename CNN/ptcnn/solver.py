import numpy as np
try:
  from . import optim
except Exception:
  import optim

class Solver(object):

    # 使用样例：
    # Solver(model, data, lr_decay=0.95, print_every=10, num_epochs=5, batch_size=2, update_rule='sgd_momentum',
    # optim_config={'learning_rate': 5e-4, 'momentum': 0.9})
    # 其中model为一个cnn对象，包含参数等
    # data则是一个字典，包含四项：X_train、X_val、y_train和y_val
    # 关于可选参数**kwargs，主要是update_rule（来自optim中的方法）、optim_config（关于获取的update_rule的参数设置）、
    # lr_decay（学习率的变化幅度，每次轮回之后学习率乘以这个）、num_opochs（训练过程中的轮回数）、
    # batch_size（minibatch的大小）、print_every（每隔多少次循环打印一次）、verbose（真值，是否打印）
    def __init__(self, model, data, **kwargs):
        self.model = model
        self.X_train = data['X_train']
        self.y_train = data['y_train']
        self.X_val = data['X_val']
        self.y_val = data['y_val']
        
        # 在设置参数，如果为空则初始化
        self.update_rule = kwargs.pop('update_rule', 'sgd')
        self.optim_config = kwargs.pop('optim_config', {})
        self.lr_decay = kwargs.pop('lr_decay', 1.0)
        self.batch_size = kwargs.pop('batch_size', 2)
        self.num_epochs = kwargs.pop('num_epochs', 10)
        self.print_every = kwargs.pop('print_every', 10)
        self.verbose = kwargs.pop('verbose', True)

        # 删除kwargs中参数后，校验是否还有多余参数
        if len(kwargs) > 0:
            extra = ', '.join('"%s"' % k for k in kwargs.keys())
            raise ValueError('Unrecognized arguments %s' % extra)

        # 检查optim对象中是否有属性或方法名为self.update_rule
        if not hasattr(optim, self.update_rule):
            raise ValueError('Invalid update_rule "%s"' % self.update_rule)
        self.update_rule = getattr(optim, self.update_rule)
        self._reset()


    def _reset(self):
        """
        Set up some book-keeping variables for optimization. Don't call this
        manually.
        """
        # Set up some variables for book-keeping
        self.epoch = 0
        self.best_val_acc = 0
        self.best_params = {}
        self.loss_history = []
        self.train_acc_history = []
        self.val_acc_history = []

        # Make a deep copy of the optim_config for each parameter
        self.optim_configs = {}
        for p in self.model.params:
            d = {k: v for k, v in self.optim_config.items()}
            self.optim_configs[p] = d


    def _step(self):
        """
        Make a single gradient update. This is called by train() and should not
        be called manually.
        """
        # Make a minibatch of training data
        # 500 张图片
        num_train = self.X_train.shape[0]
        # 随机选出batch_size：2 张
        batch_mask = np.random.choice(num_train, self.batch_size)

        # batch_mask = [t%(num_train//2), num_train//2 + t%(num_train//2)]
        # 训练样本矩阵[2,3,32,32]
        X_batch = self.X_train[batch_mask]
        # 标签矩阵[2,] 图片类型
        y_batch = self.y_train[batch_mask]

        # Compute loss and gradient
        loss, grads = self.model.loss(X_batch, y_batch)
        self.loss_history.append(loss)

        # 更新模型超参(w1,b1),(w2,b2),(w3,b3)，以及保存更新超参时对应参数因子
        # Perform a parameter update
        for p, w in self.model.params.items():
            dw = grads[p]
            config = self.optim_configs[p]
            next_w, next_config = self.update_rule(w, dw, config)
            self.model.params[p] = next_w
            # 保存参数因子，learning_rate(学习率)，velocity(速度)
            self.optim_configs[p] = next_config


    def check_accuracy(self, X, y, num_samples=None, batch_size=2):
        """
        Check accuracy of the model on the provided data.
        
        Inputs:
        - X: Array of data, of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,)
        - num_samples: If not None, subsample the data and only test the model
          on num_samples datapoints.
        - batch_size: Split X and y into batches of this size to avoid using too
          much memory.
          
        Returns:
        - acc: Scalar giving the fraction of instances that were correctly
          classified by the model.
        """
        
        # Maybe subsample the data
        N = X.shape[0]
        if num_samples is not None and N > num_samples:
            # 随机选取num_samples张图片，返回选取图片索引
            mask = np.random.choice(N, num_samples)
            N = num_samples
            X = X[mask]
            y = y[mask]

        # Compute predictions in batches
        num_batches = N // batch_size
        if N % batch_size != 0:
            num_batches += 1
        y_pred = []
        for i in range(num_batches):
            start = i * batch_size
            end = (i + 1) * batch_size
            # 这里调用了cnn的loss函数
            scores = self.model.loss(X[start:end])
            y_pred.append(np.argmax(scores, axis=1))
        y_pred = np.hstack(y_pred)
        acc = np.mean(y_pred == y)
        return acc

    '''
    训练模型：核心方法
    epoch > batch_size > iteration >= 1
    训练总的次数 = num_epochs * iterations_per_epoch
    '''
    def train(self):
        """
        Run optimization to train the model.
        """
        num_train = self.X_train.shape[0]
        iterations_per_epoch = max(num_train // self.batch_size, 1)
        num_iterations = self.num_epochs * iterations_per_epoch
        # 迭代总的次数
        for t in range(num_iterations):
            # 某次iteration训练
            self._step()

            # Maybe print training loss
            # verbose：是否显示详细信息
            if self.verbose and t % self.print_every == 0:
                print ('(Iteration %d / %d) loss: %f' % (t + 1, num_iterations, self.loss_history[-1]))

            # At the end of every epoch, increment the epoch counter and decay the
            # learning rate.
            # 每迭代完一次epoch后，更新学习率learning_rate，加快运算效率。
            epoch_end = (t + 1) % iterations_per_epoch == 0
            if epoch_end:
                self.epoch += 1
                for k in self.optim_configs:
                    self.optim_configs[k]['learning_rate'] *= self.lr_decay

            # Check train and val accuracy on the first iteration, the last
            # iteration, and at the end of each epoch.
            # 在第1次迭代，最后1次迭代，或者运行完一个epoch后，校验训练结果。
            first_it = (t == 0)
            last_it = (t == num_iterations + 1)
            if first_it or last_it or epoch_end:
                train_acc = self.check_accuracy(self.X_train, self.y_train, num_samples=4)
                val_acc = self.check_accuracy(self.X_val, self.y_val, num_samples=4)
                self.train_acc_history.append(train_acc)
                self.val_acc_history.append(val_acc)
        
                if self.verbose:
                    print ('(Epoch %d / %d) train acc: %f; val_acc: %f' % (
                         self.epoch, self.num_epochs, train_acc, val_acc))

                # Keep track of the best model
                if val_acc > self.best_val_acc:
                    self.best_val_acc = val_acc
                    self.best_params = {}
                    for k, v in self.model.params.items():
                        self.best_params[k] = v.copy()

        # At the end of training swap the best params into the model
        self.model.params = self.best_params