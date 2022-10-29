from numpy import NaN
import requests
import psycopg2
import openpyxl
import requests
import json
import logging

from lstm_1 import *
import datetime
from datetime import date, time, datetime
from datetime import timedelta
#from forecast import *
requests.urllib3.disable_warnings()
# (please change the date for other day forecast)
today = date.today()  # - timedelta(1)
Presentdate = today.strftime("%d-%m-%Y")
path = "C:\\myproj\\"+Presentdate+"_log_data.log"
logging.basicConfig(filename=path, filemode='a', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def get_dates():
    seas_set = [[3, 4, 5, 6], [7, 8, 9, 10], [11, 12, 1, 2]]
    y_day = today - timedelta(days=1)
    tm_date = today + timedelta(days=1)
    # print(tm_date,tm_date.month)
    wday = tm_date.weekday()
    set = []
    for seas in seas_set:
        for m_seas in seas:
            if (tm_date.month == m_seas):
                set = seas
    dates = []

    mnth = set[0]
    yr = tm_date.year
    lmnth = mnth - 1

    lyr = yr - 1
    c_day = date(year=lyr, month=mnth, day=1)
    day_df = c_day.weekday() - wday
#   print(day_df,c_day)
    if day_df <= 0:
        day_df *= -1
        c_day += timedelta(days=day_df)
    else:
        rdf = 7 - day_df
        c_day += timedelta(days=rdf)

    while(c_day.month <= set[3]):
        dates.append(c_day)
        c_day += timedelta(days=7)

    c_day = date(year=yr, month=lmnth, day=1)
    day_df = c_day.weekday() - wday
    if day_df <= 0:
        day_df *= -1
        c_day += timedelta(days=day_df)
    else:
        rdf = 7 - day_df
        c_day += timedelta(days=rdf)
    while(c_day < y_day):
        dates.append(c_day)
        c_day += timedelta(days=7)

    return(dates)


def get_time():
    timed = datetime(year=2006, month=11, day=3)
    time_list = []
    for i in range(1440):

        timen = timed + timedelta(minutes=i)
        hr = str(timen.hour)
        if (len(hr) < 2):
            hr = "0" + hr
        mn = str(timen.minute)
        if (len(mn) < 2):
            mn = "0" + mn
        timestr = hr + ":" + mn
        time_list.append(timestr)
    return(time_list)


def get_n_data(conn, cursor):
    iter_dates = get_dates()
    # iter_data = get_data
    query = "SELECT  reading_json_text FROM vscada.scada_point_data where point_id = '10751' and reading_date = %s"

    # print( tm,val)

    data_flist = []

    for datess in iter_dates:
        data_iter = []
        #    print(datess,datess.weekday())
        # print(datess)
        vars = datess,
        cursor.execute(query, vars)
        data = cursor.fetchall()
        # print(data[0][0])
        resp = " {"
        if len(data) > 0:
            resp = data[0][0]
        #datlen = len(resp)

        if resp[-1:] != ']':
            for i in range(200):
                resp = resp[:-1]
                if resp[-3:] == ',{"':
                    resp = resp[:-3]+']'
                    print(resp[-10:])
                    break

        # print(datess)
        # print(resp)
        resps = resp.split('{')
    #    print(resp)
        lent = len(resps)
        if lent > 3:
            for i in range(3, lent-2):
                date_val = ['', '']
                r_val = resps[i].split('"')
                tm = r_val[3]
                val = r_val[6]
                val = val[1:-2]
                date_val[0] = tm
                date_val[1] = val
                data_iter.append(date_val)
        if lent > 3:
            r_val = resps[lent-1].split('"')
            tm = r_val[3]
            val = r_val[6]
            val = val[1:-5]
            date_val[0] = tm
            date_val[1] = val
    #        print(tm, val, j)
            data_iter.append(date_val)
        data_flist.append(data_iter)
    return(data_flist)


def get_old_data():
    iter_dates = get_dates()
    # iter_data = get_data
    req = 'link'
    # print( tm,val)

    data_flist = []
    for datess in iter_dates:
        data_iter = []
        #    print(datess,datess.weekday())
        yr = datess.year
        mnth = str(datess.month)
        if (len(mnth) < 2):
            mnth = '0' + mnth
        iday = str(datess.day)
        if (len(iday) < 2):
            iday = '0' + iday
        idate = iday + "-" + mnth + "-" + str(yr)
    #    print(idate)
        response = requests.post(
            req, {"pointid": "", "recordDate": idate}, verify=False)
        resp = response.text
        resps = resp.split('{')
    #    print(resp)
        lent = len(resps)
        if lent > 3:
            for i in range(3, lent-2):
                date_val = ['', '']
                r_val = resps[i].split('"')
                tm = r_val[3]
                val = r_val[6]
                val = val[1:-2]
                date_val[0] = tm
                date_val[1] = val
                data_iter.append(date_val)
        if lent > 3:
            r_val = resps[lent-1].split('"')
            tm = r_val[3]
            val = r_val[6]
            val = val[1:-5]
            date_val[0] = tm
            date_val[1] = val
    #        print(tm, val, j)
            data_iter.append(date_val)
        data_flist.append(data_iter)
    return(data_flist)


time_list = get_time()
#data_flist = get_old_data()
tm_date = today + timedelta(days=1)
# print(len(data_flist))


def LSTM_MAIN():
    conn = psycopg2.connect(
    host="localhost",#host="192.168.0.37",
    database="postgres",
    user="postgres",
    password="password")
    cursor = conn.cursor()
    data_flist = get_n_data(conn, cursor)
    j = k = l = 0
    for data_f in data_flist:
        #    print(j)
        if len(data_f) > 0:
            k += 1
        else:
            l += 1
    #print('no =', k)
    #print('yes =', l)
    logging.info("Data Present: "+str(l) + " Data Absent: "+str(k))
    j = 0
    fc_data = []
    for time_f in time_list:
        data_set = []
        data_fval = ['', '']
        for data_f in data_flist:
            data_v = NaN
            for data_ls in data_f:
                if time_f == data_ls[0]:
                    data_v = float(data_ls[1])
                    break
                if time_f < data_ls[0]:
                    break
            data_set.append(data_v)
        j += 1
        val = process(data_set)
        val = str(val)
        data_fval[0] = time_f
        data_fval[1] = val
        fc_data.append(data_fval)
        # print(data_set)
    # print(j)
    dstr = ''
    for data_fval in fc_data:
        dstr += '{"recordTime": "'+data_fval[0] + \
            '", "recordValue":'+data_fval[1] + '},'
    dstr = dstr[:-1]
    fstr = '['+dstr+']'
    # print(fstr)

    query = "INSERT INTO vscada.rtu_point_real_fcast_data (rtu_point_id, rtu_data_date, forecast_json)VALUES(%s,%s,%s);"
    vars = ('10751', tm_date, fstr)
    cursor.execute(query, vars)
    #print(query, vars)
    logging.info("affected rows = {}".format(cursor.rowcount))
    conn.commit()
    conn.close
    cursor.close
