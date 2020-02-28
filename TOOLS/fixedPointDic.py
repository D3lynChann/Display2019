from phe import *
from math import log
import GCutils
# 加密版本
class FPD:
    def __init__(self, pt, nums, pk):
        '''
        pt已知，nums保持密文
        '''
        self.pt = pt
        self.nums = nums
        self.pk = pk
        
    def show(self, sk):
        '''
        返回明文的小数
        '''
        return sk.decrypt(self.nums) / pow(10, self.pt)
        
    def truncate(self, pt, sk):
        '''
        截斷小數，截断为pt位的小数
        '''
        return FPD(pt, GCutils.divClear(self.nums, pow(10, self.pt - pt), self.pk, sk), self.pk)
        
    def __add__(self, other):
        '''
        加法，直接利用phe的加法
        '''
        return FPD(self.pt, self.nums + other.nums, self.pk)
        
    def __sub__(self, other):
        '''
        减法，直接利用phe的减法
        '''
        return FPD(self.pt, self.nums - other.nums, self.pk)
        
    def __mul__(self, other):
        '''
        乘明文整数，直接利用phe的明文乘法
        '''
        if type(other).__name__ != 'int':
            raise Exception("Not an integer!", other)
        return FPD(self.pt, self.nums * other, self.pk)
        
    def divClear(self, other, sk):
        '''
        按比例缩小，需要用到sk
        '''
        return FPD(self.pt, GCutils.divClear(self.nums, other, self.pk, sk), self.pk)

if __name__ == '__main__':
    pk, sk = generate_paillier_keypair(n_length = 1024)
    a = FPD(4, pk.encrypt(11231245), pk)
    print(a.show(sk))
    print((a * 314).show(sk))
    print((a * 314).divClear(100, sk).show(sk))