import streamlit as st
import pandas as pd
import gdown
import requests

# Enable debug mode for better traceability
DEBUG = True

# URLs to download data files
polygon_file_url = "https://drive.google.com/uc?id=19cdI-kinFtT1CqpYRVCfrXvvk16rTkKA"
unservicable_file_url = "https://drive.google.com/uc?id=1nMI8Io9kLfOyNISUIFB44dzYWwi4hbE5&export=download"

# Function to download and load the data files
@st.cache_data
def load_data():
    try:
        polygon_file_path = "PolygonSectorsForPostcodes.csv"
        unservicable_file_path = "UnservicableUsers.csv"

        # Download files from Google Drive
        gdown.download(polygon_file_url, polygon_file_path, quiet=False)
        gdown.download(unservicable_file_url, unservicable_file_path, quiet=False)

        # Load and clean Polygon Sectors data
        polygon_df = pd.read_csv(polygon_file_path)
        polygon_df.columns = polygon_df.columns.str.strip().str.upper()
        polygon_df['POSTCODE'] = polygon_df['POSTCODE'].str.strip().str.upper()

        # Load and clean Unserviceable Users data
        unservicable_df = pd.read_csv(unservicable_file_path)
        unservicable_df.columns = unservicable_df.columns.str.strip().str.upper()
        unservicable_df['POLYGON_SECTOR'] = unservicable_df['POLYGON_SECTOR'].str.strip().str.upper()

        return polygon_df, unservicable_df
    except Exception as e:
        st.error("Failed to load data. Please try again later.")
        if DEBUG:
            st.exception(e)
        return None, None

# Load data
polygon_df, unservicable_df = load_data()

# Ensure data is loaded before proceeding
if polygon_df is None or unservicable_df is None:
    st.stop()

# Session state to avoid reprocessing
if "query_processed" not in st.session_state:
    st.session_state.query_processed = False

# Get query parameters from the URL
query_params = st.query_params
postcode = query_params.get("postcode", [""])[0].strip().replace(" ", "").upper() if query_params else None

if DEBUG:
    st.write("Query parameters received:", query_params)
    st.write("Processed postcode:", postcode)

# Main processing logic
if postcode and not st.session_state.query_processed:
    st.session_state.query_processed = True  # Mark the query as processed
    st.title("Modern Milkman Availability")
    st.write(f"Checking availability for postcode: {postcode}")

    try:
        # Find the polygon sector for the provided postcode
        result = polygon_df.loc[polygon_df['POSTCODE'] == postcode, 'POLYGON_SECTOR']
        sector = result.iloc[0] if not result.empty else None

        if sector:
            # Count interested users in the same polygon sector
            interested_users = unservicable_df[unservicable_df['POLYGON_SECTOR'] == sector].shape[0]
            st.warning(
                f"Sorry, we don’t deliver to your area yet. However, **{interested_users} people** in your area are interested in this service. "
                f"Help us reach **50 sign-ups** to bring delivery to your area!"
            )
            referral_link = f"https://themodernmilkman.co.uk/refer?postcode={postcode}"
            st.info(
                f"Share this referral link: [Referral Link]({referral_link}) "
                "to earn **£5 credit** for every sign-up!"
            )
            st.text_input("Enter your phone number to stay updated:")
        else:
            st.error("Sorry, we couldn't find your area in our database.")
    except Exception as e:
        st.error("An error occurred while processing your request. Please try again later.")
        if DEBUG:
            st.exception(e)
else:
    st.title("Modern Milkman Availability")
    if not postcode:
        st.error("Please provide a valid postcode in the query parameters.")
    elif st.session_state.query_processed:
        st.info("Postcode already processed. Refresh to try again.")

# Debug footer to show session state
if DEBUG:
    st.write("---")
    st.write("Session State:", st.session_state)
