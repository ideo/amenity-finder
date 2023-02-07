import streamlit as st
import pandas as pd

import detroit as detroit


st.header("Detroit Amenity Finder")
graph, amenities = detroit.download_dowtown_detroit()


downtown_parking = {
    "1234 Library St":          "1234 Library St, Detroit, MI 48226",
    "1188 Farmer St":           "1188 Farmer St, Detroit, MI 48226",
    "Bricktown Parking Garage": "419 E Fort St, Detroit, MI 48226",
}

col1, col2 = st.columns(2)
with col1:
    label="Choose a Bedrock Detroit Parking Structure"
    garage = st.selectbox(label, options=downtown_parking.keys())
    address = downtown_parking[garage]

with col2:
    label="How Far Are You Willing to Walk?"
    travel_time = st.number_input(label, value=5, min_value=1, max_value=15)


fig, walkable_amenities = detroit.walking_isochrone(graph, address, travel_time, amenities, garage)
st.pyplot(fig, dpi=300)

st.write(f"The following amenities can be within {travel_time} minutes of {garage}.")
st.dataframe(pd.DataFrame(walkable_amenities["amenity"].value_counts()).T)
