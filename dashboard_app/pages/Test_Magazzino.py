"""
Modulo che contiene la pagina di test del magazzino
"""
import streamlit as st
import time
import plotly.express as px
from utils.MagUtils import log_logout, start_sensor_data_generation, stop_sensor_data_generation
from streamlit_extras.switch_page_button import switch_page

# Titolo della pagina
st.title("Test Funzionalità Magazzino")

# Sidebar menu

# Bottone per il logout
if st.sidebar.button("Log Out"):
    log_logout(st.session_state.get("id_utente"))
    st.success("Logout effettuato con successo. Verrai reindirizzato alla pagina di login.")
    time.sleep(2)
    st.session_state.clear()
    switch_page("Login")
    
st.sidebar.write(f"Accesso effettuato da: {st.session_state.get('username', 'Unknown')}")

st.sidebar.title("Menu")

ruolo = st.session_state.get("ruolo", "Guest")

if ruolo == "Amministratore":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
    st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
    st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
elif ruolo == "Tecnico":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
    st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
elif ruolo == "Operatore":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')

st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Bottone per avviare/fermare la generazione dei dati dei sensori
if "sensor_data_generation" not in st.session_state:
    st.session_state.sensor_data_generation = False

if st.session_state.sensor_data_generation:
    if st.button("Ferma Generazione Dati Sensori"):
        stop_sensor_data_generation()
        st.session_state.sensor_data_generation = False
        st.success("Generazione dati sensori fermata.")
        st.stop()
else:
    if st.button("Avvia Generazione Dati Sensori"):
        start_sensor_data_generation()
        st.session_state.sensor_data_generation = True
        st.success("Generazione dati sensori avviata.")