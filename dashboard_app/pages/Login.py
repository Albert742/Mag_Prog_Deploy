import streamlit as st
from utils.MagDBcontroller import connessione, selectSQL, add_record
import bcrypt

# Hash password with bcrypt
def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

# Verify password
def verify_password(password, hashed_password):
    # Check if the provided password matches the stored hash
    return bcrypt.checkpw(password.encode(), hashed_password)
# Authenticate user credentials
def authenticate_user(username, password):
    query = "SELECT Password FROM Credenziali WHERE Username = %s"
    with connessione() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (username,))
        result = cursor.fetchone()

    if result:
        hashed_password = result[0]  # Assuming Password is stored as binary
        if verify_password(password, hashed_password):
            return True
    return False
# Create login/signup form
def login_signup():
    st.title("Warehouse Login")

    # Select login or signup
    option = st.radio("Choose an option:", ["Login", "Sign Up"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if option == "Sign Up":
        role = st.selectbox("Role", ["Amministratore", "Operatore", "Tecnico"])
        if st.button("Sign Up"):
            hashed_password = hash_password(password)
            try:
                with connessione() as conn:
                    add_record(conn, "Credenziali", ["Username", "Password", "Ruolo"], [username, hashed_password, role])
                    st.success("Signup successful! Please log in.")
            except Exception as e:
                st.error(f"Error during signup: {e}")

    elif option == "Login":
        if st.button("Login"):
            user = authenticate_user(username, password)
            if user:
                st.success("Login successful!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.switch_page("Home.py")
                st.rerun()
            else:
                st.error("Invalid credentials!")

if __name__ == "__main__":
    login_signup()
