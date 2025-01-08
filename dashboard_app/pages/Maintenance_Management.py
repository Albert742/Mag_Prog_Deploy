import pandas as pd
import streamlit as st
import time
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL
from utils.MagUtils import create_employee_id, log_logout
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima o accedi con un account autorizzato.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

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

# Titolo della pagina
st.title("Gestione Manutenzioni")

# Connessione al database
session = connessione()

# Visualizza manutenzioni
manutenzioni = select_recordsSQL(session, "ManutenzioneRobot")
if manutenzioni:
    df_manutenzioni = pd.DataFrame(manutenzioni)
    st.write("### Manutenzioni")
    st.dataframe(df_manutenzioni)
else:
    st.error("Errore nel recuperare i dati delle manutenzioni dal database.")

# Bottone per mostrare il form di aggiunta manutenzione
if "show_form_add_manutenzione" not in st.session_state:
    st.session_state.show_form_add_manutenzione = False

if not st.session_state.show_form_add_manutenzione:
    if st.button("Schedula Manutenzione"):
        st.session_state.show_form_add_manutenzione = True
        st.rerun()

# Sezione per aggiungere una manutenzione
if st.session_state.get("show_form_add_manutenzione", False):
    st.write("### Schedula Manutenzione")
    with st.form(key='manutenzione_form_add'):
        id_robot = st.number_input("ID Robot", min_value=1)
        data_manutenzione = st.date_input("Data Manutenzione")
        tipo = st.selectbox("Tipo", ['Ispezione', 'Riparazione', 'Sostituzione'])
        stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
        note = st.text_area("Note")

        submit_button = st.form_submit_button(label="Aggiungi Manutenzione")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "ManutenzioneRobot", {
                "ID_Robot": id_robot,
                "DataManutenzione": data_manutenzione,
                "Tipo": tipo,
                "Stato": stato,
                "Note": note
            })
            st.success("Manutenzione schedulata con successo!")
            time.sleep(2)
            st.session_state.show_form_add_manutenzione = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta della manutenzione: {e}")
    elif cancel_button:
        st.session_state.show_form_add_manutenzione = False
        st.rerun()

# Bottone per mostrare il form di aggiornamento manutenzione
if "show_form_update_manutenzione" not in st.session_state:
    st.session_state.show_form_update_manutenzione = False

if not st.session_state.show_form_update_manutenzione:
    if st.button("Aggiorna Manutenzione"):
        st.session_state.show_form_update_manutenzione = True
        st.rerun()

# Sezione per aggiornare una manutenzione
if st.session_state.get("show_form_update_manutenzione", False):
    st.write("### Aggiorna Manutenzione")
    with st.form(key='manutenzione_form_update'):
        id_manutenzione = st.number_input("ID Manutenzione", min_value=1)
        id_robot = st.number_input("ID Robot", min_value=1)
        data_manutenzione = st.date_input("Data Manutenzione")
        tipo = st.selectbox("Tipo", ['Ispezione', 'Riparazione', 'Sostituzione'])
        stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
        note = st.text_area("Note")

        submit_button = st.form_submit_button(label="Aggiorna Manutenzione")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            update_recordSQL(session, "ManutenzioneRobot", {
                "ID_Robot": id_robot,
                "DataManutenzione": data_manutenzione,
                "Tipo": tipo,
                "Stato": stato,
                "Note": note
            }, f"ID_Manutenzione = {id_manutenzione}", {})
            st.success("Manutenzione aggiornata con successo!")
            time.sleep(2)
            st.session_state.show_form_update_manutenzione = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento della manutenzione: {e}")
    elif cancel_button:
        st.session_state.show_form_update_manutenzione = False
        st.rerun()

# Bottone per mostrare il form di eliminazione manutenzione
if "show_form_delete_manutenzione" not in st.session_state:
    st.session_state.show_form_delete_manutenzione = False

if not st.session_state.show_form_delete_manutenzione:
    if st.button("Elimina Manutenzione"):
        st.session_state.show_form_delete_manutenzione = True
        st.rerun()

# Sezione per eliminare una manutenzione
if st.session_state.get("show_form_delete_manutenzione", False):
    st.write("### Elimina Manutenzione")
    with st.form(key='manutenzione_form_delete'):
        id_manutenzione = st.number_input("ID Manutenzione", min_value=1)

        submit_button = st.form_submit_button(label="Elimina Manutenzione")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            delete_recordSQL(session, "ManutenzioneRobot", f"ID_Manutenzione = {id_manutenzione}", {})
            st.success("Manutenzione eliminata con successo!")
            time.sleep(2)
            st.session_state.show_form_delete_manutenzione = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'eliminazione della manutenzione: {e}")
    elif cancel_button:
        st.session_state.show_form_delete_manutenzione = False
        st.rerun()