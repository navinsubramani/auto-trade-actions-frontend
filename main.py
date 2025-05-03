import yaml
import streamlit as st

from yaml.loader import SafeLoader
from streamlit_authenticator import Authenticate

with open('secrets.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)


class CustomPageState:
    """Custom session state class to manage session state variables."""

    def __init__(self):
        self.authentication_status = False
        self.name = "Unknown User"
        self.username = "Unknown User"
        self.password = None

        self.authenticator = Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
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

    def show_tradescreens(self):
        """Function to display the trade screens."""

        st.sidebar.title(f"Welcome {self.name}")
        st.sidebar.text("This application is for experimental purposes only.")


# Initialize the custom page state
mypage = CustomPageState()
mypage.login()
