import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Load your dataset
df = pd.read_csv('cleaned_data.csv', index_col=0)
df['time_stamp'] = pd.to_datetime(df['time_stamp'])

# Trip logic to split dataset into trips
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

# Create a dictionary to hold trip-level data
trips_dict = {'trip_start': [], 'trip_end': [], 'duration (mins)': [], 'avg_speed': [], 'dist': [], 'MAF': [], 'FAR': []}

for i in trips:
    trips_dict['trip_start'].append(i.iloc[0]['time_stamp'])
    trips_dict['trip_end'].append(i.iloc[-1]['time_stamp'])
    
    duration = (i.iloc[-1]['time_stamp'] - i.iloc[0]['time_stamp']).total_seconds()
    trips_dict['duration (mins)'].append(duration / 60)
    
    trips_dict['avg_speed'].append(i.loc[i['vehicle_speed'] != 0, 'vehicle_speed'].mean())
    
    # Calculate distance and fuel-related values
    i['time_diff'] = i['time_stamp'].diff().dt.total_seconds()
    i['time_till_speed_continued'] = i['time_diff'].shift(-1)
    i['final_speed'] = i['vehicle_speed'].shift(-1)
    i['acceleration'] = ((i['final_speed'] - i['vehicle_speed']) * 1000 / 3600) / i['time_till_speed_continued']
    i['distance'] = round(((i['vehicle_speed'] * 1000 / 3600) * i['time_till_speed_continued']) + 
                          (0.5 * i['acceleration'] * (i['time_till_speed_continued'] ** 2)), 2)
    
    # Last point distance calculation
    temp = i.iloc[-1]['vehicle_speed'] * 1000 / 3600
    i.at[i.index[-1], 'acceleration'] = (0 - temp) / 2
    i.at[i.index[-1], 'distance'] = round(temp * 2 + 0.5 * ((0 - temp) / 2) * 4)
    
    # Append total distance for the trip
    trips_dict['dist'].append((i['distance'].sum()) / 1000)  # Convert meters to kilometers
    
    # Mass Air Flow (MAF) calculation and Fuel Air Ratio (FAR)
    maf = (i['mass_air_flow_rate'] * i['time_till_speed_continued']).sum() / i['time_till_speed_continued'].sum()
    trips_dict['MAF'].append(maf / 1000)  # MAF in kg/s if originally in g/s
    trips_dict['FAR'].append(i['o_s1_b1_fuel_air_equivalence_ratio'].mean())

# Create DataFrame from trips_dict
trips_df = pd.DataFrame(trips_dict)
trips_df = trips_df.dropna(subset=['avg_speed']).reset_index(drop=True)

# Add fuel consumption calculations
# MAF is assumed to be in kg/s
trips_df['fuel_mass_flow_rate'] = trips_df['MAF'] / trips_df['FAR']  # MAF/FAR = fuel mass flow rate in kg/s

# Convert duration to seconds and calculate fuel consumption in kg
trips_df['fuel consumption (kg)'] = trips_df['fuel_mass_flow_rate'] * (trips_df['duration (mins)'] * 60)

# Convert fuel consumption from kg to liters using 0.75 kg/L as fuel density
trips_df['fuel consumption (liters)'] = trips_df['fuel consumption (kg)'] / 0.75

# Display the trips summary
print(trips_df[['trip_start', 'trip_end', 'duration (mins)', 'avg_speed', 'dist', 'fuel consumption (liters)']])

# Function to display summary and plot data for specific time range
def display_trip_summary_and_plot(start_time, end_time):
    # Filter the trips_df for the given time range
    mask = (trips_df['trip_start'] >= start_time) & (trips_df['trip_end'] <= end_time)
    filtered_trips = trips_df[mask]

    if filtered_trips.empty:
        print(f"No data available between {start_time} and {end_time}.")
        return

    # Summarize the results
    total_duration = filtered_trips['duration (mins)'].sum()
    total_distance = filtered_trips['dist'].sum()  # Total distance in km
    total_fuel_consumed = filtered_trips['fuel consumption (liters)'].sum()  # Total fuel consumption in liters
    avg_speed = filtered_trips['avg_speed'].mean()
    max_speed = filtered_trips['avg_speed'].max()

    print(f"Summary for the trips between {start_time} and {end_time}:")
    print(f"- Average Speed: {avg_speed:.2f} km/h")
    print(f"- Maximum Speed: {max_speed:.2f} km/h")
    print(f"- Distance Covered: {total_distance:.2f} km")
    print(f"- Fuel Consumed: {total_fuel_consumed:.2f} liters")
    print(f"- Total Duration: {total_duration:.2f} minutes")

    # Plot trip data
    fig = make_subplots(specs=[[{"secondary_y": True}]])  # Create subplot with secondary y-axis

    # Plot average speed over trips
    fig.add_trace(go.Scatter(
        x=filtered_trips['trip_start'],
        y=filtered_trips['avg_speed'],
        mode='lines+markers',
        name='Avg Speed (km/h)',
        line=dict(color='blue')
    ), secondary_y=False)

    # Plot distance covered over trips
    fig.add_trace(go.Scatter(
        x=filtered_trips['trip_start'],
        y=filtered_trips['dist'],
        mode='lines+markers',
        name='Distance Covered (km)',
        line=dict(color='orange')
    ), secondary_y=False)

    # Plot fuel consumption over trips
    fig.add_trace(go.Scatter(
        x=filtered_trips['trip_start'],
        y=filtered_trips['fuel consumption (liters)'],
        mode='lines+markers',
        name='Fuel Consumption (liters)',
        line=dict(color='green')
    ), secondary_y=True)

    # Update layout
    fig.update_layout(
        title="Trip Summary",
        xaxis_title="Trip Start Time",
        hovermode="x unified",
        template="plotly_white"
    )

    fig.update_yaxes(title_text="Speed (km/h) & Distance (km)", secondary_y=False)
    fig.update_yaxes(title_text="Fuel Consumption (liters)", secondary_y=True)

    fig.show()

# Example usage
display_trip_summary_and_plot('2024-08-01 00:00:00', '2024-08-10 23:59:59')
