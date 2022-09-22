from unittest import result
import pandas as pd
import numpy as np
import datetime as dt
import glob
import shutil
import os

ROOT = '/'
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'result'
BACKUP_FOLDER = 'backup'

# 秒数を時分秒に変換
def stringtime(inttime):
    return (
        str(inttime // 3600) + ':' + str(inttime % 3600 //60) + ':' + str(inttime - (((inttime // 3600) * 3600) + ((inttime % 3600 //60) * 60)))
        if inttime > 0 else
        '-' + str(-inttime // 3600) + ':' + str(-inttime % 3600 //60) + ':' + str(-inttime - (((-inttime // 3600) * 3600) + ((-inttime % 3600 //60) * 60)))
    )

def inoutcheck():
    csvfilelist = glob.glob(os.path.join(ROOT, UPLOAD_FOLDER, '*.csv'))
    resultlist = []

    for csv in csvfilelist:

        data = pd.read_csv(csv , header=1, usecols=['datatime', 'event', 'first', 'last'], encoding='utf-8')
        user = data['last'].iloc[0] + data['first'].iloc[0]

        data.insert(0, 'date', pd.to_datetime(data['datatime']).dt.date)
        data.insert(1, 'time', pd.to_datetime(data['datatime']).apply(lambda x: x.time()))
        data['datatime'] = pd.to_datetime(data['datatime'])
        data = data.sort_values(['date', 'time'])

        indata = data.loc[data['event'] == 'in'].groupby('date').head(1)
        outdata = data.loc[data['event'] == 'out'].groupby('date').tail(1)

        inoutdata = pd.DataFrame( data={
            'date': np.array(data.groupby('date').head(1)['date']),
            'in': np.array(indata['time']),
            'out': np.array(outdata['time']),
            'inoffice': (np.array(outdata['datatime']) - np.array(indata['datatime']))
        })

        inoutdata.insert(len(inoutdata.columns), 'over', (inoutdata['inoffice'] - dt.timedelta(hours=9)))
        inoutdata.insert(len(inoutdata.columns), 'flexsec', (inoutdata['over'].apply(lambda x: int(x.total_seconds()))))

        inoutdata.insert(len(inoutdata.columns) - 1, 'flextime', inoutdata['flexsec'].apply(lambda x: stringtime(x)))
        inoutdata = inoutdata.drop(columns='over')

        inoutdata.loc['totalflex'] = ['', '', '', '', stringtime(inoutdata['flexsec'].sum()), inoutdata['flexsec'].sum()]

        resultname = 'inout_'  + str(dt.date.today()) + '_' + user
        inoutdata.to_csv(os.path.join(ROOT, RESULT_FOLDER, resultname + '.csv'), columns=['date', 'in', 'out', 'flextime'], index = True, index_label = user, encoding='shift-jis')

        backupdir = os.path.join(ROOT, BACKUP_FOLDER, str(dt.date.today()))
        os.makedirs(backupdir, exist_ok=True)
        shutil.move(csv, os.path.join(backupdir, resultname + '_original.csv'))

        resultlist.append(resultname)

    return resultlist