import ReadAndWriteImage, copy, math

def getGrayData(fileName):
    return ReadAndWriteImage.color2matrix(fileName)
    
def getImage(data, fileName):
    ReadAndWriteImage.matrix2img(data, fileName)
    print('finish')
    
def GaussianIt(data, div = False):
    h = len(data); w = len(data[0])
    filter = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
    res = copy.deepcopy(data)
    for ctr in range(1, h - 1):
        for itr in range(1, w - 1):
            tempSum = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    tempSum += filter[i + 1][j + 1] * data[ctr][itr]
            res[ctr][itr] = tempSum
    if div == True:
        for ctr in range(1, h - 1):
            for itr in range(1, w - 1):
                res[ctr][itr] = res[ctr][itr] // 16
    return res            

def SobelIt(data):
    h = len(data); w = len(data[0])
    Gxs = [[0 for ctr in range(w)] for itr in range(h)]
    Gs = copy.deepcopy(data); Gys = copy.deepcopy(Gxs); tangs = copy.deepcopy(Gxs)
    for ctr in range(1, h - 1):
        for itr in range(1, w - 1):
            Gxs[ctr][itr] = data[ctr - 1][itr + 1] + 2 * data[ctr][itr + 1] + data[ctr + 1][itr + 1] - (data[ctr - 1][itr - 1] + 2 * data[ctr][itr - 1] + data[ctr + 1][itr - 1])
            Gys[ctr][itr] = data[ctr - 1][itr - 1] + 2 * data[ctr - 1][itr] + data[ctr - 1][itr + 1] - (data[ctr + 1][itr - 1] + 2 * data[ctr + 1][itr] + data[ctr + 1][itr + 1])
            Gs[ctr][itr] = abs(Gxs[ctr][itr] - Gys[ctr][itr])
    return Gxs, Gys, Gs       

def NMSuppress(Gxs, Gys, Gs):
    h = len(Gs); w = len(Gs[0])
    res = copy.deepcopy(Gs)
    for ctr in range(1, h - 1):
        for itr in range(1, 639):
            if Gs[ctr][itr] != 0:
                dx = Gxs[ctr][itr]; dy = Gys[ctr][itr]
                d = Gs[ctr][itr]
                if abs(dy) > abs(dx):
                    w = abs(dx) / abs(dy)
                    d2 = Gs[ctr - 1][itr]
                    d4 = Gs[ctr + 1][itr]
                    if dx * dy > 0:
                        d1 = Gs[ctr - 1][itr - 1]
                        d3 = Gs[ctr + 1][itr + 1]
                    else:
                        d1 = Gs[ctr - 1][itr + 1]
                        d3 = Gs[ctr + 1][itr - 1]
                else:
                    w = abs(dy) / abs(dx)
                    d2 = Gs[ctr][itr - 1]
                    d4 = Gs[ctr][itr + 1]
                    if dx * dy > 0:
                        d1 = Gs[ctr + 1][itr - 1]
                        d3 = Gs[ctr - 1][itr + 1]
                    else:
                        d1 = Gs[ctr - 1][itr - 1]
                        d3 = Gs[ctr + 1][itr + 1]
                gt1 = w * d1 + (1 - w) * d2
                gt2 = w * d3 + (1 - w) * d4
                if d >= gt1 and d >= gt2:
                    res[ctr][itr] = d
                else:
                    res[ctr][itr] = 0
    return res       
    
def doubThres(matrix):
    h = len(Gs); w = len(Gs[0])
    res = [[0 for ctr in range(w)] for itr in range(h)]
    maxP = 0
    for ctr in range(1, h - 1):
        for itr in range(1, w - 1):
            if matrix[ctr][itr] > max:
                maxP = matrix[ctr][itr]
    thres1 = 0.1 * maxP; thres2 = 0.3 * maxP
    for ctr in range(1, h - 1):
        for itr in range(1, w - 1):
            if matrix[ctr][itr] > thres2:
                res[ctr][itr] = 2
            elif matrix[ctr][itr] <= thres2 and matrix[ctr][itr] > thres1:
                res[ctr][itr] = 1
    return res

def connEdge(matrix):
    h = len(Gs); w = len(Gs[0])
    res = copy.deepcopy(matrix)
    for ctr in range(1, h - 1):
        for itr in range(1, w - 1):
            if matrix[ctr][itr] == 1:
                tempFlag = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if matrix[ctr + i][itr + j] == 2:
                            tempFlag = 2
                res[ctr][itr] = tempflag            
    return res
    
if __name__ == '__main__':
    data = getGrayData('G:/codes/HOUGH/FIG/9.jpg')
    Gres = GaussianIt(data, True)
    getImage(Gres, 'G:/codes/HOUGH/CLEARHOUGH/1.bmp')
    Gxs, Gys, Sres = SobelIt(Gres)
    getImage(Sres, 'G:/codes/HOUGH/CLEARHOUGH/2.bmp')
    NMSres = NMSuppress(Gxs, Gys, Sres)
    getImage(NMSres, 'G:/codes/HOUGH/CLEARHOUGH/3.bmp')