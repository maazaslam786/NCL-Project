import pandas as pd
import numpy as np

def generate_interval(data):
    time = data['time_stamp']
    n = len(time)
    base_time = pd.to_datetime(time.iloc[0], format='%m/%d/%Y %H:%M') + pd.Timedelta(seconds=1)
    intervals = [base_time + pd.Timedelta(seconds=i * 2) for i in range(n)]

    data['time_stamp'] = intervals
    return data

df = pd.read_csv('car_data_bulk.csv', low_memory=False)
df.set_index('bulk_id')

df = df.loc[df['car_reg_no'] == 113]

df = df.dropna(axis=1, how='all') #dropping the columns which contains all null values

# # #repeated columns which one to keep?
# # print(df['o_s1_b1_fuel_air_equivalence_ratio'].describe())
# print(df['o_s1_b1_fuelair_equivalence_ratio'].describe()) #contains all zeros so removing it

df = df.drop('o_s1_b1_fuelair_equivalence_ratio',axis=1)

cond = df['time_stamp'].isna()

# print(df[cond]) #finding the pattern in null values of time_stamp
df.loc[cond ,'time_stamp'] = df.loc[cond , 'longitude'] #observed that when time_stamp was null, time_stamp was actually present in the longitude column so replacing it

df.loc[cond, 'longitude'] = np.nan

df['engine_rpm'] = df['engine_rpm'].fillna(0) #filling the null values with zero as we observed that when engine_rpm was null vehicle_speed was 0/null and other values were also null, so the engine would be turned off

df[df['engine_rpm']==0] = df[df['engine_rpm']==0].fillna(0) #when engine is turned off all other components are also turned off

# print('Data after filling the engine off readings')
# print(df.isna().sum())

#707198 break point
#950133   break point
# print(len(df))
# print(df.iloc[950133])
df_seg1 = df.iloc[0:707198].copy()
df_seg2 = df.iloc[707198:950133].copy()
df_seg3 = df.iloc[950133:].copy()


# print('Segment 1: ',df_seg1['time_stamp'].unique())
# print('Segment 2: ',df_seg2['time_stamp'].unique())
# print('Segment 3: ',df_seg3['time_stamp'].unique())

df_seg1['time_stamp'] = pd.to_datetime(df_seg1['time_stamp'])
df_seg3['time_stamp'] = pd.to_datetime(df_seg3['time_stamp'])


df_seg2 = df_seg2.groupby('time_stamp').apply(generate_interval)
df_seg2 = df_seg2.reset_index(level = 'time_stamp', drop=True)
# print(df_seg2.head())


df = pd.concat([df_seg1,df_seg2,df_seg3])
df['latitude'] = df['latitude'].fillna(0).astype('float')
df['longitude'] = df['longitude'].fillna(0).astype('float')

# df.info()
# print(df.isna().sum())

df['o_s2_b2_voltage'] = df['o_s2_b2_voltage'].astype('float')
df['o_s1_current'] = df['o_s1_current'].astype('float')
df['calculated_engine_load'] = df['calculated_engine_load'].astype('float')
df['absolute_load_value'] = df['absolute_load_value'].astype('float')
df['throttle_position'] = df['throttle_position'].astype('float')
df['relative_throttle_position'] = df['relative_throttle_position'].astype('float')
df['ap_pos_d'] = df['ap_pos_d'].astype('float')
df['ap_pos_e'] = df['ap_pos_e'].astype('float')
df['commanded_evaporative_purge'] = df['commanded_evaporative_purge'].astype('float')
df['short_term_fuel_trim_b1'] = df['short_term_fuel_trim_b1'].astype('float')
df['absolute_barometric_pressure'] = df['absolute_barometric_pressure'].astype('float')


df.fillna(df[df!=0].mean(),inplace=True) #replacing null values with mean value

# print(df['o_s1_current'].unique()) #all zeros
# print(df['catalyst_temperature_b1_s1'].unique()) #all zeros
# print(df['catalyst_temperature_b1_s2'].unique()) #all zeros

# #dropping the columns
df = df.drop(['o_s1_current','catalyst_temperature_b1_s1','catalyst_temperature_b1_s2'], axis=1)

# print('\nCleaned Data:')
# print(df.isna().sum())
print(len(df))
# df.to_csv('cleaned_bulk_data.csv')
