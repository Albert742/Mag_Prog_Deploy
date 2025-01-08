"""
Modulo che contiene la pagina di test del magazzino
"""
import streamlit as st
import time
import random
import datetime
import threading
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima o accedi con un account autorizzato.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

# Funzione per generare dati randomici per i sensori
def generate_sensor_data(temp_range, humidity_range, presence_anomalies, temp_anomalies, humidity_anomalies, duration):
    session = connessione()
    if not session:
        st.session_state.error_message = "Errore di connessione al database."
        return

    sensori = select_recordsSQL(session, "Sensori")
    if not sensori:
        st.session_state.error_message = "Nessun sensore trovato."
        session.close()
        return

    record_count = 0
    start_time = time.time()
    while True:
        for sensore in sensori:
            if duration and (time.time() - start_time) >= duration:
                break
            if sensore['Tipo'] == 'Temperatura':
                valore = round(random.uniform(*temp_range), 2) if not temp_anomalies else round(random.uniform(-20.0, 60.0), 2)
            elif sensore['Tipo'] == 'Umidità':
                valore = round(random.uniform(*humidity_range), 2) if not humidity_anomalies else round(random.uniform(0.0, 100.0), 2)
            elif sensore['Tipo'] == 'Presenza':
                valore = random.choice([0, 1]) if not presence_anomalies else random.choice([1])

            lettura = {
                "ID_Sensore": sensore['ID_Sensore'],
                "Tipo": sensore['Tipo'],
                "Valore": valore,
                "DataLettura": datetime.datetime.now()
            }
            success = add_recordSQL(session, "LettureSensori", lettura)
            if success:
                record_count += 1

        if duration and (time.time() - start_time) >= duration:
            break

        time.sleep(5)  # Attendi 5 secondi prima di generare nuovi dati

    session.close()
    st.session_state.record_count = record_count

# Funzione per avviare la generazione dei dati
def start_generating_data(temp_range, humidity_range, presence_anomalies, temp_anomalies, humidity_anomalies, duration):
    threading.Thread(target=generate_sensor_data, args=(temp_range, humidity_range, presence_anomalies, temp_anomalies, humidity_anomalies, duration)).start()

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
    st.sidebar.page_link('pages/Orders_Managment.py', label='Gestione Ordini')
    st.sidebar.page_link('pages/Maintenance_Management.py', label='Gestione Manutenzioni')
    st.sidebar.page_link('pages/Allert_Management.py', label='Gestione Allerte')
    st.sidebar.page_link('pages/Test_Magazzino.py', label='Test Funzionalità')
elif ruolo == "Tecnico":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
    st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
    st.sidebar.page_link('pages/Orders_Managment.py', label='Gestione Ordini')
    st.sidebar.page_link('pages/Maintenance_Management.py', label='Gestione Manutenzioni')
elif ruolo == "Operatore":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')

st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Form per configurare la generazione dei dati
st.write("### Configura Generazione Dati")
with st.form(key='config_form'):
    temp_range = st.slider("Intervallo Temperatura (°C)", min_value=-10.0, max_value=50.0, value=(15.0, 25.0))
    humidity_range = st.slider("Intervallo Umidità (%)", min_value=0.0, max_value=100.0, value=(30.0, 70.0))
    presence_anomalies = st.checkbox("Includi Anomalie di Presenza", value=False)
    temp_anomalies = st.checkbox("Includi Anomalie di Temperatura", value=False)
    humidity_anomalies = st.checkbox("Includi Anomalie di Umidità", value=False)
    duration = st.number_input("Durata (secondi, 0 per infinito)", min_value=0, value=0)
    submit_button = st.form_submit_button(label="Avvia Generazione Dati")

if submit_button:
    if duration == 0:
        st.warning("Attenzione: La generazione dei dati continuerà all'infinito finché l'applicazione non verrà interrotta manualmente.")
    start_generating_data(temp_range, humidity_range, presence_anomalies, temp_anomalies, humidity_anomalies, duration if duration > 0 else None)
    st.rerun()

# Mostra messaggi di errore o successo
if "error_message" in st.session_state:
    st.error(st.session_state.error_message)
    del st.session_state.error_message

if "record_count" in st.session_state:
    st.success(f"Sessione terminata. Record aggiunti: {st.session_state.record_count}")
    del st.session_state.record_count