from plr import *
import random
import ReadAndWriteImage 

def firstPass(matrix):
    h = len(matrix); w = len(matrix[0]); cur = 0; sts = []; te = 0
    labels = [[0 for ctr in range(w)] for itr in range(h)]
    for ctr in range(1, h):
        for itr in range(1, w):
            if matrix[ctr][itr] != 0:
                left = matrix[ctr][itr - 1]; up = matrix[ctr - 1][itr]
                if left == up == 0:
                    cur += 1
                    labels[ctr][itr] = cur
                elif left == 0 and up != 0:
                    labels[ctr][itr] = labels[ctr - 1][itr]
                elif left != 0 and up == 0: 
                    labels[ctr][itr] = labels[ctr][itr - 1]
                else:
                    te += 1
                    minL = min(labels[ctr - 1][itr], labels[ctr][itr - 1])
                    maxL = max(labels[ctr - 1][itr], labels[ctr][itr - 1])
                    labels[ctr][itr] = minL
                    if minL != maxL:
                        sts.append((minL, maxL))
    print('cur:', cur)
    print('test:', te)
    return labels, sts, cur        

def secondPass(sts, cur, matrix):
    dads = [ctr for ctr in range(cur + 1)]
    for pair in sts:
        dads[pair[1]] = pair[0]
    for ctr in range(cur + 1):
        while dads[dads[ctr]] != dads[ctr]:
            dads[ctr] = dads[dads[ctr]]
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[0])):
            matrix[ctr][itr] = dads[matrix[ctr][itr]]
    print('dads:', dads)        
    return matrix
    
def thirdPass(minNum, matrix, cur):
    colors = [random.randint(127, 255) for ctr in range(cur)]
    dic = {}
    for line in matrix:
        for pix in line:
            if pix in dic.keys():
                dic[pix] += 1
            else:
                dic[pix] = 1
    for ctr in range(len(matrix)):
        for itr in range(len(matrix[0])):
            if dic[matrix[ctr][itr]] <= minNum:
                matrix[ctr][itr] = 0
            if matrix[ctr][itr] > 0:
                matrix[ctr][itr] = colors[matrix[ctr][itr]]
    return matrix
     
def findDadWithPlr(inputLabel, sk):
    '''
        inputLable is encrypted
        return an encrypted label
    '''
    global countPlr, dadsPlr, numsOfConnectedAreaPlr
    tempInput = decrypt(inputLabel, sk)
    tempDad = dadsPlr[tempInput]
    if compProtocol(dadsPlr[decrypt(tempDad, sk)], tempDad, sk) == 0:
        return tempDad
    else:
        dadsPlr[tempInput] = findDadWithPlr(tempDad, sk)
        return dadsPlr[tempInput]        
         
def twoPassWithPlr(matrix, mask, area, pk, sk):
    global countPlr, dadsPlr, numsOfConnectedAreaPlr
    h = len(matrix); w = len(matrix[0])
    
    dadsPlr = [encrypt(ctr, pk) for ctr in range(h * w)]
    tempOne = encrypt(1, pk); tempZero = encrypt(0, pk)
    numsOfConnectedAreaPlr = [tempOne for ctr in range(h * w)]
    dx = [0, 0, -1, 1]
    dy = [-1, 1, 0, 0]
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            if compProtocol(matrix[i][j], mask, sk) == 0:
                for dir in range(4):
                    nx = dx[dir] + i
                    ny = dy[dir] + j
                    if nx >= 0 and nx < h and ny >= 0 and ny < w and compProtocol(matrix[nx][ny], mask, sk) == 0:
                        a = encrypt(i * w + j, pk)
                        b = encrypt(nx * w + ny, pk)
                        pa = findDadWithPlr(a, sk)
                        pb = findDadWithPlr(b, sk)
                        tempPa = decrypt(pa, sk); tempPb = decrypt(pb, sk)
                        tempAdd = addCipher(numsOfConnectedAreaPlr[tempPa], numsOfConnectedAreaPlr[tempPb])
                        if compProtocol(pa, pb, sk) == -1:
                            dadsPlr[decrypt(pb, sk)] = pa
                            numsOfConnectedAreaPlr[tempPa] = tempAdd
                            numsOfConnectedAreaPlr[tempPb] = tempZero
                        elif compProtocol(pa, pb, sk) == 1:
                            dadsPlr[decrypt(pa, sk)] = pb
                            numsOfConnectedAreaPlr[tempPb] = tempAdd
                            numsOfConnectedAreaPlr[tempPa] = tempZero
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            if compProtocol(matrix[i][j], mask, sk) == 0:
                a = encrypt(i * w + j, pk)
                findDadWithPlr(a, sk)

    countPlr = tempZero
    res = [[tempZero for ctr in range(w)] for itr in range(h)]
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            if compProtocol(matrix[i][j], mask, sk) == 0:
                a = encrypt(i * w + j, pk)
                pa = findDadWithPlr(a, sk)
                if compProtocol(numsOfConnectedAreaPlr[decrypt(pa, sk)], area, sk) >= 0:
                    pa_i = decrypt(pa, sk) // w
                    pa_j = decrypt(pa, sk) % w
                    if compProtocol(res[pa_i][pa_j], tempZero, sk) == 0:
                        res[pa_i][pa_j] = encrypt(random.randint(0, 256), pk)
                        countPlr = addCipher(countPlr, tempOne)
                    res[i][j] = res[pa_i][pa_j]
    return countPlr, res

def test():
    m = ReadAndWriteImage.color2matrix('pic/testOutPut06171039.bmp')
    res, sts, cur = firstPass(m)
    res = secondPass(sts, cur, res)
    res = thirdPass(10, res, cur)  
    ReadAndWriteImage.matrix2img(res, 'pic/testOutPut07031046.bmp')
        
if __name__ == '__main__':
    test()