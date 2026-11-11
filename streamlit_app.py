import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
import time

# Set Streamlit page configuration
st.set_page_config(
    page_title="Nightscout Glucose Chart",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Title
st.title("📈 Nightscout Blood Glucose Curve")

# Sidebar Inputs
st.sidebar.header("Nightscout API Configuration")

# Input for Nightscout Base URL
base_url = st.sidebar.text_input(
    "Nightscout Base URL",
    value="https://your-nightscout-url.com",
    help="Enter your Nightscout base URL (e.g., https://your-nightscout-url.com)",
)

# Input for API Secret or Token
auth_option = st.sidebar.selectbox(
    "Authentication Method",
    ("API Secret", "JWT Token"),
    help="Choose your authentication method for accessing the Nightscout API.",
)

if auth_option == "API Secret":
    api_secret = st.sidebar.text_input(
        "API Secret",
        value="",
        type="password",
        help="Enter your Nightscout API Secret.",
    )
    headers = {"api-secret": api_secret} if api_secret else {}
elif auth_option == "JWT Token":
    jwt_token = st.sidebar.text_input(
        "JWT Token",
        value="",
        type="password",
        help="Enter your Nightscout JWT Token.",
    )
    headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}
else:
    headers = {}

# Date range selection
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=2))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Debugging output
print(f"Selected Start Date: {start_date}")
print(f"Selected End Date: {end_date}")

# Convert dates to Unix timestamps
start_date_unix = int(time.mktime(start_date.timetuple()) * 1000)
end_date_unix = int(time.mktime(end_date.timetuple()) * 1000) + 86399999  # End of the day in milliseconds

# Debugging output
print(f"Start Date Unix: {start_date_unix}")
print(f"End Date Unix: {end_date_unix}")

# Button to Fetch Data
if st.sidebar.button("Fetch Glucose Data"):
    if not base_url:
        st.sidebar.error("Please enter your Nightscout Base URL.")
        print("Error: Nightscout Base URL is missing.")
    elif (auth_option == "API Secret" and not api_secret) or (
        auth_option == "JWT Token" and not jwt_token
    ):
        st.sidebar.error(f"Please enter your {auth_option}.")
        print(f"Error: {auth_option} is missing.")
    else:
        # Construct the API URL
        entries_url = f"{base_url}/api/v1/entries.json"

        # Debugging output
        print(f"Entries URL: {entries_url}")

        # Define query parameters
        params = {
            "find[date][$gte]": start_date_unix,
            "find[date][$lte]": end_date_unix,
            "find[type]": "sgv",
            "count": 10000,  # Adjust as needed
        }

        # Debugging output
        print(f"Query Parameters: {params}")

        try:
            # Make the API request
            response = requests.get(entries_url, headers=headers, params=params)
            response.raise_for_status()  # Raise an error for bad status codes

            # Debugging output
            print(f"Response Status Code: {response.status_code}")

            entries = response.json()

            # Debugging output (count only, no glucose values)
            entry_count = len(entries) if isinstance(entries, list) else "n/a"
            print(f"Number of entries received: {entry_count}")

            if not entries:
                st.warning("No glucose entries found for the selected date range.")
                print("No glucose entries found for the selected date range.")
            else:
                # Convert entries to DataFrame
                df = pd.DataFrame(entries)

                # Convert 'date' to datetime
                df['dateTime'] = pd.to_datetime(df['date'], unit='ms')

                # Sort by dateTime
                df = df.sort_values('dateTime')

                # Group by date and plot each day separately
                df['date'] = df['dateTime'].dt.date
                grouped = df.groupby('date')

                for date, group in grouped:
                    st.subheader(f"Glucose Levels for {date}")
                    fig, ax = plt.subplots()
                    ax.plot(group['dateTime'], group['sgv'], marker='o', linestyle='-')
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Glucose Level (mg/dL)")
                    ax.set_title(f"Glucose Levels on {date}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)

                    # Calculate the first derivative
                    group['sgv_diff'] = group['sgv'].diff()

                    # Calculate the rolling mean of the first derivative
                    group['sgv_diff_smooth'] = group['sgv_diff'].rolling(window=4).mean()

                    st.subheader(f"First Derivative of Glucose Levels for {date} (Smoothed)")
                    fig, ax = plt.subplots()
                    ax.plot(group['dateTime'], group['sgv_diff_smooth'], marker='o', linestyle='-')
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Change in Glucose Level (mg/dL)")
                    ax.set_title(f"First Derivative of Glucose Levels on {date} (Smoothed)")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)

                    # Calculate the second derivative
                    group['sgv_diff2'] = group['sgv_diff_smooth'].diff()
                    # Calculate the rolling mean of the second derivative
                    group['sgv_diff2_smooth'] = group['sgv_diff2'].rolling(window=4).mean()
                    st.subheader(f"Second Derivative of Glucose Levels for {date}")
                    fig, ax = plt.subplots()
                    ax.plot(group['dateTime'], group['sgv_diff2_smooth'], marker='o', linestyle='-')
                    ax.set_xlabel("Time")
                    ax.set_ylabel("Change in First Derivative (mg/dL)")
                    ax.set_title(f"Second Derivative of Glucose Levels on {date}")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)

                # Display glucose statistics
                st.subheader("Glucose Statistics (Selected Date Range)")
                st.write(f"**Minimum BG:** {df['sgv'].min()} mg/dL")
                st.write(f"**Maximum BG:** {df['sgv'].max()} mg/dL")
                st.write(f"**Average BG:** {df['sgv'].mean():.2f} mg/dL")
                st.write(f"**Standard Deviation:** {df['sgv'].std():.2f} mg/dL")

        except requests.exceptions.HTTPError as http_err:
            st.error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            st.error(f"An error occurred: {err}")
else:
    st.info("Enter your Nightscout API details in the sidebar and click 'Fetch Glucose Data'.")

