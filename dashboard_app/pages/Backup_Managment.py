from sqlalchemy import text
import streamlit as st
import pandas as pd
import time
import os
import shutil
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL, backup_database, restore_database, get_db_connection
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

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
    st.sidebar.page_link('pages/Internal_Logistic_Managment.py', label='Gestione Logistica Interna')
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
        if btn:
            # Delete the temp/backups directory after download
            shutil.rmtree(os.path.dirname(file_path))
        return btn

# Sezione per creare un backup
st.write("### Crea Backup")
with st.form(key='backup_form'):
    create_backup_button = st.form_submit_button(label="Crea Backup")
if create_backup_button:
    backup_file = backup_database(backup_dir=os.path.join("temp", "backups"))
    if backup_file:
        st.success(f"Backup creato con successo. Procedi a scaricarlo.")
        download_backup(backup_file)
    else:
        st.error("Errore durante la creazione del backup.")
        
from pages.Login import verifica_password, autentica_utente

# Creazione della cartella temporanea per i ripristini
temp_dir = "temp/restores"
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Sezione per ripristinare un backup
st.write("### Ripristina Backup")
uploaded_file = st.file_uploader("Carica il file di backup", type=["sql"])

if uploaded_file is not None:
    st.write("### Conferma Password")
    password = st.text_input("Inserisci la tua password per confermare il ripristino", type="password")
    
    with st.form(key='restore_form'):
        restore_backup_button = st.form_submit_button(label="Ripristina Backup")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_restore_button = st.form_submit_button(label="Annulla")

    if restore_backup_button:
        username = st.session_state.get("username")
        if username:
            user, ruolo, id_utente = autentica_utente(username, password)
            if user:
                # Save the uploaded file to a temporary location
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                
                success, message = restore_database(temp_file_path)
                if success:
                    st.success(message)
                    # Delete the temp/restores directory after restoration
                    shutil.rmtree(temp_dir)
                    st.rerun()
                else:
                    st.error(f"{message}")

                # Clean up the temporary file
                os.remove(temp_file_path)
            else:
                st.error("Password errata. Ripristino non autorizzato.")
        else:
            st.error("Utente non autenticato. Effettua il login per procedere.")
    elif cancel_restore_button:
        st.stop()
