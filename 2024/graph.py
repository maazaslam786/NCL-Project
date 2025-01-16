import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

summary_df = pd.read_csv('summary_month_2024.csv')
summary_df['timeframe'] = pd.to_datetime(summary_df['timeframe'])

for idx, row in summary_df.iterrows():
    print("*****",row['timeframe'].strftime("%B %Y"),"*****")
    print('Average Speed:',row['average_speed'],'kmph')
    print('Maximum Speed:',row['max_speed'])
    print('Total Driving Time:',row['total_drive_time'],'minutes')
    print('Distance Travelled:',row['distance (km)'],'kms')
    print('Fuel Consumed:',row['fuel'],'liters')
    print('Mileage for the duration:',row['mileage'],'km/L')
    print('Engine Coolant Temperature:',row['coolant_temp'],'°C')
    print('Engine Overheat Percentage:',row['engine_overheat'],'%')
    print()


fig = go.Figure()

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['mileage'], 
                         mode='lines', name='Mileage', yaxis='y1'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['fuel'], 
                         mode='lines', name='Fuel Consumption', yaxis='y2'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['distance (km)'], 
                         mode='lines', name='Distance Travelled', yaxis='y3'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['coolant_temp'], 
                         mode='lines', name='Average Engine Coolant Temperature', yaxis='y4'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['total_drive_time'], 
                         mode='lines', name='Total Driving Time', yaxis='y5'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['max_speed'], 
                         mode='lines', name='Maximum speed', yaxis='y6'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['average_speed'], 
                         mode='lines', name='Average speed', yaxis='y7'))

fig.add_trace(go.Scatter(x=summary_df['timeframe'], y=summary_df['engine_overheat'], 
                         mode='lines', name='Engine Overheat Percent', yaxis='y8'))


fig.update_layout(
    title=f'Summary Data by Month',
    xaxis=dict(title='Month'),

    yaxis=dict(
        titlefont=dict(color="blue"),
        tickfont=dict(color="blue"),
        showticklabels=False
    ),

    yaxis2=dict(
        overlaying="y",
        showticklabels=False
    ),
    
    yaxis3=dict(
        overlaying="y",
        showticklabels=False
    ),
    
    yaxis4=dict(
        overlaying="y",
        showticklabels=False
    ),

    yaxis5=dict(
        overlaying="y",
        showticklabels=False
    ),
    yaxis6=dict(
        overlaying="y",
        showticklabels=False
    ),
    yaxis7=dict(
        overlaying="y",
        showticklabels=False
    ),
    yaxis8=dict(
        overlaying="y",
        showticklabels=False
    ),
    legend_title_text='Parameters'
)

print(summary_df)
fig.show()
