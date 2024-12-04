import streamlit as st
import pandas as pd
import gdown
import requests 

# Debugging mode
DEBUG = True

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
        polygon_df['POSTCODE'] = polygon_df['POSTCODE'].str.strip().str.upper()

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
postcode = query_params.get("postcode", [""])[0].strip().replace(" ", "").upper() if query_params else None

if DEBUG:
    st.write("Query parameters:", query_params)
    st.write("Processed postcode:", postcode)

# Main logic
if postcode:
    if st.session_state["last_processed_postcode"] == postcode:
        st.info("Postcode already processed. Refresh to retry.")
    else:
        st.session_state["last_processed_postcode"] = postcode
        st.title("Modern Milkman Availability")
        st.write(f"Checking availability for postcode: {postcode}")

        result = polygon_df.loc[polygon_df['POSTCODE'] == postcode, 'POLYGON_SECTOR']
        sector = result.iloc[0] if not result.empty else None

        if sector:
            interested_users = unservicable_df[unservicable_df['POLYGON_SECTOR'] == sector].shape[0]
            st.warning(
                f"Sorry, we don’t deliver to your area yet. **{interested_users} people** are interested. "
                "Help us reach **50 sign-ups**!"
            )
            referral_link = f"https://themodernmilkman.co.uk/refer?postcode={postcode}"
            st.info(f"Share your referral link: [Link]({referral_link})")
            st.text_input("Enter your phone number to stay updated.")
        else:
            st.error("Area not found in database.")
else:
    st.error("No valid postcode provided.")
