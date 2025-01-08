"""
Modulo che contiene la pagina di test del magazzino
"""
import streamlit as st
import time
import plotly.express as px
import random
import datetime
import threading
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page

# Define the stop event
stop_event = threading.Event()

# Funzione per generare dati randomici per i sensori
def generate_sensor_data():
    session = connessione()
    if not session:
        st.error("Errore di connessione al database.")
        return

    sensori = select_recordsSQL(session, "Sensori")
    if not sensori:
        st.error("Nessun sensore trovato.")
        session.close()
        return

    while not stop_event.is_set():
        for sensore in sensori:
            if sensore['Tipo'] == 'Temperatura':
                valore = round(random.uniform(15.0, 25.0), 2)  # Temperatura in gradi Celsius
            elif sensore['Tipo'] == 'Umidità':
                valore = round(random.uniform(30.0, 70.0), 2)  # Umidità in percentuale
            elif sensore['Tipo'] == 'Presenza':
                valore = random.choice([0, 1])  # Presenza 0 o 1

            lettura = {
                "ID_Sensore": sensore['ID_Sensore'],
                "Tipo": sensore['Tipo'],
                "Valore": valore,
                "DataLettura": datetime.datetime.now()
            }
            add_recordSQL(session, "LettureSensori", lettura)
        time.sleep(5)  # Attendi 5 secondi prima di generare nuovi dati

    session.close()

# Funzione per avviare la generazione dei dati
def start_generating_data():
    stop_event.clear()
    st.session_state.generating_data = True
    threading.Thread(target=generate_sensor_data).start()

# Funzione per interrompere la generazione dei dati
def stop_generating_data():
    stop_event.set()
    st.session_state.generating_data = False

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

# Bottone per avviare/interrompere la generazione dei dati
if "generating_data" not in st.session_state:
    st.session_state.generating_data = False

if st.session_state.generating_data:
    if st.button("Interrompi Generazione Dati"):
        stop_generating_data()
        st.rerun()
else:
    if st.button("Avvia Generazione Dati"):
        start_generating_data()
        st.rerun()