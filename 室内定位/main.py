import xlrd
import xlwt
import numpy as np
import datetime
import time
import matplotlib.pyplot as plt
from locate2and3points import distance_to_BS, locate_by_pointlist, distance
from pf import create_particles, run_pf


gateway = [[], [22, 6.41], [22.62, 22.59], [41, 17.4], [31.875, 2.29], [8.35, 22.59],[6.15,3.39]]
time_window = 1  # min


def read_data(file_path):
    wb = xlrd.open_workbook(file_path)
    sheet_list = wb.sheet_names()
    print(sheet_list)
    devicelogs = {}
    for i in range(len(sheet_list)):
        sheet = wb.sheet_by_name(sheet_list[i])
        nrows = sheet.nrows
        log_list = []
        for j in range(1,nrows):
            temp = []
            temp.append(float(sheet.cell(j, 3).value))
            temp.append(int(sheet.cell(j, 6).value))
            temp.append(xlrd.xldate.xldate_as_datetime(sheet.cell(j, 9).value, 0))
            log_list.append(temp)
        devicelogs[sheet_list[i]] = log_list
    return devicelogs  # {'device_name' = [[rssi, gateway_id, datetime],...]}


def process_data(raw_list: list): # [[rssi, gateway_id, datetime],...]
    now_date = raw_list[0][2]
    now_date = now_date - datetime.timedelta(seconds = now_date.second)
    result = {}
    temp = []

    for x in raw_list:
        # 按分钟计时，根据time_window分割数据
        if (x[2] - now_date).seconds < time_window*60:
            t = [x[1],x[0]]
            if t not in temp:
                temp.append(t)
        else:
            # 消除重复网关
            temp = eliminate_duplicates(temp)
            # 转化格式
            for i in range(len(temp)):
                temp[i] = [gateway[temp[i][0]][0],gateway[temp[i][0]][1], distance_to_BS(temp[i][1])]
            result[now_date] = temp

            now_date = x[2]-datetime.timedelta(seconds = x[2].second)
            temp = [[x[1], x[0]]]
    
    temp = eliminate_duplicates(temp)
     # 转化格式
    for i in range(len(temp)):
        temp[i] = [gateway[temp[i][0]][0],gateway[temp[i][0]][1], distance_to_BS(temp[i][1])]
    result[now_date] = temp

    return result  # {datetime:[[gateway_x, gateway_y, distance],...]}


def eliminate_duplicates(temp_l):
    count = {}
    result = []
    for x in temp_l:
        if x[0] not in count:
            count[x[0]] = [x[1]]
        else:
            count[x[0]].append(x[1])
    for key, value in count.items():
        result.append([key, sum(value)/len(value)])  # 消除重复的策略可改，这里定的是均值
    return result

def  read_std_results(file_path):
    wb = xlrd.open_workbook(file_path)
    sheet_list = wb.sheet_names()
    print(sheet_list)
    std_results = {}
    for i in range(len(sheet_list)):
        sheet = wb.sheet_by_name(sheet_list[i])
        nrows = sheet.nrows
        for j in range(1,nrows):
            temp = []
            temp.append(float(sheet.cell(j, 1).value))
            temp.append(int(sheet.cell(j, 2).value))
            temp.append(xlrd.xldate.xldate_as_datetime(sheet.cell(j, 7).value, 0))
            hour=temp[2].hour
            minute=temp[2].minute
            std_results[100*hour+minute] = temp[0:2]
    return std_results  # {'device_name' = [[rssi, gateway_id, datetime],...]}


if __name__ == "__main__":
    path = '2020-04-07-Abeacon3.xlsx'
    result_path = '2020-04-07-Abeacon3_result.xls'
    std_result_path = "2020-04-07-15个测试位置.xlsx"
    raw_data = read_data(path)
    wb = xlwt.Workbook(encoding='utf-8')
    style = xlwt.XFStyle()
    style.num_format_str = 'M/D/YY h:mm'
    # plt.xlabel('X')
    # plt.ylabel('Y')
    # plt.xlim(xmax=45,xmin=0)
    # plt.ylim(ymax=29,ymin=0)
    std_results=read_std_results(std_result_path)

    for key in raw_data.keys():
        sheet = wb.add_sheet(key)

        #########################
        #
        # triposition prediction
        #
        #########################
        i = 0
        data_ = process_data(raw_data[key])

        #删除无效元素
        data=data_.copy()
        for key, value in data_.items():
            locate = locate_by_pointlist(value)
            if locate[0] == 0 and locate[1] == 0:
                data.pop(key)

        #三角定位
        tri_predictions=np.ndarray((len(data.items()),2))
        for key, value in data.items():
            locate = locate_by_pointlist(value)
            tri_predictions[i][0]=locate[0]
            tri_predictions[i][1]=locate[1]
            i += 1
        
        #########################
        #
        # particle filter
        # precition
        #
        #########################

        n_particles = 50000
        v_mean=10
        v_std=5
        tri_pf_predictions = np.empty(tri_predictions.shape)
        particles = create_particles(v_mean, v_std, n_particles) # 初始化粒子
        weights = np.ones(n_particles) / n_particles # 初始化权重

        for i,pos in enumerate(tri_predictions):
            pos = pos.copy()
            state = run_pf(particles, weights, pos)
            tri_pf_predictions[i, :] = state[0:2]

        #########################
        #
        # print results
        #
        #########################
        results=tri_pf_predictions

        i=0
        for key, value in data.items():
            
            sheet.write(i,0,float(results[i][0]))
            sheet.write(i,1,float(results[i][1]))
            sheet.write(i,2,key,style)
            i += 1

        #########################
        #
        # result evaluation
        #
        #########################

        i=0
        for key, value in data.items():
            hour=key.hour
            minute=key.minute
            if(std_results.get(100*hour+minute)!=None):
                #print("{:f} {:f} {:f}".format(results[i][0],results[i][1],distance(results[i][0:2],std_results[100*hour+minute])))
                print(distance(results[i][0:2],std_results[100*hour+minute]))
            i += 1

        #########################
        #
        # dram the figure
        #
        #########################

        std_x=[]
        std_y=[]
        tri_x=[]
        tri_y=[]
        tri_pf_x=[]
        tri_pf_y=[]

        i=0
        for key, value in data.items():
            hour=key.hour
            minute=key.minute
            if(std_results.get(100*hour+minute)!=None):
                std_x.append(std_results.get(100*hour+minute)[0])
                std_y.append(std_results.get(100*hour+minute)[1])
                tri_x.append(tri_predictions[i][0])
                tri_y.append(tri_predictions[i][1])
                tri_pf_x.append(tri_pf_predictions[i][0])
                tri_pf_y.append(tri_pf_predictions[i][1])
            i += 1
        plt.plot(std_x,std_y, marker='+',c='r')
        plt.plot(tri_x,tri_y, marker='+',c='b')
        plt.plot(tri_pf_x,tri_pf_y, marker='+',c='g')
        plt.show()
        plt.close()
        #plt.plot(tri_pf_predictions[:,0],tri_pf_predictions[:,1])
        #plt.show()

    wb.save(result_path)
    # plt.show()
