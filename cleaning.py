import pandas as pd
import numpy as np



df = pd.read_csv('95_113_sir.csv',index_col=0)
# df.info()

# df.info()
# df['time_stamp'] = pd.to_datetime(df['time_stamp'])
print(df.iloc[10000]['time_stamp'])


# df = df.dropna(axis=1, how='all') #dropping the columns which contains all null values
# # df.info()

# #repeated columns which one to keep?
# print(df['o_s1_b1_fuel_air_equivalence_ratio'].describe())
# print(df['o_s1_b1_fuelair_equivalence_ratio'].describe()) #contains all zeros so removing it

# df = df.drop('o_s1_b1_fuelair_equivalence_ratio',axis=1)

# df['engine_rpm'] = df['engine_rpm'].fillna(0) #filling the null values with zero as we observed that when engine_rpm was null vehicle_speed was 0/null and other values were also null, so the engine would be turned off

# df[df['engine_rpm']==0] = df[df['engine_rpm']==0].fillna(0) #when engine is turned off all other components are also turned off

# print('Data after filling the engine off readings')
# # df.info()

# df.fillna(df[df!=0].mean(),inplace=True) #replacing null values with mean value

# print('\nCleaned Data:')
# print(df.isna().sum())

#df.info()
# df.to_csv('cleaned_data.csv')
