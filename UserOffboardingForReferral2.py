import streamlit as st
import pandas as pd
import gdown
import requests

# Debugging mode
DEBUG = None

# Data file URLs
polygon_file_url = "https://drive.google.com/uc?id=19cdI-kinFtT1CqpYRVCfrXvvk16rTkKA"
unservicable_file_url = "https://drive.google.com/uc?id=1nMI8Io9kLfOyNISUIFB44dzYWwi4hbE5&export=download"

# Load data function
@st.cache_data
def load_data():
    try:
        polygon_file_path = "PolygonSectorsForPostcodes.csv"
        unservicable_file_path = "UnservicableUsers.csv"

        # Download and load data
        gdown.download(polygon_file_url, polygon_file_path, quiet=False)
        gdown.download(unservicable_file_url, unservicable_file_path, quiet=False)

        polygon_df = pd.read_csv(polygon_file_path)
        polygon_df.columns = polygon_df.columns.str.strip().str.upper()
        # Normalize postcodes in polygon_df
        polygon_df['POSTCODE'] = polygon_df['POSTCODE'].str.strip().str.replace(" ", "").str.upper()

        unservicable_df = pd.read_csv(unservicable_file_path)
        unservicable_df.columns = unservicable_df.columns.str.strip().str.upper()
        unservicable_df['POLYGON_SECTOR'] = unservicable_df['POLYGON_SECTOR'].str.strip().str.upper()

        return polygon_df, unservicable_df
    except Exception as e:
        st.error("Failed to load data.")
        if DEBUG:
            st.exception(e)
        return None, None

# Load data
polygon_df, unservicable_df = load_data()

if polygon_df is None or unservicable_df is None:
    st.stop()

# Initialize session state
if "last_processed_postcode" not in st.session_state:
    st.session_state["last_processed_postcode"] = None

# Get query parameters
query_params = st.query_params
#st.write("Raw query parameters:", query_params)  # Debug the raw input

# Extract and normalize postcode
if "postcode" in query_params:
    postcode_raw = query_params["postcode"]
    if isinstance(postcode_raw, list):  # Handle the case where query_params returns a list
        postcode = postcode_raw[0]  # Get the first item
    else:
        postcode = postcode_raw  # Directly use the string value
    postcode = postcode.strip().replace(" ", "").upper()  # Normalize the postcode
else:
    postcode = None

# Debugging outputs
#st.write("Raw query parameters:", query_params)  # Debug the raw input
#st.write("Extracted raw postcode:", postcode_raw if "postcode" in query_params else None)  # Debug raw value
#st.write("Normalized postcode:", postcode)  # Debug the processed postcode

# Debugging outputs
#if DEBUG:
    #st.write("Query parameters:", query_params)
    #st.write("Processed postcode:", postcode)

# HUB_ID to Hub Name Mapping
hub_names = {
    25: "Swindon",
    11: "Lichfield",
    15: "Preston",
    6: "Nottingham",
    5: "Leeds",
    19: "Sidcup",
    18: "Harrow",
    1: "Jacksons SK",
    7: "York",
    30: "Warrington",
    22: "Southampton",
    13: "Wellingborough",
    17: "Newcastle",
    9: "Sheffield",
    20: "Guildford",
}

# Main logic
if postcode:
    if st.session_state["last_processed_postcode"] == postcode:
        st.info("Postcode already processed. Refresh to retry.")
    else:
        st.session_state["last_processed_postcode"] = postcode
        st.title("Modern Milkman postcode checker")
        st.write(f"Checking milk rounds near: {postcode}")

        # Debug matching logic
        matching_entries = polygon_df[polygon_df['POSTCODE'] == postcode]
        #st.write("Matching entries in polygon_df:", matching_entries)

        # Find the sector for the given postcode
        result = polygon_df.loc[polygon_df['POSTCODE'] == postcode, 'POLYGON_SECTOR']
        sector = result.iloc[0] if not result.empty else None

        if sector:
            # Find the HUB_ID for the sector
            hub_result = unservicable_df.loc[unservicable_df['POLYGON_SECTOR'] == sector, 'HUB_ID']
            hub_id = hub_result.iloc[0] if not hub_result.empty else None

            if hub_id:
                # Get the hub name
                hub_name = hub_names.get(hub_id, "Unknown Hub")

                # Count the number of users in the same HUB_ID
                interested_users = unservicable_df[unservicable_df['HUB_ID'] == hub_id].shape[0]
                st.warning(
                    f"Sorry, we don’t deliver to your area yet, but we are looking at expanding into **{hub_name}**. "
                    f"**{interested_users} people** are interested. Get {hub_name} to 5000 sign ups by sharing the link below to get us in your area!"
                )
                referral_link = f"https://themodernmilkman.co.uk/refer?postcode={postcode}"
                st.info(f"Share your referral link: https://themodernmilkman.co.uk/?utm_source=GetModernMilkmanToYourArea")
                st.text_input("Enter your phone number to stay updated.")
            else:
                st.error("HUB_ID not found for your area.")
        else:
            st.error("We could not find your postcode :( double check and ensure it's valid.")
else:
    st.error("No valid postcode provided.")
