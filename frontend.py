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
    st.title("🚀 Welcome to Fast Social")

    # simple form with two buttons
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                # 1. Login with Form Data
                login_data = {"username": email, "password": password}
                response = requests.post("http://localhost:8000/users/token", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    # Fixed typo: access_token (with double 's')
                    st.session_state.token = token_data["access_token"]

                    # 2. Get user info using the new token
                    # We pass headers=get_header() because /me needs authentication
                    user_response = requests.get("http://localhost:8000/users/me", headers=get_headers())

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

                # Match UserCreate schema exactly
                signup_payload = {
                    "username": generated_username,
                    "email": email,
                    "password": password
                }

                # This hits @router.post("/register") route
                response = requests.post("http://localhost:8000/users/register", json=signup_payload)

                if response.status_code == 201: # 201 is Created
                    st.success("Account created! You can now Login.")
                else:
                    error_msg = response.json().get("detail", "Error")
                    st.error(f"Sign up failed: {error_msg}")
    else:
        st.info("Please enter your email and password to continue.")


def upload_page():
    st.title("📸 Share Something")

    upload_file = st.file_uploader("Choose Media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    caption = st.text_area("Caption:", placeholder="What's on your mind ?")

    if upload_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type)}
            data = {"caption": caption}
            response =  requests.post("http://localhost:8000/posts/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 201:
                st.success("Posted!")
                st.rerun()
            else:
                st.error("Upload failed!")


def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 the URL code"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        # Overlay text: ie (input encoded), ly (bottom offset), co (color), bg (background)
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-30,co-white,bg-000000A0,l-end"

        # Merge existing params with text overlay
        if transformation_params:
            transformation_params = f"{transformation_params}:{text_overlay}"
        else:
            transformation_params = text_overlay

    if not transformation_params:
        return original_url

    # ImageKit logic: Add /tr:params/ after the ID
    # Example: https://ik.imagekit.io/id/filename -> https://ik.imagekit.io/id/tr:w-500/filename
    parts = original_url.split("/")
    base = "/".join(parts[:4]) # https://ik.imagekit.io/your_id
    file_path = "/".join(parts[4:]) # the rest of the path

    return f"{base}/tr:{transformation_params}/{file_path}"


def feed_page():
    st.title("🏠 Feed")

    response = requests.get("http://localhost:8000/posts/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()
        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            st.markdown("---")

            # Header with user, date, and delete button (if owner)
            col1, col2 = st.columns([4, 1])
            with col1:
                username = post['user']['username']
                st.markdown(f"**@{username}** • {post['created_at'][:10]}")
            with col2:
                current_user_id = str(st.session_state.user['id'])
                post_owner_id = str(post['user_id'])

                if current_user_id == post_owner_id:
                    if st.button("🗑️", key=f"delete_{post['id']}", help="Delete Post"):
                        response = requests.delete(f"http://localhost:8000/posts/{post['id']}", headers=get_headers())

                        if response.status_code == 204: # 204 is the standard for successful deletion
                            st.success("Post deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete post!")

            caption = post.get('caption', '')
            if post['file_type'].startswith('image'):
                uniform_url = create_transformed_url(post['url'], "w-500", caption)
                st.image(uniform_url)
            else:
                st.video(post['url'])
                st.caption(caption)
    else:
        st.error("Failed to load feed")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Sidebar navigation
    st.sidebar.title(f"👋 Hi {st.session_state.user['email']}!")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["🏠 Feed", "📸 Upload"])

    if page == "🏠 Feed":
        feed_page()
    else:
        upload_page()