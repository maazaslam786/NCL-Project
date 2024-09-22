import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import seaborn as sns


def acc_analysis(df):
    trips = get_trips(df)

    trips_df = pd.DataFrame()
    for i in range(len(trips)):
        if trips[i]['vehicle_speed'].mean() != 0:
            trips[i]['trip'] = i+1
            trips_df = pd.concat([trips_df,trips[i]])


    sns.relplot(trips_df, x='time_stamp',y='acceleration',kind='line',hue='trip',palette='viridis') \
    .set(title='Acceleration by Time',xlabel='Time',ylabel='Acceleration')

##    ax = sns.relplot(trips_df, x='time_stamp',y='acceleration',kind='line')
##    ax.set(title='Acceleration by Time',xlabel='Time',ylabel='Acceleration')
##
##    g = ax.axes[0, 0]
##    
##    trip_no = trips_df['trip'].unique()
##    cmap = plt.get_cmap('viridis', len(trip_no)) 
##    for idx,j in enumerate(trip_no):
##        data = trips_df[trips_df['trip']==j]
##        start = data['time_stamp'].min()
##        end = data['time_stamp'].max()
##        g.axvspan(start, end, color=cmap(idx), alpha=0.3)

    plt.show()
    

def get_trips(df):
    trips = []
    trip = []
    in_trip = False
    for idx, row in df.iterrows():  #trip starts when engine_rpm increases from zero (engine starts) and ends when engine_rpm again reaches zero (engine turns off)
        if row['engine_rpm'] > 0:
            if not in_trip:         #checking if the car was already in trip or not
                in_trip = True      #starting a new trip as car was not in a trip
                trip = []
            trip.append(row)
        elif row['engine_rpm'] == 0:
            if in_trip:             #since there are many zero value, so checking if the car was already in a trip if yes then end the trip
                in_trip = False
                if trip:
                    trips.append(pd.DataFrame(trip)) #adding the trip to the trips list

    return trips

def get_trips_df(df):
    
    trips = get_trips(df)

    trips_dict = {'trip_start':[],'trip_end':[], 'duration (mins)':[], 'avg_speed':[], 'max_speed':[],'distance':[], 'MAF':[], 'FAR':[],'fuel_mass_flow_rate':[],'fuel consumption (grams)':[]}
    for i in trips:
        trips_dict['trip_start'].append(i.iloc[0]['time_stamp'])
        trips_dict['trip_end'].append(i.iloc[-1]['time_stamp'])
        
        duration = (i.iloc[-1]['time_stamp'] - i.iloc[0]['time_stamp']).total_seconds()
        trips_dict['duration (mins)'].append(duration/60)
            
        trips_dict['avg_speed'].append(i['vehicle_speed'].mean())
        trips_dict['max_speed'].append(i['vehicle_speed'].max())

        trips_dict['distance'].append((i['distance'].sum())/1000)

        trips_dict['MAF'].append(i['mass_air_flow_rate'].mean())
        trips_dict['FAR'].append(i['o_s1_b1_fuel_air_equivalence_ratio'].mean())

        fuel_mass_flow_rate = i['mass_air_flow_rate'].mean() / i['o_s1_b1_fuel_air_equivalence_ratio'].mean()
        trips_dict['fuel_mass_flow_rate'].append(fuel_mass_flow_rate)

        trips_dict['fuel consumption (grams)'].append(round(fuel_mass_flow_rate * duration,2))

    trips_df = pd.DataFrame(trips_dict)
    trips_df = trips_df[trips_df['avg_speed'] != 0].reset_index(drop=True)

    return trips_df

def fuel_estimation(df):
    
    trips_df = get_trips_df(df)
    
    print('Number of Trips:',len(trips_df))
    speed_labels = ['0-10','11-20','21-30','31-40','41-50','50+']
    speed_bins = [0,10,20,30,40,50,np.inf]
    trips_df['Speed Brackets'] = pd.cut(trips_df['avg_speed'], bins=speed_bins, labels=speed_labels)

    
    trips_df['fuel_consumption (liters)'] = round((trips_df['fuel consumption (grams)'] / 1000) / 0.75 , 2) #density of fuel = 0.75 kg/L
    print(trips_df.head())


    sns.set_style("whitegrid") 
    plt.figure()                                                 #husl 
    sns.relplot(trips_df, x='distance', y='fuel_consumption (liters)',size='duration (mins)',ax=ax0,hue='Speed Brackets',palette='husl') \
                         .set(title='Fuel Consumption by Distance',xlabel='Distance (km)', ylabel='Fuel Consumption (liters)')
    plt.show()

    plt.figure()
    sns.regplot(trips_df, x='distance', y='fuel_consumption (liters)',ci=None,ax=ax1) \
                         .set(title='Fuel Consumption by Distance',xlabel='Distance (km)', ylabel='Fuel Consumption (liters)')
    plt.show()
        

def speed_insights(df):
    
    trips_df = get_trips_df(df)

    print('Number of Trips:',len(trips_df))
    print('Average Speed:',round(trips_df['avg_speed'].mean(),2))
    print('Maximum Speed:',trips_df['max_speed'].max())

    fig, ax = plt.subplots()
    sns.barplot(trips_df, x=trips_df.index, y='avg_speed', ax=ax, label='Average Speed',color='k')
    sns.barplot(trips_df, x=trips_df.index, y='max_speed',ax=ax, label='Maximum Speed',alpha=0.5)
    ax.set_xticks(ticks=[i for i in range(0,len(trips_df),5)])
    ax.set(title='Speed by Trips',xlabel='Trip',ylabel='Speed')
    ax.legend()
    plt.show()



df = pd.read_csv('cleaned_data.csv',index_col=0)
df['time_stamp'] = pd.to_datetime(df['time_stamp'])
df['time_diff'] = df['time_stamp'].diff().dt.total_seconds()
df['time_till_speed_continued'] = df['time_diff'].shift(-1)
df['final_speed'] = df['vehicle_speed'].shift(-1)
df['acceleration'] = ((df['final_speed']- df['vehicle_speed'])*1000/3600) / df['time_till_speed_continued']
df['distance'] = round((df['vehicle_speed']*df['time_till_speed_continued']) + (0.5*df['acceleration']*(df['time_till_speed_continued']**2)),2)


#speed_insights(df)
#df.info()
fuel_estimation(df)

#acc_analysis(df)


