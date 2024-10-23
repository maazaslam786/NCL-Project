# import pandas as pd

# # Load your cleaned data
# data_cleaned = pd.read_csv('cleaned_data22.csv')

# # Convert the 'time_stamp' column to datetime format
# data_cleaned['time_stamp'] = pd.to_datetime(data_cleaned['time_stamp'])

# # Filter rows where engine_rpm is above 4000
# high_rpm_data = data_cleaned[data_cleaned['engine_rpm'] > 4000]

# # Ensure the data is sorted by time for proper time frame detection
# high_rpm_data = high_rpm_data.sort_values(by='time_stamp')

# # Function to group consecutive high RPM periods into time frames and calculate additional metrics
# def get_high_rpm_timeframes(data):
#     if data.empty:
#         return pd.DataFrame()  # Return an empty DataFrame if no data is available

#     # Calculate the time differences between consecutive rows
#     data['time_diff'] = data['time_stamp'].diff()

#     # Define a threshold for considering consecutive rows as part of the same period (e.g., 1 minute)
#     threshold = pd.Timedelta(minutes=1)

#     # Create a group identifier based on the threshold
#     data['group'] = (data['time_diff'] > threshold).cumsum()

#     # Group by the identifier and calculate start, end times, duration, and average RPM of each high RPM period
#     high_rpm_periods = data.groupby('group').agg(
#         start_time=('time_stamp', 'min'),
#         end_time=('time_stamp', 'max'),
#         average_rpm=('engine_rpm', 'mean')  # Calculate average RPM within the period
#     ).reset_index(drop=True)

#     # Calculate the duration in seconds for each high RPM period
#     high_rpm_periods['duration'] = (high_rpm_periods['end_time'] - high_rpm_periods['start_time']).dt.total_seconds()

#     return high_rpm_periods

# # Get the high RPM time frames
# high_rpm_timeframes = get_high_rpm_timeframes(high_rpm_data)

# # Display the high RPM time frames
# if not high_rpm_timeframes.empty:
#     print("\nTime frames when engine RPM is above 4000:")
#     print(high_rpm_timeframes)
# else:
#     print("No periods found with engine RPM above 4000.")

import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
# Load your cleaned data
data_cleaned = pd.read_csv('combined_data.csv')

# Convert the 'time_stamp' column to datetime format
data_cleaned['time_stamp'] = pd.to_datetime(data_cleaned['time_stamp'])


rpm_threshold = 4000


high_rpm_data = data_cleaned[data_cleaned['engine_rpm'] > rpm_threshold]


high_rpm_data = high_rpm_data.sort_values(by='time_stamp')

# Function to group consecutive high RPM periods into time frames and calculate additional metrics
def get_high_rpm_timeframes(data):
    if data.empty:
        return pd.DataFrame() 

    # Calculate the time differences between consecutive rows
    data['time_diff'] = data['time_stamp'].diff()

    # Define a threshold for considering consecutive rows as part of the same period 
    threshold = pd.Timedelta(minutes=1)

    # Create a group identifier based on the threshold
    data['group'] = (data['time_diff'] > threshold).cumsum()

    # Group by the identifier and calculate start, end times, and average RPM of each high RPM period
    high_rpm_periods = data.groupby('group').agg(
        start_time=('time_stamp', 'min'),
        end_time=('time_stamp', 'max'),
        average_rpm=('engine_rpm', 'mean') 
    ).reset_index(drop=True)

    # Calculate the duration in seconds for each high RPM period
    high_rpm_periods['duration'] = (high_rpm_periods['end_time'] - high_rpm_periods['start_time']).dt.total_seconds()

    return high_rpm_periods


high_rpm_timeframes = get_high_rpm_timeframes(high_rpm_data)


plt.figure(figsize=(14, 7))
plt.plot(data_cleaned['time_stamp'], data_cleaned['engine_rpm'], label='Engine RPM', color='blue', alpha=0.6)

# Highlight the periods of high RPM by shading the areas
for _, row in high_rpm_timeframes.iterrows():
    plt.axvspan(row['start_time'], row['end_time'], color='red', alpha=0.3, label='High Strain Period' if _ == 0 else "")


plt.axhline(y=rpm_threshold, color='r', linestyle='--', label=f'Threshold RPM = {rpm_threshold}')

# Add labels and title
plt.title('Engine RPM with Highlighted High Strain Periods', fontsize=14)
plt.xlabel('Timestamp', fontsize=12)
plt.ylabel('Engine RPM', fontsize=12)
plt.legend()
plt.grid(True)


plt.show()

# Print high RPM timeframes
if not high_rpm_timeframes.empty:
    print("\nTime frames when engine RPM is above 4000:")
    print(high_rpm_timeframes)
else:
    print("No periods found with engine RPM above 4000.")



