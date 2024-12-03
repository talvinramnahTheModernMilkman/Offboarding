import streamlit as st
import pandas as pd
import gdown
import requests 

# Debug Mode
DEBUG = True

# File URLs
polygon_file_url = "https://drive.google.com/uc?id=19cdI-kinFtT1CqpYRVCfrXvvk16rTkKA"
unservicable_file_url = "https://drive.google.com/uc?id=1nMI8Io9kLfOyNISUIFB44dzYWwi4hbE5&export=download"

# Download and load the CSV files
@st.cache_data
def load_data():
    polygon_file_path = "PolygonSectorsForPostcodes.csv"
    gdown.download(polygon_file_url, polygon_file_path, quiet=False)
    polygon_df = pd.read_csv(polygon_file_path)
    polygon_df.columns = polygon_df.columns.str.strip().str.upper()
    polygon_df['POSTCODE'] = polygon_df['POSTCODE'].str.strip().str.upper()

    unservicable_file_path = "UnservicableUsers.csv"
    gdown.download(unservicable_file_url, unservicable_file_path, quiet=False)
    unservicable_df = pd.read_csv(unservicable_file_path)
    unservicable_df.columns = unservicable_df.columns.str.strip().str.upper()
    unservicable_df['POLYGON_SECTOR'] = unservicable_df['POLYGON_SECTOR'].str.strip().str.upper()

    return polygon_df, unservicable_df

# Load data
polygon_df, unservicable_df = load_data()

# Initialize session state to prevent duplicate processing
if "query_processed" not in st.session_state:
    st.session_state.query_processed = False

# Process query parameters
query_params = st.query_params
postcode = query_params.get("postcode", [""])[0].strip().replace(" ", "").upper()

if DEBUG:
    st.write("Query parameters received:", query_params)
    st.write("Processed postcode:", postcode)

# If a postcode is provided
if postcode and not st.session_state.query_processed:
    st.session_state.query_processed = True
    st.title("Modern Milkman Availability")
    st.write(f"Checking availability for postcode: {postcode}")

    # Get polygon sector
    result = polygon_df.loc[polygon_df['POSTCODE'] == postcode, 'POLYGON_SECTOR']
    sector = result.iloc[0] if not result.empty else None

    if sector:
        # Count interested users
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
else:
    st.title("Modern Milkman Availability")
    st.error("Please provide a postcode in the query parameters.")
