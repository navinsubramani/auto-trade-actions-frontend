import yaml
import streamlit as st
import os

from streamlit_authenticator import Authenticate
import plotly.express as px
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

from supabase_client import SupabaseClient
from yfinance_client import YFinanceClient

st.set_page_config(
    page_title="Boring Trade Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

class CustomPageState:
    """Custom session state class to manage session state variables."""

    def __init__(self):
        self.authentication_status = False
        self.name = "Unknown User"
        self.username = "Unknown User"
        self.supabase_client = SupabaseClient()
        self.yfinance_client = YFinanceClient()

        username = os.getenv('USERNAME')
        credentials = {
            'usernames': {
                username: {
                    'email': os.getenv('EMAIL'),
                    'name': os.getenv('NAME'),
                    'password': os.getenv('PASSWORD')
                }
            }
        }

        self.authenticator = Authenticate(
            credentials,
            cookie_expiry_days=int(os.getenv('EXPIRY_DAYS', 30)),
            cookie_name=os.getenv('COOKIE_KEY'),
            api_key=os.getenv('COOKIE_NAME'),
        )

    def login(self):
        """Login function to authenticate users."""

        self.authenticator.login(
            'main',
            clear_on_submit=True,
        )

        if st.session_state["authentication_status"]:
            self.authentication_status = True
            self.name = st.session_state["name"]
            self.username = st.session_state["username"]

            # Display the logout button in the sidebar
            self.show_tradescreens()
            self.logout()
            self.show_takeprofit_stoploss_data()

        elif st.session_state["authentication_status"] is False:
            st.error('Username/password is incorrect')
            self.authentication_status = False
            self.name = "Unknown User"
            self.username = "Unknown User"


        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
            self.authentication_status = False
            self.name = "Unknown User"
            self.username = "Unknown User"

    def logout(self):
        """Logout function to clear session state."""

        self.authenticator.logout(
            location='sidebar'
        )

        st.sidebar.button('Refresh', on_click=self.show_takeprofit_stoploss_data)
        st.sidebar.subheader("Algo Pro Alert")
        st.sidebar.code(f"{os.getenv('algo_pro_webhook')}")
        st.sidebar.subheader("Price Alert")
        st.sidebar.code(f"{os.getenv('price_alert_webhook')}")
        st.sidebar.subheader("Strategy Note")
        st.sidebar.text("strategy1 / Take Profit at price points and move stop loss: All 3 TP and SL must be set. No runner.")
        st.sidebar.text("strategy2 / Move stop loss at price points: All 3 TP and SL must be set. Runner is left open.")
        st.sidebar.text("strategy3 / Nill")
        st.sidebar.text("strategy4 / Move stop loss at profit taken: All 3 TP and SL must be set. No runner.")
        st.sidebar.text("strategy5 / Trialing Stop Loss: SL must be set. No runner.")

    def show_tradescreens(self):
        """Function to display the trade screens."""

        st.sidebar.title(f"Welcome {self.name}")

    def show_takeprofit_stoploss_data(self):
        """Function to display take profit and stop loss data."""

        st.title("Take Profit and Stop Loss Data")
        # Create a container with two vertical layouts
        id = None
        ticker = None
        strategy = ""
        tp1 = None
        tp2 = None
        tp3 = None
        sl = None

        def is_number(value):
            try:
                return isinstance(value, (int, float)) and not isinstance(value, bool) and not np.isnan(value)
            except TypeError:
                return False
            return False

        # ----------------------------------------
        # Take Profit and Stop Loss Data
        # ----------------------------------------
        data = self.supabase_client.get_tpsl_data()

        selection = st.dataframe(
            data.drop(columns=['id']),
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="tpsl_data",
            )
        try:
            row = selection["selection"]["rows"][0]
            id = data.iloc[row]['id']
            ticker = data.iloc[row]['ticker']
            strategy = data.iloc[row]['strategy']
            tp1 = data.iloc[row]['tp1']
            tp2 = data.iloc[row]['tp2']
            tp3 = data.iloc[row]['tp3']
            sl = data.iloc[row]['sl']

        except IndexError:
            pass
        
        chart_tab, edit_tab = st.tabs(["Chart View", "Edit"])

        # ----------------------------------------
        # Plot the data
        # ----------------------------------------
        with chart_tab:
            if id is not None:
                st.subheader("Chart View of last 7 day data with TP and SL")
                historical_data = self.yfinance_client.fetch_data(ticker)
                fig = px.line(
                    historical_data,
                    y='Close',
                )
                fig.update_yaxes(autorange=True)
                if strategy == "strategy1" or strategy == "strategy2":
                    if is_number(tp1):
                        fig.add_hline(y=tp1, line_color="green", line_width=1, line_dash="dash", annotation_text=f"TP1 - {tp1}", annotation_position="top left")
                    if is_number(tp2):
                        fig.add_hline(y=tp2, line_color="green", line_width=1.5, line_dash="dash", annotation_text=f"TP2 - {tp2}", annotation_position="top left")
                    if is_number(tp3):
                        fig.add_hline(y=tp3, line_color="green", line_width=2, line_dash="dash", annotation_text=f"TP3 - {tp3}", annotation_position="top left")
                    if is_number(sl):    
                        fig.add_hline(y=sl, line_color="red", line_width=2, line_dash="dash", annotation_text=f"SL - {sl}", annotation_position="top left")
                st.plotly_chart(fig, use_container_width=True)        
            else:
                st.warning("Please select a row to view the chart.")
        # ----------------------------------------
        # Edit the data
        # ----------------------------------------
        with edit_tab:
            
            try:
                if id is not None:
                    st.subheader("Edit Take Profit and Stop Loss Data")
                    row_data = data.iloc[row]
                    row_data = pd.DataFrame(row_data).T
                    row_data = row_data.reset_index(drop=True)
                    row_data = row_data.drop(columns=['id'])
                    edited_row_data = st.data_editor(
                        row_data,
                        disabled=False,
                    )

                    col1, col2, col3, col4 = st.columns([1, 1, 1, 10])

                    if col1.button("Update"):
                        self.supabase_client.update_tpsl_row(id, edited_row_data)

                    if col2.button("Add"):
                        self.supabase_client.insert_tpsl_row(edited_row_data)

                    if col3.button("Delete"):
                        self.supabase_client.delete_tpsl_row(id)

                else:
                    st.warning("Please select a row to edit.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# Initialize the custom page state
mypage = CustomPageState()
mypage.login()
