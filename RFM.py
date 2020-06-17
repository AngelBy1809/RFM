import pandas as pd
import numpy as np
import datetime
pd.set_option('display.max_columns', None)
columns = ['交易金额', '交易数量', '购买日期', '用户ID']
df = pd.read_csv('RFM.csv', sep=',', error_bad_lines=False, names=columns, header=None, low_memory=False)
df.drop(index=0, inplace=True)
# 数据探查
# print(df.describe())
# print(df.info())
# 计算最近购买日期及设定参数R
dt = df
dt_date = dt.groupby('用户ID')['购买日期'].max()  # 最近一次购买日期
cur_date = '2020-05-31'
dt_date = pd.DataFrame(dt_date).reset_index()
dt_date.rename(columns={'购买日期':'最近一次购买日期'}, inplace=True)
dt_date['当前日期'] = cur_date
# dt_date['交易金额'] = dt['交易金额']
dt_date['当前日期'] = pd.to_datetime(dt_date['当前日期'])
dt_date['最近一次购买日期'] = pd.to_datetime(dt_date['最近一次购买日期'])
dt_date['R间隔时间'] = (dt_date['当前日期'] - dt_date['最近一次购买日期'])
dt_date['R间隔时间'] = dt_date['R间隔时间'].map(lambda x: x/np.timedelta64(1, 'D'))
print(dt_date.head(5))


def qnty_level(row, col_name='R间隔时间'):
    value = row[col_name]
    if value <= 30:
        lev = 5
    elif value >= 31 and value <= 60:
        lev = 4
    elif value >= 61 and value <= 90:
        lev = 3
    elif value >= 91 and value <= 120:
        lev = 2
    else:
        lev = 1
    return lev

dt_date['R分值'] = dt_date.apply(qnty_level,axis=1)
# 1、以上计算R参数的部分
# 2、下面计算F参数和M参数，即购买频次和消费金额
df['交易金额'] = df['交易金额'].astype(str).astype(float)  # 交易金额原为object类型，需要转化成数值型（此处是float）
df1 = pd.pivot_table(df, index=['用户ID'], values=['购买日期', '交易金额'], aggfunc={'购买日期': 'count', '交易金额': 'sum'})
df1 = df1.reset_index()
df1.rename(columns={'购买日期': '购买次数', '交易金额': '累计金额'}, inplace=True)

def purchase_level(row, col_name='购买次数'):
    value = row[col_name]
    if value <= 2:
        lev = 1
    elif value >= 3 and value <= 4:
        lev = 2
    elif value >= 5 and value <= 7:
        lev = 3
    elif value >= 8 and value <= 9:
        lev = 4
    else:
        lev = 5
    return lev


df1['F分值'] = df1.apply(purchase_level, axis=1)

def money_level(row, col_name='累计金额'):
    value = row[col_name]
    if value <= 100:
        lev = 1
    elif value >= 101 and value <= 200:
        lev = 2
    elif value >= 201 and value <= 500:
        lev = 3
    elif value >= 501 and value <= 1000:
        lev = 4
    else:
        lev = 5
    return lev


df1['M分值'] = df1.apply(money_level, axis=1)
# 到此处已经计算好3个参数：R分值、F分值和M分值
# 下面进行合并：dt_date 和 df1
dt_new = pd.merge(df1, dt_date, on='用户ID')

dt_new['R均值'] = dt_new['R分值'].mean()
dt_new['F均值'] = dt_new['F分值'].mean()
dt_new['M均值'] = dt_new['M分值'].mean()

# 以下对用户价值进行划分（金额）


def money_level2(row, col_name='F分值'):
    value = row[col_name]
    if value <= 3.62:
        lev = '低'
    else:
        lev = '高'
    return lev


dt_new['M等级'] = dt_new.apply(money_level2, axis=1)


def purchase_level2(row, col_name='F分值'):
    value = row[col_name]
    if value <= 3.46:
        lev = '低'
    else:
        lev = '高'
    return lev


dt_new['F等级'] = dt_new.apply(purchase_level2, axis=1)


def qnty_level2(row, col_name='R分值'):
    value = row[col_name]
    if value <= 2.61:
        lev = '高'
    else:
        lev = '低'
    return lev


dt_new['R等级'] = dt_new.apply(qnty_level2, axis=1)


# 划分不同价值用户
def values_level(row, col_name='R等级', col_name2='F等级', col_name3='M等级'):
    value = row[col_name]
    value2 = row[col_name2]
    value3 = row[col_name3]
    if value == '高' and value2 == '高' and value3 == '高':
        lev = '重要价值用户'
    else:
        lev = '低价值用户'
    return lev


dt_new['用户价值'] = dt_new.apply(values_level, axis=1)
# 计算购买频率及设定参数F
# 计算交易金额并设定M
