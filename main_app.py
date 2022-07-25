#import knihoven

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy
import altair as alt
import streamlit as st
import plotly
from PIL import Image
import h3
import datetime

#conection engine do databaze
conn_string = "mysql+pymysql://student2:eh2BjVEpYmDcT96E@data.engeto.com:3306/data_academy_02_2022"
engine = sqlalchemy.create_engine(conn_string)

#nacteni dat do dataframu
df_bikes = pd.read_sql('SELECT * FROM edinburgh_bikes', engine)
df_weather = pd.read_sql('SELECT * FROM edinburgh_weather', engine)

#cisteni dat od preklepu
df_bikes['start_station_name'] = df_bikes['start_station_name'].replace({
    'Brunswick Place - Virtual':'Brunswick Place',
    'Bruntsfield links':'Bruntsfield',
    'Newhaven Road / Dudley Gardens':'Dudley Gardens',
    'Hillside Crescent 2':'Hillside Crescent 1',
    'Sustrans - walk cycle event':'Haymarket - Murrayfield Rugby Event',
    'RHC - Edinburgh Festival Camping (05th to 26th August)':'Royal Highland Show - West Gate (19th to 23rd June)',
    'Meadow Place 2':'Meadow Place',
    'The Tron':'Hunter Square',
    'Picardy Place':'Picady Place'
})
df_bikes['end_station_name'] = df_bikes['end_station_name'].replace({
    'Brunswick Place - Virtual':'Brunswick Place',
    'Bruntsfield links':'Bruntsfield',
    'Newhaven Road / Dudley Gardens':'Dudley Gardens',
    'Hillside Crescent 2':'Hillside Crescent 1',
    'Sustrans - walk cycle event':'Haymarket - Murrayfield Rugby Event',
    'RHC - Edinburgh Festival Camping (05th to 26th August)':'Royal Highland Show - West Gate (19th to 23rd June)',
    'Meadow Place 2':'Meadow Place',
    'The Tron':'Hunter Square',
    'Picardy Place':'Picady Place'
})

#nastaveni layoutu pro stranku
st.set_page_config(page_title='Python project',page_icon='checkered_flag', layout='wide')

st.markdown("<h1 style='text-align: center; color: black;'>Edinburgh Bikes</h1>", unsafe_allow_html=True)


#sidebar pro vyber dat
page = st.sidebar.selectbox('Choose your interests', ('Home', 'Standard description', 'Analysis'), index=0)

#uvodni informace
if page == 'Home':
    link = '[GitHub](https://github.com/AndreaDvorakova/ENGETO_Data_Academy_Python_project.git)'
    st.markdown("<span style='text-align: center; color: black;'>In Edinburgh, as in other cities, the bike sharing system works - there are stations with bikes in the city, you can borrow one and then return it at another station. The problem is that in some stations bikes regularly accumulate and in others they are missing. The bike operator, Just Eat Cycles, has commissioned a project to make the system more efficient.</span>", unsafe_allow_html=True)
    st.markdown("<span style='text-align: center; color: black;'>Feel free to explore all the subpages and if you are interested in the code, visit the link:</span>", unsafe_allow_html=True)
    st.markdown(link, unsafe_allow_html=True)
    st.image("https://a.cdn-hotels.com/gdcs/production73/d1723/35b8f7e3-14c4-4d53-ae2f-5f7f6adb6aac.jpg?impolicy=fcrop&w=1600&h=1066&q=medium",
            use_column_width=True)
    

#prvni stranka obsahujici standardni descriptivni statistiku    
elif page == 'Standard description':
    subpage = st.sidebar.radio('Subpage', ['Number of rented/returned bikes', 'Most/least busy station', 'Potential surplus/shortage', 'Distance between stations', 'Rental duration'])

    #dataframe pro secteni pujcek podle start_station_id
    df_start = (df_bikes
                [['start_station_id', 'start_station_name']]
                .set_index(['start_station_id', 'start_station_name'])
                .rename_axis(['station_id', 'start_station_name']))

    df_start = df_start.reset_index()

    df_start = df_start.groupby(['station_id', 'start_station_name']).size().reset_index(name='count_start')

    #dataframe pro secteni pujcek podle end_station_id
    df_end = (df_bikes
                [['end_station_id', 'end_station_name']]
                .set_index(['end_station_id', 'end_station_name'])
                .rename_axis(['station_id', 'end_station_name']))

    df_end = df_end.reset_index()
    df_end = df_end.groupby(['station_id', 'end_station_name']).size().reset_index(name='count_end')
        
    #spojeni dvou dataframu
    df_activity = df_end[['station_id', 'end_station_name','count_end']].join(df_start[['count_start']], rsuffix ='_start')

    if subpage == 'Number of rented/returned bikes':

        st.markdown("<span style='text-align: center; color: black;'>Let's look into some basics about our data. The two graphs below shoving us the overall sum of rentals/returns in each station. The graphs are interactive, so feel free to look more into the detail, as on the high-level view there is too much difference between the extreme values. By clicking on columns you get the specific information about the sum of rentals/returns.</span>", unsafe_allow_html=True)              
        
        #tvorba grafu z start a end dat
        c1, c2= st.columns((1,1))

        c1.markdown("<h2 style='text-align: center; color: grey;'>Num.of rented bikes at start station</h2>", unsafe_allow_html=True)
        start_chart = alt.Chart(df_activity).mark_bar().encode(
            x=alt.X('count_start', axis=alt.Axis(title='Num.of rented bikes')),
            y=alt.Y('end_station_name', axis=alt.Axis(title='Station'), sort='-x'),
            tooltip=[alt.Tooltip('end_station_name', title='Station'), 
                    alt.Tooltip('count_start', title='No.of bikes'),
                    alt.Tooltip('station_id', title='Station ID')]
        ).interactive()

        c2.markdown("<h2 style='text-align: center; color: grey;'>Num.of returned bikes at end station</h2>", unsafe_allow_html=True)
        end_chart = alt.Chart(df_activity).mark_bar().encode(
            x=alt.X('count_end', axis=alt.Axis(title='Num.of returned bikes')),
            y=alt.Y('end_station_name', axis=alt.Axis(title='Station'), sort='-x'),
            tooltip=[alt.Tooltip('end_station_name', title='Station'), 
                    alt.Tooltip('count_end', title='No.of bikes'), 
                    alt.Tooltip('station_id', title='Station ID')]
        ).interactive()

        c1.altair_chart(start_chart, use_container_width=True)
        c2.altair_chart(end_chart, use_container_width=True)

    elif subpage == 'Most/least busy station':
        #suma vratek a vypujcek pro zjisteni frekventovanosti stanice
        df_activity['sum_of_rental_return']  = df_activity['count_start'] + df_activity['count_end']
        df_activity = df_activity.set_index(['station_id', 'end_station_name'])

        temporary_df = (df_bikes[['start_station_id', 'start_station_latitude', 'start_station_longitude']]
                        .set_index(['start_station_id', 'start_station_latitude', 'start_station_longitude'])
                        .rename_axis(['station_id', 'start_station_latitude', 'start_station_longitude']))
        df_activity = df_activity.join(temporary_df).drop_duplicates().reset_index()

        #uvodni komentar 
        st.markdown("<span style='text-align: center; color: black;'>To identify the most and the least busy station in Edinburgh I used the sum of rented and returned bikes in each station. The graph below is representing these data. For easy understanding the min and max values are highlithed.</span>", unsafe_allow_html=True)
        
        #graf + zvyrazneni min/max hodnot
        busy_chart = alt.Chart(df_activity).mark_bar().encode(
            x=alt.X('station_id', axis=alt.Axis(title='station')),
            y=alt.Y('sum_of_rental_return', axis=alt.Axis(title='sum'), sort='-x'),
            tooltip=[alt.Tooltip('station_id', title='Station'), 
                    alt.Tooltip('sum_of_rental_return', title='sum')],
            color=alt.condition((alt.datum.sum_of_rental_return == 24018.0) | (alt.datum.sum_of_rental_return == 5.0),
                   alt.value("red"), alt.value("navy"))
        ).interactive()

        st.altair_chart(busy_chart, use_container_width=True)       

        #min a max hodnoty
        c3, c4, c5 = st.columns((1,1,2))
        c3.markdown("<span style='text-align: center; color: black;'>Min.value: </span>", unsafe_allow_html=True)
        c3.write(df_activity.groupby('station_id')['sum_of_rental_return'].min().sort_values(ascending=True).reset_index().iloc[0], use_container_width=True)
        c4.markdown("<span style='text-align: center; color: black;'>Max.value: </span>", unsafe_allow_html=True)
        c4.write(df_activity.groupby('station_id')['sum_of_rental_return'].max().sort_values(ascending=False).reset_index().iloc[0], use_container_width=True, align='center')

        #prehled vsech podkladovych dat pro tuto stranku
        st.markdown("<span style='text-align: center; color: black;'>The data for each station is represented in the table below.</span>", unsafe_allow_html=True)
        st.write(df_activity) 


    elif subpage == 'Potential surplus/shortage':
        #uvodni komentar 
        st.markdown("<span style='text-align: center; color: black;'>With difference between the returns and the rentals I would like to demonstrate the station with potential surplus or shortage.</span>", unsafe_allow_html=True)
        
        #rozdil vratek a vypujcek pro zjisteni stanice, kde kola chybi a kde se hodne vraci, 5 + 5 stanic, kde se nejvic pujcuje/vraci 
        df_activity['difference'] = df_activity['count_end'] - df_activity['count_start']
        df_surplus = df_activity.sort_values(by=['difference'], ascending=False).iloc[:5]
        df_shortage = df_activity.sort_values(by=['difference'], ascending=True).iloc[:5]

        #graf
        df_difference = (df_activity[['station_id', 'count_end', 'count_start', 'difference']])
        fig, ax = plt.subplots(figsize=(24,8))
        df_difference.plot(x='station_id', ax=ax, linewidth=2, grid=True, title='Number of rented/returned bikes and difference btw them')
        st.write(fig)

        #5 + 5 stanic, kde se nejvic pujcuje/vraci
        c6, c7 = st.columns((1,1))
        c6.markdown("<span style='text-align: center; color: black;'>Five stations with potential surplus (most bike returns): </span>", unsafe_allow_html=True)
        c6.write(df_surplus)
        c7.markdown("<span style='text-align: center; color: black;'>Five stations with potential shortage (most rented bikes): </span>", unsafe_allow_html=True)
        c7.write(df_shortage)

        #prehled vsech podkladovych dat pro stranku
        st.markdown("<span style='text-align: center; color: black;'>The data for each station is represented in the table below.</span>", unsafe_allow_html=True)
        st.write(df_activity)

    elif subpage == 'Distance between stations':
        st.markdown("<h2 style='text-align: center; color: grey;'>Distances between the start and end station</h2>", unsafe_allow_html=True)
        #uvodni komentar
        st.markdown("<span style='text-align: center; color: black;'>The data for each station is represented in the table below, the distances between the stations is in the last column.</span>", unsafe_allow_html=True)
        #vypocet vzdalenosti mezi start a end station
        coords = df_bikes[['start_station_latitude', 'start_station_longitude', 'end_station_latitude', 'end_station_longitude']]
        df_bikes['distance_btw_stations'] = df_bikes.apply(lambda row: h3.point_dist((row['start_station_latitude'], row['start_station_longitude']),(row['end_station_latitude'], row['end_station_longitude'])), axis=1)
        st.write(df_bikes)


    elif subpage == 'Rental duration':
        #uvodni komentar
        st.markdown("<span style='text-align: center; color: black;'>Data were categorized by duration in minutes. The outlier values were marked as edge values. The graph is representing the count of records for each cathegory. The share of each column is compared to the sum of all records and represendet by the percent in the tooltip.</span>", unsafe_allow_html=True)
        
        df_bikes['dur_in_min'] = (df_bikes['duration'] / 60).astype(int)
        #funkce pro doplneni intervalu do dataframe
        def f(row):
            if row['dur_in_min'] < 60:
                val = '0 - 60 min'
            elif row['dur_in_min'] < 120:
                val = '60 - 120 min'
            elif row['dur_in_min'] < 180:
                val = '120 - 180 min'
            elif row['dur_in_min'] < 240:
                val = '180 - 240 min' 
            elif row['dur_in_min'] < 300:
                val = '240 - 300 min'
            elif row['dur_in_min'] < 360:
                val = '300 - 360 min'
            elif row['dur_in_min'] < 420:
                val = '360 - 420 min'
            elif row['dur_in_min'] < 480:
                val = '420 - 480 min'
            elif row['dur_in_min'] < 540:
                val = '480 - 540 min'
            elif row['dur_in_min'] < 600:
                val = '540 - 600 min'
            elif row['dur_in_min'] < 660:
                val = '600 - 660 min'
            elif row['dur_in_min'] < 720:
                val = '660 - 720 min'
            elif row['dur_in_min'] < 780:
                val = '720 - 780 min'
            elif row['dur_in_min'] < 860:
                val = '780 - 860 min'
            elif row['dur_in_min'] < 920:
                val = '860 - 920 min'
            elif row['dur_in_min'] < 1000:
                val = '920 - 1000 min'
            else:    
                val = 'edge values'
            return val
        #aplikace funkce na datech
        df_bikes['interval'] = df_bikes.apply(f, axis=1)

        #dataframe pro graf trvani vypujcky a vypocet procentualniho zastoupeni na celku
        df_duration = df_bikes.groupby('interval').count()['index']
        df_duration = df_duration.reset_index()                                
        df_duration['prct'] = df_duration['index'].transform(lambda x: x/x.sum())
        df_duration = df_duration.reset_index() 

        #graf - pocet vypujcek pro jednotlive intervaly
        duration_chart = alt.Chart(df_duration).mark_bar().encode(
                        x=alt.X('interval', axis=alt.Axis(title='Interval')),
                        y=alt.Y('index', axis=alt.Axis(title='Sum of records')),
                        tooltip=[alt.Tooltip('index:Q', title='Sum:'), 
                                alt.Tooltip('interval:N', title='Interval:'),
                                alt.Tooltip('prct:Q', format='.2%', title='Percent:')]
                        ).interactive()

        st.altair_chart(duration_chart, use_container_width=True)  
 

elif page == 'Analysis':
    #subpage pod analysis
    section = st.sidebar.radio('Section', ['Demand over time', 'Causes of demand fluctuation', 'Weather vs demand', 'Demand vs weekday'])
    
    #uprava datumu pro pozdejsi analyzu
    df_bikes['started_at'] = pd.to_datetime(df_bikes['started_at'], format='%Y-%m-%d %H:%M', utc=True, errors='coerce')
    df_bikes['date'] = df_bikes['started_at'].dt.strftime('%Y-%m-%d')
    df_bikes['year'] = df_bikes['started_at'].dt.strftime('%Y')
    df_bikes['month'] = df_bikes['started_at'].dt.strftime('%m').astype(int)
    df_bikes['day'] = df_bikes['started_at'].dt.strftime('%d')
    df_bikes['month_day'] = df_bikes['started_at'].dt.strftime('%m-%d')
    df_bikes['year_month'] = df_bikes['started_at'].dt.strftime('%Y-%m')
    df_bikes['day_in_week'] = df_bikes['started_at'].dt.day_name()
    df_bikes['time'] = df_bikes['started_at'].dt.strftime('%H:%M')
    df_bikes['hour'] = df_bikes['started_at'].dt.strftime('%H')

    if section == 'Demand over time':
        #uvodni komentar
        st.markdown("<span style='text-align: center; color: black;'>The graph below represents the demand over the whole time of functioning. The biggest peek was in May, 2020.</span>", unsafe_allow_html=True)
        
        #tvorba dataframe pro zobrazeni v grafu
        df_in_time = df_bikes.groupby('year_month').count()['index']
        df_in_time = df_in_time.reset_index()

        #graf - vyvoj poptavky za cele obdobi
        time_chart = alt.Chart(df_in_time).mark_line(point = True).encode(
            x = alt.X('year_month', title='Month in year', axis=alt.Axis(labelAngle=-45)),
            y = alt.Y('index', title='Sum of rentals'),
            tooltip=[alt.Tooltip('year_month', title='Month in year:'), 
                    alt.Tooltip('index', title='Sum.of records')]
            ).properties(title = 'Bike rental in time').interactive()
        st.altair_chart(time_chart, use_container_width=True)

    elif section == 'Causes of demand fluctuation':
        #uvodni komentar
        st.markdown("<span style='text-align: center; color: black;'>As a potencial cause of fluctuation in demand after bikes I see the connection with the months. The demand is the highest in summer months as it is demonstrated in the graph below.</span>", unsafe_allow_html=True)
        
        #tvorba dataframe pro zobrazeni v grafu
        df_months = df_bikes.groupby(['year','month']).count()['index']
        df_months = df_months.reset_index()
        selection = alt.selection_multi(fields = ['year'], bind = 'legend')

        #graf - vykyvy v mesicich
        month_chart = alt.Chart(df_months).mark_line(point = True).encode(
                x = alt.X("month:O", title="Months", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("index:Q", title='Count of records'),
                color=alt.Color("year:N"),
                tooltip=[alt.Tooltip('month', title='Month:'), 
                        alt.Tooltip('index', title='Sum.of records')],
                opacity = alt.condition(selection, alt.value(1), alt.value(0.2))
        ).properties(title="Demand in months"                  
        ).interactive().add_selection(selection)
        st.altair_chart(month_chart, use_container_width=True)

        #komentar k dalsimu grafu o dnech
        st.markdown("<span style='text-align: center; color: black;'>Also the day in the week seems to have an effect on the demand. Weekends are more busy than the working days.</span>", unsafe_allow_html=True)
        
        #tvorba dataframe pro zobrazeni v grafu
        df_week_days = df_bikes.groupby(['year','day_in_week']).count()['index']
        df_week_days = df_week_days.reset_index()

        #graf - poptavka ve dnech
        week_chart = alt.Chart(df_week_days).mark_bar().encode(
                    x=alt.X('day_in_week', title='Day in week'),
                    y=alt.Y('index', title='Sum of records'),
                    color='year',
                    tooltip=[alt.Tooltip('day_in_week', title='Day:'), 
                        alt.Tooltip('index', title='Sum.of records:')]
                    ).properties(title='Demand in weekdays')
        st.altair_chart(week_chart, use_container_width=True)

        #komentar k dalsimu grafu o hodinach
        st.markdown("<span style='text-align: center; color: black;'>In working days the first peek of renting is between 6AM and 8AM which could be caused by the fact that people are renting bikes to get to their work. The second peek is probably caused by the trip back home from work as it is around 3PM and 5PM. During the weekends the rise of demand is more constant and it stagnates at midday and drops after 3PM.</span>", unsafe_allow_html=True)
                
        #tvorba dataframe pro zobrazeni v grafu
        df_hours = df_bikes.groupby(['day_in_week','hour']).count()['index']
        df_hours = df_hours.reset_index()

        #graf - poptavka v hodinach
        selection = alt.selection_multi(fields = ['day_in_week'], bind = 'legend')
        df_hours['tooltip_hour'] = (df_hours['hour'].astype(str)) + '-' + ((df_hours['hour'].astype(int) + 1).astype(str))
        day_chart = alt.Chart(df_hours).mark_line(point = True).encode(
                    x = alt.X("hour:O", title="Hour", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("index:Q", title='Count of records'),
                    color=alt.Color("day_in_week:N"),
                    tooltip=[alt.Tooltip('tooltip_hour', title='Hour:'), 
                        alt.Tooltip('index', title='Sum.of records')],
                    opacity = alt.condition(selection, alt.value(1), alt.value(0.2))
                    ).properties(title="Demand in hours").interactive().add_selection(selection)
        st.altair_chart(day_chart, use_container_width=True)
        
    elif section == 'Weather vs demand':

        #vyber relevantnich hodnot z pocasi
        df_weather = df_weather.query("date >= '2018-09-15' & date <= '2021-06-30'")
        #zmena datatype na int, float relevantnich sloupcu a vyber pouze novych sloupcu do databaze
        df_weather['temp_split'] = df_weather['temp'].str.split('°')
        df_weather['temp1'] = df_weather['temp_split'].apply(lambda x: x[0]).astype(int)
        df_weather['wind_split'] = df_weather['wind'].str.split(' ')
        df_weather['wind1'] = df_weather['wind_split'].apply(lambda x: x[0]).astype(int)
        df_weather['rain_split'] = df_weather['rain'].str.split(' ')
        df_weather['rain1'] = df_weather['rain'].str.split(' ').apply(lambda x: x[0]).astype(float)
        df_weather = df_weather[['date', 'temp1', 'wind1', 'rain1']]
        #vypocet prumernych hodnot za jednotlive dny
        df_weather_1 = df_weather.groupby('date').agg({'temp1': 'mean', 'wind1': 'mean', 'rain1': 'mean'}).reset_index()
        #propojeni dat o vypujckach a pocasi do jedne databaze
        df_bike_weather = df_bikes.set_index('date').join(df_weather_1.set_index('date')).reset_index()
        df_bike_weather = df_bike_weather.dropna()
        #pocet vypujcek po dnech a data o pocasi
        temp_bike_base = df_bike_weather.groupby(['date', 'temp1', 'rain1', 'wind1'])['index'].count()
        temp_bike_base = temp_bike_base.reset_index()
        temp_bike_base['date1'] = pd.to_datetime(temp_bike_base['date']).dt.normalize()

        #komentar ke strance
        st.markdown("<span style='text-align: center; color: black;'>There is no significant similarity between the number of rentals and the elements of the weather as rain, temperature or wind. Some similar movementst are between the temperature and the rentals, but the windiness and rain is volatile. The charts below representing the number of rentals, average temprature for each day, average windiness and rain in days. For detail you can zoom in.</span>", unsafe_allow_html=True)
                
        #graf - pocty pujcech ve dnech
        bike_chart = alt.Chart(temp_bike_base).mark_line(point = True).encode(
                    x = alt.X('date1', title='Date', axis=alt.Axis(labelAngle=-45)),
                    y = alt.Y('index', title='Sum of rentals'),
                    tooltip=[alt.Tooltip('date1', title='Date:'), 
                            alt.Tooltip('index', title='Sum of rentals:')]
                    ).properties(title = 'Sum of rentals by days').interactive()
        st.altair_chart(bike_chart, use_container_width=True)
              
        #graf - prumerne teploty ve dnech
        temp_chart = alt.Chart(temp_bike_base).mark_line(point = True).encode(
                    x = alt.X('date1', title='Date', axis=alt.Axis(labelAngle=-45)),
                    y = alt.Y('temp1', title='Average temp'),
                    tooltip=[alt.Tooltip('date1', title='Date:'), 
                            alt.Tooltip('temp1', title='Daily avg temp:')]
                    ).properties(title = 'Daily average temperature').interactive()
        st.altair_chart(temp_chart, use_container_width=True)

        #graf - dest ve dnech
        rain_chart = alt.Chart(temp_bike_base).mark_line(point = True).encode(
                    x = alt.X('date1', title='Date', axis=alt.Axis(labelAngle=-45)),
                    y = alt.Y('rain1', title='Average rain'),
                    tooltip=[alt.Tooltip('date1', title='Date:'), 
                            alt.Tooltip('rain1', title='Avg rain:')]
                    ).properties(title = 'Average rain in days').interactive()
        st.altair_chart(rain_chart, use_container_width=True)

        #graf - vitr ve dnech
        wind_chart = alt.Chart(temp_bike_base).mark_line(point = True).encode(
                    x = alt.X('date1', title='Date', axis=alt.Axis(labelAngle=-45)),
                    y = alt.Y('wind1', title='Average wind'),
                    tooltip=[alt.Tooltip('date1', title='Date:'), 
                            alt.Tooltip('wind1', title='Avg wind:')]
                    ).properties(title = 'Windiness in days').interactive()
        st.altair_chart(wind_chart, use_container_width=True)
        
    elif section == 'Demand vs weekday':

        #komentar k dalsimu grafu o hodinach
        st.markdown("<span style='text-align: center; color: black;'>The chart below is showing the sum of rentals is each weekday and the coloring is distinguishing the data in years.</span>", unsafe_allow_html=True)     

        df_week_days = df_bikes.groupby(['year','day_in_week']).count()['index']
        df_week_days = df_week_days.reset_index()
        week_chart = alt.Chart(df_week_days).mark_bar().encode(
                    x=alt.X('day_in_week', title='Day in week'),
                    y=alt.Y('index', title='Sum of records'),
                    color='year',
                    tooltip=[alt.Tooltip('day_in_week', title='Day:'), 
                        alt.Tooltip('index', title='Sum.of records:')]
                    ).properties(title='Demand in weekdays')
        st.altair_chart(week_chart, use_container_width=True)
   

