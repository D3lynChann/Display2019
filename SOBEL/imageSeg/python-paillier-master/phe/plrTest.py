from paillier import *
from time import time
from util import *
import random
from damgard_jurik import keygen

initP1024 = 12487210913669987076526020022976573194319993993938252811898710142157989090511036069867469640339577134874850216109999644669109610468775603453160589565121637
initQ1024 = 10727087481820311139845870783035236841841366041752215236488534771730036991602720006434662374951629717830061790530004004422493013233346257615261398282277671
initN1024 = 133951403874879288352122483001559857565280621564475778505227398182729334088341727812710026365803652340450454878523789586144889214357742196131425935096471750889062538726065404508719390940507461465173347080962843944263960782220545393654002254877547899300432385898146514248586138285080162381388232097964524067427
initNN1024 = initN1024 * initN1024

initP2048 = 142771884146716563507042201149688900594663109365515913888304654209499259567179777344199627574338382271941618669627867893167662348949574464430111278579880566915070493955836899370768821799823799449424466305281797266799181298536904422644124892169858644585341019352652890609876772612620780508033370615879697109053
initQ2048 = 113444369271967446525934593589084658339568920358652561879293463472686261811741539518093814378734374042025149474568020197679770150141191508802382770511871421863661661187634923414766327954758239627408603161766435475813443521279301039585541865880292067026286260240282018427581793540534174374551856106498680234931
initN2048 = 16196666346794668735983895493355857042664371088065516991529707138218158897533917578638765603272864011075998418861350818206623704900112833231971778564299335966758947790316025091137700366196781000346538471944520018242572206778854277267446282495366274515064311721884244161224995752966552775642106745616674499962155390821538329942452349102517840849322385645648369400624000118798276672340777853490833242686802276240312474727472165860624278557926474017575989897863895185025523090045156585124639322434066058831954060852485906555161213843101316122788819230758260724502536309944274655948037685650854210398125441193671566930343
initNN2048 = initN2048 * initN2048

def getGen1024Time():
    #生成一个1024位的(r**n)%(n**2)的平均时间
    totalTime = 0
    for ctr in range(100):
        r = random.randint(1, initN1024)
        start = time()
        r = powmod(r, initN1024, initNN1024)
        end = time()
        totalTime += end - start
    return totalTime / 100
    
def getGen2048Time():
    #生成一个2048位的(r**n)%(n**2)的平均时间
    totalTime = 0
    for ctr in range(100):
        r = random.randint(1, initN2048)
        start = time()
        r = powmod(r, initN2048, initNN2048)
        end = time()
        totalTime += end - start
    return totalTime / 100

def BobGenerateCsAndS(d_hat_e, r_hat, r_hat_e, one_e, zero_e, pk):
    #if s == 1: no 0 in c if d > r
    w_e = []; l = len(d_hat_e)
    
    #w = d XOR r
    for ctr in range(len(r_hat)):
        if r_hat[ctr] == 0:
            w_e.append(d_hat_e[ctr])
        else:
            w_e.append(one_e - d_hat_e[ctr])
    
    #sum^{l - 1}_{j = i + 1}{w_j}
    sum_w_e = [None for ctr in range(l)]
    sum_w_e[l - 1] = zero_e
    for ctr in range(l - 2, -1, -1):
        sum_w_e[ctr] = sum_w_e[ctr + 1] + w_e[ctr + 1]
    
    #s in {-1, 1}    
    s = 1 if random.randint(0, 100) % 2 else -1
    s_e = pk.encrypt(s)
    
    #c = d - r + s + 3*sum_w
    c_e = []
    for ctr in range(l):
        r = random.randint(0, 1024)
        c_e.append(r * (d_hat_e[ctr] - r_hat_e[ctr] + s_e + (3 * sum_w_e[ctr])))
        
    return c_e, s
    
def AliceDecryptCs(sk, c_e, one_e, zero_e):
    #if there is a 0 in c_e, return [1]
    for item in c_e:
        if int(sk.decrypt(item)) == 0:
            return zero_e
    return one_e

def BobGetTheRes(s, lamda_e, one_e):
    return one_e - lamda_e if s == -1 else lamda_e
    
if __name__ == '__main__':
    pk0, sk0 = generate_paillier_keypair_1(initP1024, initQ1024)
    one_e0 = pk0.encrypt(1); zero_e0 = pk0.encrypt(0)
    
    pk, sk = keygen(n_bits = 64)
    one_e = pk.encrypt(1); zero_e = pk.encrypt(0)
    #from left to right
    d_hat = [0, 1, 1, 0, 1, 1, 1, 1]
    r_hat = [1, 0, 1, 1, 0, 0, 0, 1]
    
    d_hat_e = [pk.encrypt(item) for item in d_hat]
    r_hat_e = [pk.encrypt(item) for item in r_hat]
    
    start = time()
    c_e, s = BobGenerateCsAndS(d_hat_e, r_hat, r_hat_e, one_e, zero_e, pk)
    end = time()
    
    print('c_i:')
    for item in c_e:
        print(int(sk.decrypt(item)), end = '\t')
    print('\ns:', s)    
    print('time:', end - start)  
    
    start = time()
    lamda_e = AliceDecryptCs(sk, c_e, one_e0, zero_e0)
    end = time()
    print('lamda:', sk0.decrypt(lamda_e))
    print('time:', end - start)
    
    start = time()
    res = BobGetTheRes(s, lamda_e, one_e0)
    end = time()
    print(sk0.decrypt(res))
    print('time:', end - start)    
    
    #is tpppp
    '''
    a = pk.encrypt(1234)
    b = pk.encrypt(2345)
    r = 12344567836
    start = time()
    c = a - b
    r = c * r
    print(sk.decrypt(r))
    end = time()
    print(end - start)
    '''
