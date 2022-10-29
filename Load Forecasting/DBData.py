import psycopg2
from datetime import datetime
from datetime import timedelta
# def get_data(is_act,hr,dt):
#is_act = 0
#hr = '10:00'
#dt = datetime.now() - timedelta(days=2)


def getdata(is_act, hr, dt):
    conn = psycopg2.connect(
        host="10.100.0.35",
        database="postgres",
        user="postgres",
        password="$$erver@&aps!")
    cursor = conn.cursor()
    if is_act == 1:

        query = "SELECT  reading_json_text FROM vscada.scada_point_data where point_id = '10751' and reading_date = %s"
        dates = str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)
        var = dates,
        cursor.execute(query, var)
        data = cursor.fetchall()

    else:
        query = "SELECT  forecast_json FROM vscada.rtu_point_real_fcast_data where rtu_point_id = '10751' and rtu_data_date = %s"
        dates = str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)
        var = dates,
        cursor.execute(query, var)
        data = cursor.fetchall()
    data_iter = []
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

            r_val = resps[i].split('"')
            date_val = ['', '']
            tm = r_val[3]
            val = r_val[6]
            val = val[1:-2]
            if tm[:2] == hr[:2]:
                date_val[0] = tm
                date_val[1] = val
                data_iter.append(date_val)
    if lent > 3:
        r_val = resps[lent-1].split('"')
        date_val = ['', '']
        tm = r_val[3]
        val = r_val[6]
        val = val[1:-5]
        if tm[:2] == hr[:2]:
            date_val[0] = tm
            date_val[1] = val
            data_iter.append(date_val)
    stmin = 0
    inival = 0
    fdata_iter = []
    if is_act == 1:
        for data_val in data_iter:
            dmin = int(data_val[0][3:5])
            for i in range(stmin, dmin):
                fdata_iter.append(data_val[1])
                #print(i, data_val[1])
            stmin = dmin
        if len(data_iter) < 1:
            print((data_iter), '--------No actual DaTa----')
        data_val = data_iter[len(data_iter)-1]
        dmin = int(data_val[0][3:5])
        for i in range(dmin, 60):
            fdata_iter.append(data_val[1])
            #print(i, data_val[1])
    else:
        i = 0
        for data_val in data_iter:

            fval = data_val[1]
            if data_val[1] == str('nan'):
                if i >= 0 and i < 59:
                    for j in range(i, 60):
                        dt = data_iter[j]
                        if dt[1] != str('nan'):
                            fval = dt[1]
                            break
                else:
                    if i == 59:
                        for j in range(1, 59):
                            dt = data_iter[59-j]
                            if dt[1] != str('nan'):
                                fval = dt[1]
                                break
            i += 1
            fdata_iter.append(fval)
    f_data = []
    for fdata in fdata_iter:
        ff_data = float(fdata)
        f_data.append(ff_data)
    conn.close
    cursor.close
    return(f_data)


def save_dt(res, hr, dt):
    conn = psycopg2.connect(
        host="10.100.0.35",
        database="postgres",
        user="postgres",
        password="$$erver@&aps!")
    cursor = conn.cursor()
    i = 0
    dstr = ''
    cdt = datetime.today()
    for data_fval in res:
        icar = str(i)
        if len(icar) < 2:
            icar = '0'+icar
        time_str = hr[:2]
        time_str += ':'+icar
        dstr += '{"recordTime": "'+time_str + \
            '", "recordValue":'+str(data_fval) + '},'
        i += 1
    dstr = dstr[:-1]
    fstr = '['+dstr+']'
    date_str = dt.strftime("%Y") + '-' + \
        dt.strftime("%m")+'-'+dt.strftime("%d")
    # print(fstr)
    query = "SELECT real_forecast_json  FROM vscada.rtu_point_real_fcast_data where rtu_point_id = '10751' and rtu_data_date = %s;"
    vars = date_str,
    cursor.execute(query, vars)
    data = cursor.fetchall()
    chr = cdt.strftime('%H') + ':00'
    # print(data)
    if data[0][0] != None:

        tstr = data[0][0]
        fstr = tstr[:-1] + ',' + dstr + ']'

    # print(fstr)
    query = "UPDATE vscada.rtu_point_real_fcast_data SET  real_forecast_json= %s where rtu_point_id = '10751' and rtu_data_date = %s;"
    vars = (fstr, date_str)
    cursor.execute(query, vars)
    #print(query, vars)
    #logging.info("affected rows = {}".format(cursor.rowcount))
    conn.commit()
    conn.close
    cursor.close
