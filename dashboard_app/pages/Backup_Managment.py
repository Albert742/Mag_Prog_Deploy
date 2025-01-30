from sqlalchemy import text
import streamlit as st
import pandas as pd
import time
import os
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL, backup_database, restore_database, get_db_connection
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima o accedi con un account autorizzato.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

# Connessione al database
session = connessione()

# Gestione Backup
st.write("## Gestione Backup")

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
    st.sidebar.page_link('pages/External_Logistic_Managment.py', label='Gestione Logistica Esterna')
    st.sidebar.page_link('pages/External_Logistic_Managment.py', label='Gestione Logistica Esterna')
    st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
    st.sidebar.page_link('pages/Maintenance_Management.py', label='Gestione Manutenzioni')
    st.sidebar.page_link('pages/Allert_Management.py', label='Gestione Allerte')
    st.sidebar.page_link('pages/Backup_Managment.py', label='Gestione Backup')
    st.sidebar.page_link('pages/Test_Magazzino.py', label='Test Funzionalità')
elif ruolo == "Tecnico":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
    st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
    st.sidebar.page_link('pages/External_Logistic_Managment.py', label='Gestione Logistica Esterna')
    st.sidebar.page_link('pages/Maintenance_Management.py', label='Gestione Manutenzioni')
    st.sidebar.page_link('pages/Allert_Management.py', label='Gestione Allerte')
elif ruolo == "Operatore":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')

st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

def download_backup(file_path):
    with open(file_path, "rb") as file:
        btn = st.download_button(
            label="Scarica Backup",
            data=file,
            file_name=os.path.basename(file_path),
            mime="application/octet-stream"
        )
        return btn

# Sezione per creare un backup
st.write("### Crea Backup")
if st.button("Crea Backup"):
    backup_file = backup_database(backup_dir=os.path.join("C:", "Users", "alber", "Desktop", "testback"))
    if backup_file:
        st.success(f"Backup creato con successo. Procedi a scaricarlo.")
        download_backup(backup_file)
    else:
        st.error("Errore durante la creazione del backup.")

# Sezione per ripristinare un backup
st.write("### Ripristina Backup")
uploaded_file = st.file_uploader("Carica il file di backup", type=["sql"])
if uploaded_file is not None:
    with open("temp_backup.sql", "wb") as f:
        f.write(uploaded_file.getbuffer())
    if st.button("Ripristina Backup"):
        success = restore_database(backup_file="temp_backup.sql")
        if success:
            st.success("Ripristino del database avvenuto con successo.")
        else:
            st.error("Errore durante il ripristino del database. Controlla il file discrepancies.log per i dettagli.")

# Sezione per gestire le discrepanze
if os.path.exists("discrepancies.log"):
    st.write("### Discrepanze trovate")
    with open("discrepancies.log", "r") as f:
        discrepancies = f.readlines()
    for discrepancy in discrepancies:
        st.write(discrepancy)
    if st.button("Sovrascrivi dati esistenti"):
        with open("temp_backup.sql", "r") as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    try:
                        engine, session = get_db_connection()
                        with engine.connect() as connection:
                            connection.execute(text(command))
                    except Exception as e:
                        st.error(f"Errore durante l'esecuzione del comando: {command}\nErrore: {e}")
        st.success("Dati sovrascritti con successo.")
        os.remove("discrepancies.log")
    if st.button("Mantieni dati esistenti"):
        st.success("Dati esistenti mantenuti.")
        os.remove("discrepancies.log")