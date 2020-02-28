from phe import *

Pai = 3.1415926535
angles_old = ['0.78539816339745', '0.46364760900081', '0.24497866312686', '0.12435499454676', '0.06241880999596','0.03123983343027', '0.01562372862048', '0.00781234106010', '0.00390623013197', '0.00195312251648', '0.00097656218956', '0.00048828121119', '0.00024414062015', '0.00012207031189', '0.00006103515617', '0.00003051757812', '0.00001525878906', '0.00000762939453', '0.00000381469727', '0.00000190734863', '0.00000095367432','0.00000047683716', '0.00000023841858', '0.00000011920929','0.00000005960464', '0.00000002980232', '0.00000001490116', '0.00000000745058']
angles = [int(float(i) * pow(10, 14)) for i in angles_old]

def refAngle(theta):
    while theta >= 360 or theta < 0:
        if theta >= 360:
            theta = theta - 360
        elif theta < 0:
            theta = theta + 360
    return theta    

def deal(yaw):
    if yaw < 0:
        return -(abs(yaw)/Pai)*180
    else:
        return (abs(yaw)/Pai)*180
        
def cordicIt(input):
    ref = refAngle(int(input))

    if ref <= 90 and ref >= 0:
        ref = refAngle(int(ref))
        Quad = 1
    elif ref <= 180 and ref > 90:
        ref = 180 - refAngle(int(ref))
        Quad = 2
    elif ref <= 270 and ref > 180:
        ref = refAngle(int(ref)) - 180
        Quad = 3
    elif ref <= 360 and ref > 270:
        Quad = 4
        ref = 360 - refAngle(int(ref))

    Vxnew = 1
    Vynew = 0
    K =  0.60725293500888
    theta = 0

    #iterations
    for n in range(len(angles)):
        if int(ref) > theta:
            Vx = Vxnew - ((1 / 2 ** n) * Vynew)
            Vy = ((1 / 2 ** n) * Vxnew) + Vynew
            Vxnew = Vx
            Vynew = Vy
            theta = theta + (deal(angles[n]))
        else:
            Vx = Vxnew + ((1 / 2 ** n) * Vynew)
            Vy = (-(1 / 2 ** n) * Vxnew) + Vynew
            Vxnew = Vx
            Vynew = Vy
            theta = theta - (deal(angles[n]))
    cosx = Vxnew * K
    sinx = Vynew * K

    if int(Quad) == 1:
        cosx = cosx
        sinx = sinx
    elif int(Quad) == 2:
        cosx = cosx * -1
    elif int(Quad) == 3:
        cosx = cosx * -1
        sinx = sinx * -1
    elif int(Quad) == 4:
        sinx = sinx * -1


    print("cosx: " + str(cosx))
    print("sinx: " + str(sinx)) 

print(angles)
#cordicIt(60)    