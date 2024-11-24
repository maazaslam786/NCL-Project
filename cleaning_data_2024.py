import pandas as pd
import numpy as np

def generate_interval(data):
    time = data['time_stamp']
    n = len(time)
    base_time = pd.to_datetime(time.iloc[0], format='%m/%d/%Y %H:%M') + pd.Timedelta(seconds=1)
    intervals = [base_time + pd.Timedelta(seconds=i * 2) for i in range(n)]

    data['time_stamp'] = intervals
    return data

df = pd.read_csv('95_113_sir.csv',index_col=0)
# df.info()


df = df.groupby('time_stamp').apply(generate_interval)
df = df.reset_index(level = 'time_stamp', drop=True)

df = df.dropna(axis=1, how='all') #dropping the columns which contains all null values
# df.info()

#repeated columns which one to keep?
# print(df['o_s1_b1_fuel_air_equivalence_ratio'].describe())
# print(df['o_s1_b1_fuelair_equivalence_ratio'].describe()) #contains all zeros so removing it

df = df.drop('o_s1_b1_fuelair_equivalence_ratio',axis=1)

df['engine_rpm'] = df['engine_rpm'].fillna(0) #filling the null values with zero as we observed that when engine_rpm was null vehicle_speed was 0/null and other values were also null, so the engine would be turned off

df[df['engine_rpm']==0] = df[df['engine_rpm']==0].fillna(0) #when engine is turned off all other components are also turned off

print('Data after filling the engine off readings')
print(df.isna().sum())


df.fillna(df[df!=0].mean(),inplace=True) #replacing null values with mean value
print(df.isna().sum())

df = df.fillna(0)

print('\nCleaned Data:')
print(df.isna().sum())

df = df.sort_values(by='time_stamp')
print(df['time_stamp'].iloc[0])
print(df['time_stamp'].iloc[-1])

df.to_csv('cleaned_data_2024.csv')