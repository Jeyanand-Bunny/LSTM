from re import L
from matplotlib.pyplot import flag
import numpy as np
import math
from matplotlib import pyplot as pt
import pandas as pd
import logging
from datetime import date
today = date.today()
Presentdate = today.strftime("%d-%m-%Y")

#path = "C:\\myproj\\"+Presentdate+"_log_data.log"
# logging.basicConfig(filename=path, filemode='a', level=logging.DEBUG,
#                   format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
# print(prediction)


def sums(a):
    a1 = 0
    for i, v in enumerate(a):
        a1 = a1+v
    a2 = len(a)
    a1 = a1/a2
    return a1


def Kalman(prevpred, prevact, prediction):
    index = 0
    error1 = []
    flag = []

    for i, v in enumerate(prevact):
        res = [prevact[i + 1] - prevact[i] for i in range(len(prevact)-1)]
    for i in res:
        index = i+index
    le = len(res)
    # print(res)
    um = index/(le)
    #print('_____', um)

    for i in range(len(prevact)):
        temp = (prevact[i]-prevpred[i])/prevact[i]
        error1.append(temp)
        if(temp < 0):
            flag.append(0)
        else:
            flag.append(1)

    Avg = 0
    for i in range(len(error1)):
        Avg += error1[i]
    Avg1 = len(error1)
    up = Avg/Avg1
    # print(up)
    # print(up)

    #logging.info('Average Error = ', up)
    #logging.info('Uncertainity Measurement = ', um)
    # print(um)

    Kalmangain = um/(um+up)
    #logging.info('Kalmangain = ', Kalmangain)
    # print(Kalmangain,"kg")

    pp = sums(prediction)
    mpre = sums(prevact)
    prpre = sums(prevpred)
    C_Data1 = []
    for i in range(len(prediction)):
        if(flag[i] == 0):
            val = -1
        else:
            val = 1
        C_Data1.append(prediction[i]+(Kalmangain*(prevact[i]-prevpred[i])))
    return C_Data1
