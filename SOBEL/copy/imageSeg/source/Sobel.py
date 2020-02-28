from plr import *
import DataPacking
G_Y = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
G_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]

def SobelIt(matrix):
    assert type(matrix).__name__ == 'list'
    res = [[] for i in range(len(matrix))]
    res[0] = matrix[0][:]
    res[-1] = matrix[-1][:]
    for i in range(1, len(matrix) - 1):
        res[i].append(matrix[i][0])
        for j in range(1, len(matrix[0]) - 1):
            A_x = (matrix[i - 1][j + 1] + 2 * matrix[i][j + 1] + matrix[i + 1][j + 1]) - (matrix[i - 1][j - 1] + 2 * matrix[i][j - 1] + matrix[i + 1][j - 1])
            A_y = (matrix[i - 1][j - 1] + 2 * matrix[i - 1][j] + matrix[i - 1][j + 1]) - (matrix[i + 1][j - 1] + 2 * matrix[i + 1][j] + matrix[i + 1][j + 1])
            res[i].append(abs(A_x) + abs(A_y))
        res[i].append(matrix[i][-1])         
    return res    

def SobelItWithPlrAndPack(matrix, pk, sk, l, L):
    '''
    打包加密数据的Sobel算子，利用到减法绝对值哈
    '''
    assert type(matrix).__name__ == 'list'
    res = [[] for i in range(len(matrix))]
    res[0] = matrix[0][:]
    res[-1] = matrix[-1][:]
    for i in range(1, len(matrix) - 1):
        res[i].append(matrix[i][0])
        for j in range(1, len(matrix[0]) - 1):
            A_x = DataPacking.SubAbsForPack(addListCipher([matrix[i - 1][j + 1], mulClear(matrix[i][j + 1], 2), matrix[i + 1][j + 1]]), addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i][j - 1], 2), matrix[i + 1][j - 1]]), pk, sk, l, L)
            A_y = DataPacking.SubAbsForPack(addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i - 1][j], 2), matrix[i - 1][j + 1]]), addListCipher([matrix[i + 1][j - 1], mulClear(matrix[i + 1][j], 2), matrix[i + 1][j + 1]]), pk, sk, l, L)
            
            res[i].append(addCipher(A_x, A_y))
        res[i].append(matrix[i][-1])         
    return res 

def SobelItWithPlr(matrix, pk, sk):
    assert type(matrix).__name__ == 'list'
    res = [[] for i in range(len(matrix))]
    res[0] = matrix[0][:]
    res[-1] = matrix[-1][:]
    for i in range(1, len(matrix) - 1):
        res[i].append(matrix[i][0])
        for j in range(1, len(matrix[0]) - 1):
            A_x = subCipher(addListCipher([matrix[i - 1][j + 1], mulClear(matrix[i][j + 1], 2), matrix[i + 1][j + 1]]), addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i][j - 1], 2), matrix[i + 1][j - 1]]))
            A_y = subCipher(addListCipher([matrix[i - 1][j - 1], mulClear(matrix[i - 1][j], 2), matrix[i - 1][j + 1]]), addListCipher([matrix[i + 1][j - 1], mulClear(matrix[i + 1][j], 2), matrix[i + 1][j + 1]]))
            
            res[i].append(addCipher(absProtocol(A_x, pk, sk), absProtocol(A_y, pk, sk)))
        res[i].append(matrix[i][-1])         
    return res 