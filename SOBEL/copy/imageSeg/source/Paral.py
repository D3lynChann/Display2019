from threading import Thread
from time import sleep
import math

li = [[1,2,3,4,5,6,7,8,9,10,11,12],[13,14,15,16,17,18,19,20,21,22,23,24],[25,26,27,28,29,30,31,32,33,34,35,36],[37,38,39,40,41,42,43,44,45,46,47,48],[49,50,51,52,53,54,55,56,57,58,59,60],[61,62,63,64,65,66,67,68,69,70,71,72],[73,74,75,76,77,78,79,80,81,82,83,84],[85,86,87,88,89,90,91,92,93,94,95,96],[97,98,99,100,101,102,103,104,105,106,107,108],[109,110,111,112,113,114,115,116,117,118,119,120]]

def divMis(matrix, px = 2, py = 2):
    sizx = len(matrix) // px; sizy = len(matrix[0]) // py
    res = []; res0 = []
    for ctr in range(px):
        res.append(matrix[ctr * sizx: (ctr + 1) * sizx])
    for ctr in range(px):
        for itr in range(py):
            temp = []
            for lines in res[ctr]:
                temp.append(lines[itr * sizy: (itr + 1) * sizy])
            res0.append(temp) 
    return res0            

def carryMis(matrixs, px = 2, py = 2):
    hig = len(matrixs[0])
    res = []
    tempRes = []; ctr = 0
    while ctr < px:
        tempRes.append(matrixs[ctr * py: (ctr + 1) * py])
        ctr += 1 
    for matr in tempRes:    
        for ctr in range(hig):
            for itr in range(py - 1):
                matr[0][ctr].extend(matr[itr + 1][ctr])
            res.append(matr[0][ctr])        
    return res 
    
def palIt(func, argTuList, threads):
    for argTu in argTuList:
        thread = Thread(target = func, args = argTu)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    res = []
    for ctr in range(len(argTuList)):      
        res.append(argTuList[-1][-1][ctr])
    return res    
    
def T(matrix, num, ress):
    sleep(2)
    ress[num] = matrix

def test():
    threads = []; res = {}; argTuList = []
    res0 = divMis(li, 5, 4)  
    for i in range(20):
        argTuList.append((res0[i], i, res))
    rez = palIt(T, argTuList, threads)     
    res1 = carryMis(rez, 5, 4) 
    print(res1)
    