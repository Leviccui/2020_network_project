from math import sqrt
import pandas as pd 
import sympy
import numpy as np 
import itertools

RSSI_threshold = 90


def distance_to_BS(rssi, a=54, n=4):
    """
    根据RSSI计算距离
    :param rssi:
    :param a: 距离发射器1m时的RSSI值，单位:-dbm，默认为42
    :param n: 衰减系数，默认为3.3
    :return:
    """
    return 10 ** ((abs(rssi) - a) / (10 * n)) if abs(rssi) < RSSI_threshold else None


def locate_by_pointlist(point_list: list): #两点定位
    """
    根据已知节点坐标和各自到未知节点的距离估计未知节点的位置
    :param point_list: [x, y ,distance]
    :return: 未知节点的坐标
    """
    x = 0
    y = 0
    temp_list = point_list.copy()
    for p in temp_list:
        if p[2] is None:
            point_list.remove(p)
    num = len(point_list)
    temp_list = point_list.copy()
    if num == 2:
        for p1 in point_list:
            temp_list.remove(p1)
            for p2 in temp_list:
                p2p = distance(p1, p2)
                dist_sum = p1[2] + p2[2]
                if dist_sum <= p2p:
                    x += p1[0] + (p2[0] - p1[0])*p1[2] / dist_sum
                    y += p1[1] + (p2[1] - p1[1])*p1[2] / dist_sum
                else:
                    dr = p2p / 2 + (p1[2]**2 - p2[2]**2) / (2 * p2p)
                    x += p1[0] + (p2[0] - p1[0])*dr / p2p
                    y += p1[1] + (p2[1] - p1[1])*dr / p2p
        #x /= num
        #y /= num
    elif num >=3:
        x, y = three_point(point_list)
    elif num == 1:
        x = point_list[0][0]
        y = point_list[0][1]
    # x /= (num*(num-1))/2
    # x /= (num*(num-1))/2
    return x, y


def distance(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def three_point(point_list: list): #三点定位
    temp_list = point_list.copy()
    for p in temp_list:
        if p[2] is None:
            point_list.remove(p)

    sumX=0.0
    sumY=0.0

    min=temp_list[0][2]
    min_p=temp_list[0]
    for p in temp_list:
        if(p[2]<min):
            min=p[2]
            min_p=p

    for p in temp_list:
        if(p==min_p):
            continue
        w=p[2]/(p[2]+min)
        x=min_p[0]*w+p[0]*(1-w)
        y=min_p[1]*w+p[1]*(1-w)
        sumX+=x
        sumY+=y

    return sumX/(len(temp_list)-1),sumY/(len(temp_list)-1)
    
    '''
    n=len(point_list)
    A=np.zeros((n-1,2))
    b=np.zeros((n-1,1))

    q=point_list[n-1]
    for i in range(n-1):
        p=point_list[i]

        A[i][0]=2*(p[0]-q[0])
        A[i][1]=2*(p[1]-q[1])
        b[i][0]=p[0]**2-q[0]**2+p[1]**2-q[1]**2+q[2]**2-p[2]**2

    A=np.matrix(A)
    b=np.matrix(b)

    X=A.T*A
    X=X.I
    X=X*A.T
    X=X*b

    return float(X[0][0]),float(X[1][0])

    num=0
    x=0
    y=0
    for item in itertools.combinations(point_list,3):
        locx,locy=triposition(item[0][0],item[0][1],item[0][2],item[1][0],item[1][1],item[1][2],item[2][0],item[2][1],item[2][2])
        x+=locx
        y+=locy
        num+=1
    x/=num
    y/=num
    return x,y
    '''


def triposition(xa,ya,da,xb,yb,db,xc,yc,dc): 
    x,y = sympy.symbols('x y')
    f1 = 2*x*(xa-xc)+np.square(xc)-np.square(xa)+2*y*(ya-yc)+np.square(yc)-np.square(ya)-(np.square(dc)-np.square(da))
    f2 = 2*x*(xb-xc)+np.square(xc)-np.square(xb)+2*y*(yb-yc)+np.square(yc)-np.square(yb)-(np.square(dc)-np.square(db))
    result = sympy.solve([f1,f2],[x,y])
    locx,locy = float(result[x]),float(result[y])
    return [locx,locy]

def err(x,y,gt):
    return sqrt((x-gt[0])**2+(y-gt[1])**2)

'''
if __name__ == "__main__":
    wifi = pd.read_csv('./data/toy data/wifi.csv')
    point = pd.read_csv('./data/toy data/point.csv')
    wifi_x=list(wifi['x'])
    wifi_y=list(wifi['y'])
    rssi=point.values[:,3:]
    gt=point.values[:,1:3]
    print(gt)
    #两点
    for p in range(len(point)):
        point_list=[]
        for i in range(len(wifi)):
            temp=[]
            temp.append(wifi_x[i])
            temp.append(wifi_y[i])
            temp.append(distance_to_BS(rssi[p][i]))
            point_list.append(temp)
        
        x_2,y_2 = locate_by_pointlist(point_list)
        x_3,y_3 = three_point(point_list)
        print(x_2,y_2,err(x_2,y_2,gt[p]))
        print(x_3,y_3,err(x_3,y_3,gt[p]))
'''