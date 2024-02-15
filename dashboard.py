import streamlit as st
from streamlit_folium import st_folium
import folium
import pickle
import matplotlib.pyplot as plt
from utils import plot_graphs


# Define a dictionary to map file names to DataFrame contents
dataframe_names = {
    'dataframe_0.pkl': 'airport_map',
    'dataframe_1.pkl': 'top_ten_flights',
    'dataframe_2.pkl': 'top_ten_profits',
    'dataframe_3.pkl': 'top5',
    'dataframe_4.pkl': 'delays',
    'dataframe_5.pkl': 'routes_map'
}

# Load the DataFrames from their respective pickle files
loaded_dataframes = {}
for filename, name in dataframe_names.items():
    with open(filename, 'rb') as f:
        loaded_dataframes[name] = pickle.load(f)

# Now you can access the loaded DataFrames using their names
airport_map = loaded_dataframes['airport_map']
top_ten_flights = loaded_dataframes['top_ten_flights']
top_ten_profits = loaded_dataframes['top_ten_profits']
top5 = loaded_dataframes['top5']
delays = loaded_dataframes['delays']
delays.sort_values(inplace=True)
routes_map = loaded_dataframes['routes_map']





# Title
st.title("Airline Route Analysis Dashboard")

# Sidebar
st.sidebar.header("Filters")
show_top_flights = st.sidebar.checkbox("Show Top 10 Busiest Routes")
show_top_profits = st.sidebar.checkbox("Show Top 10 Most Profitable Routes")
show_top5_recommendations = st.sidebar.checkbox("Show Top 5 Recommendations")

# Main content
if show_top_flights:    
    st.subheader("Top 10 Busiest Routes")
    st.dataframe(top_ten_flights)

if show_top_profits:
    st.subheader("Top 10 Most Profitable Routes")
    st.dataframe(top_ten_profits)

if show_top5_recommendations:
    st.subheader("Top 5 Recommendations")
    st.dataframe(top5)

    # Map visualization for top 5 recommendations
    st.subheader("Map Visualization for Top 5 Recommendations")
    m = folium.Map(location=[routes_map['lat_origin'].mean(), routes_map['lon_origin'].mean()], zoom_start=4)
    for index, row in routes_map.iterrows():
        if row['ORIGIN_IATA_CODE'] in top5['ORIGIN_IATA_CODE'].values and row['DEST_IATA_CODE'] in top5['DEST_IATA_CODE'].values:
            folium.Marker(location=[row['lat_origin'], row['lon_origin']], popup=str(f"{row['ORIGIN_IATA_CODE']}-> {row['DEST_IATA_CODE']}") + '<br>'+ str(f"Profit: {row['Profit']:,}")).add_to(m)
            folium.Marker(location=[row['lat_dest'], row['lon_dest']], popup=str(f"{row['DEST_IATA_CODE']}-> {row['ORIGIN_IATA_CODE']} ") + '<br>'+str(f"Profit: {row['Profit']:,}")).add_to(m)
            folium.PolyLine(locations=[[row['lat_origin'], row['lon_origin']], [row['lat_dest'], row['lon_dest']]], color='orange').add_to(m)
    
    st_map = st_folium(m, width=700, height=450)
    st.write(st_map)

# Visualizations

st.subheader("Most Busiest Routes")
fig, ax = plot_graphs(top_ten_flights,index_name='ORIGIN_IATA_CODE', x_label='Origin Airport (IATA Code)', y_label='Total flights', title='Busiest Routes by Total Flights')
st.pyplot(fig)

st.subheader("Most Profitable Routes")
fig, ax = plot_graphs(top_ten_profits,index_name='ORIGIN_IATA_CODE' , df_col='Profit', x_label='Origin Airport (IATA Code)', y_label='Total Profit ($)', title='Profitability of Most Profitable Routes')
st.pyplot(fig)


st.subheader("Departure Delays Distribution")
fig, ax = plot_graphs(delays,index_name=None, x_label='Origin Airport (IATA Code)', y_label='Average Departure Delay (min)', title='Average Flight Delay by Origin Airport')
st.pyplot(fig)



# Key insights and conclusions
st.subheader("Key Insights and Key Performance Indicators")

# LAX-SFO
st.write("**LAX-SFO:**")
st.write("This route, linking Los Angeles International Airport (LAX) and San Francisco International Airport (SFO), stands out as the busiest in the US, witnessing 8340 roundtrips in Q1 2019. It also boasts the highest profitability, generating $316 million in revenue. While competition from major carriers is a concern, the substantial demand and profit potential make it an attractive option for new entrants.")

# LGA-ORD
st.write("**LGA-ORD:**")
st.write("Connecting New York's LaGuardia Airport (LGA) and Chicago's O'Hare International Airport (ORD) presents a promising market opportunity. With 7156 flights in Q1 2019 and a profit of $268 million, it ranks as the second busiest and second most profitable route. However, LGA's slot and gate constraints should be taken into account.")

# LAS-LAX
st.write("**LAS-LAX:**")
st.write("In Q1 2019, this route between Las Vegas (LAS) and Los Angeles (LAX) recorded 6511 roundtrips, generating $255 million in profit. Las Vegas serves as a robust origin/destination market, while LAX facilitates onward connections.")

# JFK-LAX
st.write("**JFK-LAX:**")
st.write("Similar to LAX-SFO, JFK-LAX links two major hubs with substantial business and leisure travel. While ranking as the fourth busiest route with 6,320 round trips and fourth profitable route with $248 million, it overlaps with LAX-SFO, posing a challenge.")

# HNL-OGG
st.write("**HNL-OGG:**")
st.write("Despite not being among the top five busiest routes, HNL-OGG (Honolulu to Kahului) ranks as the fifth most profitable, earning $205 million in Q1 2019. Requiring only 2107 flights to break even, it connects two major Hawaiian airports, catering to the leisure market and presenting a unique opportunity.")

# Display Key Performance Indicators
st.subheader("Key Performance Indicators (KPIs)")
st.write("Here are some recommended KPIs for tracking the performance of new routes:")
st.write("- Number of monthly/quarterly round-trip flights completed.")
st.write("- Percent of on-time arrivals and departures.")
st.write("- Average monthly/quarterly passenger loads.")
st.write("- Passenger revenue per available seat mile (PRASM).")
st.write("- Cost per available seat mile (CASM).")
st.write("- Average revenue per passenger.")
st.write("- Ancillary revenue per passenger (e.g., baggage fees).")
st.write("- Customer satisfaction scores.")
