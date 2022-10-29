import numpy as np
import pandas as pd
import logging
import matplotlib.pyplot as plt
from numpy import nan, ndarray
import logging
import math
from numpy import array
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from datetime import date
today=date.today()
Presentdate=today.strftime("%d-%m-%Y")
#print(Presentdate)
#print(today)
path="C:\\myproj\\"+Presentdate+"_log_data.log"
#print(path)
#logging.basicConfig(filename='C:\\myproj\\app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig(filename=path, filemode='a',level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
model = Sequential()
n_steps_in, n_steps_out = 7, 1
n_features = 1
def BDR(list):
	
	logging.info('Bad data replacement algorithm is called.')
	a=pd.Series(list)
	a.interpolate(method='linear',direction = 'forward', inplace=True)
	logging.info('Bad data is checked and replaced Successfully.')
	#print(a)
	return a.tolist()

def get_val(list):
	for i in list:
		if (i>2000 and i<15000):
			return i
	return np.nan

def val_check(list):
	if(list[0]>2000 and list[0]<15000):
		return list
	else:
		list[0]=get_val(list)
		return list
		
def Replace_With_NaN(list):
    logging.info('Replace with NaN algorithm is called.')
    l1=[]
    for i in list:
        if(i<14000 and i>7000):
            l1.append(i)
        else:
            l1.append(np.nan)
    logging.info('Bad data is replaced with NaN and returned.')
    return l1
        
def split_sequence(sequence, n_steps_in, n_steps_out):
	
	logging.info('Split sequence is called.')
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps_in
		out_end_ix = end_ix + n_steps_out
		# check if we are beyond the sequence
		if out_end_ix > len(sequence):
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:out_end_ix]
		X.append(seq_x)
		y.append(seq_y)
	logging.info('Split sequence is done.')
	return array(X), array(y)

def create_model(X,y):
    # define models
    # demonstrate prediction
    logging.info('Model initialized.')
    model.add(LSTM(100, activation='relu', input_shape=(n_steps_in, n_features)))
    model.add(RepeatVector(n_steps_out))
    model.add(LSTM(100, activation='relu', return_sequences=True))
    model.add(TimeDistributed(Dense(1)))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit(X, y, epochs=200, verbose=0)
    logging.info('Model created.')

def LSTM_Algo(list):
    
    logging.info('LSTM Algorithm is called.')
    n=len(list)
    s=array(list)
    new_s=[]
    Data=new_s
    s = s.reshape((len(s), 1))
    scaler = MinMaxScaler(feature_range = (0, 1))
    s = scaler.fit_transform(s)
    try:
        s=s.reshape(n,)
    except:
        logging.error('Reshape error of given list.')
    Data=s
    logging.info('Given Data got normalized.')
    n_steps_in, n_steps_out = 7, 1
    # split into samples
    X, y = split_sequence(s, n_steps_in, n_steps_out)
    # reshape from [samples, timesteps] into [samples, timesteps, features]
    n_features = 1
    X = X.reshape((X.shape[0], X.shape[1], n_features))
    y = y.reshape((y.shape[0], y.shape[1], n_features))
    sample=Data
    #Here the data should be checked before passing on i.e. if there are zeros
    s1=np.array(sample, np.int64)
    try:
        x_input = s1[-7:]
    except:
        logging.error('x_input Reshape error.')
    x_input = x_input.reshape((1, n_steps_in, n_features))        
    try:
        yhat = model.predict(x_input, verbose=0)
        logging.info('Reuse of created model.')
    except:
        logging.warning('Model created again.')
        create_model(X,y)
        yhat = model.predict(x_input, verbose=0)
        
    logging.info('Predict Model is called.')
    #yhat= yhat.reshape(1,)
    yhat=yhat[0]
    #yhat=yhat.tolist()  
    yhat=yhat.reshape(-1, 1)
    output_data = scaler.inverse_transform(yhat)
    logging.info('Output data got denormalized.')
    logging.info('Denormalized data is returned.')
    logging.info('LSTM Model Worked Successfully.\n')
    return (round(output_data[0][0],2))

def process(list):
    logging.info('Main Process is called.')
    RWN=Replace_With_NaN(list)
    L1=val_check(RWN)
    New_List=BDR(L1)
    value=LSTM_Algo(New_List)
    return value