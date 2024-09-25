import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_trips(df):
    trips = []
    trip = []
    in_trip = False
    for idx, row in df.iterrows():
        if row['engine_rpm'] > 0:
            if not in_trip:
                in_trip = True
                trip = []
            trip.append(row)
        elif row['engine_rpm'] == 0:
            if in_trip:
                in_trip = False
                if trip:
                    trips.append(pd.DataFrame(trip))
    return trips

def get_trips_df(df):
    trips = get_trips(df)
    trips_dict = {
        'trip_start': [], 'trip_end': [], 'duration (mins)': [], 'avg_speed': [], 
        'max_speed': [], 'distance': [], 'MAF': [], 'FAR': [], 'fuel_mass_flow_rate': [], 'fuel consumption (grams)': []
    }
    
    for i in trips:
        trips_dict['trip_start'].append(i.iloc[0]['time_stamp'])
        trips_dict['trip_end'].append(i.iloc[-1]['time_stamp'])
        
        duration = (i.iloc[-1]['time_stamp'] - i.iloc[0]['time_stamp']).total_seconds()
        trips_dict['duration (mins)'].append(duration / 60)
        
        trips_dict['avg_speed'].append(i['vehicle_speed'].mean())
        trips_dict['max_speed'].append(i['vehicle_speed'].max())
        trips_dict['distance'].append((i['distance'].sum()) / 1000)
        
        trips_dict['MAF'].append(i['mass_air_flow_rate'].mean())
        trips_dict['FAR'].append(i['o_s1_b1_fuel_air_equivalence_ratio'].mean())
        
        fuel_mass_flow_rate = i['mass_air_flow_rate'].mean() / i['o_s1_b1_fuel_air_equivalence_ratio'].mean()
        trips_dict['fuel_mass_flow_rate'].append(fuel_mass_flow_rate)
        
        trips_dict['fuel consumption (grams)'].append(round(fuel_mass_flow_rate * duration, 2))

    trips_df = pd.DataFrame(trips_dict)
    trips_df = trips_df[trips_df['avg_speed'] != 0].reset_index(drop=True)
    
    return trips_df

def fuel_estimation(df):
    trips_df = get_trips_df(df)
    
    print('Number of Trips:', len(trips_df))
    speed_labels = ['0-10','11-20','21-30','31-40','41-50','50+']
    speed_bins = [0,10,20,30,40,50,np.inf]
    trips_df['Speed Brackets'] = pd.cut(trips_df['avg_speed'], bins=speed_bins, labels=speed_labels)

    # Calculate fuel consumption in liters (Density of fuel = 0.75 kg/L)
    trips_df['fuel_consumption (liters)'] = round((trips_df['fuel consumption (grams)'] / 1000) / 0.75, 2)
    
    # Fuel price per liter
    fuel_price_per_liter = 249.1
    
    # Calculate fuel price for each trip
    trips_df['fuel_cost'] = trips_df['fuel_consumption (liters)'] * fuel_price_per_liter
    
    print(trips_df.head())

    # Plot fuel consumption by distance
    sns.set_style("whitegrid") 
    plt.figure()
    sns.relplot(trips_df, x='distance', y='fuel_consumption (liters)', size='duration (mins)', hue='Speed Brackets', palette='husl') \
        .set(title='Fuel Consumption by Distance', xlabel='Distance (km)', ylabel='Fuel Consumption (liters)')
    plt.show()

    # Plot regression line for fuel consumption by distance
    plt.figure()
    sns.regplot(trips_df, x='distance', y='fuel_consumption (liters)', ci=None) \
        .set(title='Fuel Consumption by Distance', xlabel='Distance (km)', ylabel='Fuel Consumption (liters)')
    plt.show()
    
    # Plot fuel cost per trip
    plt.figure()
    sns.barplot(x=trips_df.index, y=trips_df['fuel_cost'], palette='coolwarm')
    plt.title('Fuel Cost by Trip')
    plt.xlabel('Trip Number')
    plt.ylabel('Fuel Cost (in Rupees)')
    plt.xticks(ticks=[i for i in range(0, len(trips_df), 5)], labels=[f'Trip {i+1}' for i in range(0, len(trips_df), 5)])
    plt.show()

# Load and preprocess the dataset
df = pd.read_csv('cleaned_data.csv', index_col=0)
df['time_stamp'] = pd.to_datetime(df['time_stamp'])
df['time_diff'] = df['time_stamp'].diff().dt.total_seconds()
df['time_till_speed_continued'] = df['time_diff'].shift(-1)
df['final_speed'] = df['vehicle_speed'].shift(-1)
df['acceleration'] = ((df['final_speed'] - df['vehicle_speed']) * 1000 / 3600) / df['time_till_speed_continued']
df['distance'] = round((df['vehicle_speed'] * df['time_till_speed_continued']) + (0.5 * df['acceleration'] * (df['time_till_speed_continued'] ** 2)), 2)

# Call the updated fuel estimation function
fuel_estimation(df)
