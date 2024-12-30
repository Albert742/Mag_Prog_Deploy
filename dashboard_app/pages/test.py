import streamlit as st
import requests
from flask import Flask, request

# Initialize Flask app
app = Flask(__name__)

@app.route('/get_ip')
def get_ip():
    user_ip = request.remote_addr
    return user_ip

# Run Flask app in a separate thread
from threading import Thread

def run_flask():
    app.run(port=5000)

flask_thread = Thread(target=run_flask)
flask_thread.start()

# Streamlit app
st.title("Test IP Getter")

# Get client IP from Flask endpoint
try:
    response = requests.get("http://localhost:5000/get_ip")
    if response.status_code == 200:
        client_ip = response.text
        st.markdown(f"The remote IP is {client_ip}")
    else:
        st.markdown("Unable to retrieve the remote IP.")
except Exception as e:
    st.markdown(f"Error: {e}")