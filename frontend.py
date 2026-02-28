import streamlit as st
import requests
import base64
import urllib.parse

st.set_page_config(page_title="Fast Social", layout="wide")

if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("Welcome to Fast Social")

    # simple form with two buttons
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                # 1. Login with Form Data
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/api/users/token", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    # Fixed typo: access_token (with double 's')
                    st.session_state.token = token_data["access_token"]

                    # 2. Get user info using the new token
                    # We pass headers=get_header() because /me needs authentication
                    user_response = requests.get("http://localhost:8000/api/users/me", headers=get_headers())

                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.success(f"Welcome back, {st.session_state.user['username']}!")
                        st.rerun()
                    else:
                        st.error("Login worked, but failed to fetch your profile.")
                else:
                    st.error("Invalid email or password!")

        with col2:
            if st.button("Sign up", type="secondary", use_container_width=True):
                # 3. Create the username from email (e.g., 'john' from 'john@gmail.com')
                generated_username = email.split('@')[0]

                # Match your UserCreate schema exactly
                signup_payload = {
                    "username": generated_username,
                    "email": email,
                    "password": password
                }

                # This hits your @router.post("") route
                response = requests.post("http://localhost:8000/api/users", json=signup_payload)

                if response.status_code == 201: # 201 is Created
                    st.success("Account created! You can now Login.")
                else:
                    error_msg = response.json().get("detail", "Error")
                    st.error(f"Sign up failed: {error_msg}")
    else:
        st.info("Please enter your email and password to continue.")