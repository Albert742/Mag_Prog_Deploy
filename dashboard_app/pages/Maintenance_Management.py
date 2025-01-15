import pandas as pd
import streamlit as st
import time
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL
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

# Titolo della pagina
st.title("Gestione Manutenzioni")

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

# Recupera i dati delle manutenzioni dalle diverse tabelle
manutenzioni_robot = select_recordsSQL(session, "ManutenzioneRobot")
manutenzioni_scaffalature = select_recordsSQL(session, "ManutenzioneScaffalature")
manutenzioni_veicoli = select_recordsSQL(session, "ManutenzioneVeicoli")
manutenzioni_zone = select_recordsSQL(session, "ManutenzioneZone")

# Crea i DataFrame per le manutenzioni
df_manutenzioni_robot = pd.DataFrame(manutenzioni_robot)
df_manutenzioni_scaffalature = pd.DataFrame(manutenzioni_scaffalature)
df_manutenzioni_veicoli = pd.DataFrame(manutenzioni_veicoli)
df_manutenzioni_zone = pd.DataFrame(manutenzioni_zone)

# Seleziona il tipo di manutenzione
tipo_manutenzione = st.selectbox("Seleziona il tipo di manutenzione", ["Robot", "Scaffalature", "Veicoli", "Zone"])

# Visualizza le manutenzioni in base al tipo selezionato
if tipo_manutenzione == "Robot":
    st.write("### Manutenzioni Robot")
    st.dataframe(df_manutenzioni_robot)
elif tipo_manutenzione == "Scaffalature":
    st.write("### Manutenzioni Scaffalature")
    st.dataframe(df_manutenzioni_scaffalature)
elif tipo_manutenzione == "Veicoli":
    st.write("### Manutenzioni Veicoli")
    st.dataframe(df_manutenzioni_veicoli)
elif tipo_manutenzione == "Zone":
    st.write("### Manutenzioni Zone")
    st.dataframe(df_manutenzioni_zone)

# Bottone per mostrare il form di aggiunta manutenzione
if "show_form_add_manutenzione" not in st.session_state:
    st.session_state.show_form_add_manutenzione = False

if not st.session_state.show_form_add_manutenzione:
    if st.button("Aggiungi Manutenzione"):
        st.session_state.show_form_add_manutenzione = True
        st.rerun()

# Sezione per aggiungere una manutenzione
if st.session_state.get("show_form_add_manutenzione", False):
    st.write("### Aggiungi Manutenzione")
    with st.form(key='manutenzione_form_add'):
        if tipo_manutenzione == "Robot":
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
                    st.success("Manutenzione aggiunta con successo!")
                    time.sleep(2)
                    st.session_state.show_form_add_manutenzione = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante l'aggiunta della manutenzione: {e}")
            elif cancel_button:
                st.session_state.show_form_add_manutenzione = False
                st.rerun()
        elif tipo_manutenzione == "Scaffalature":
            id_scaffalatura = st.number_input("ID Scaffalatura", min_value=1)
            data_manutenzione = st.date_input("Data Manutenzione")
            tipo = st.selectbox("Tipo", ['Ispezione', 'Pulizia', 'Riparazione', 'Sostituzione'])
            stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
            note = st.text_area("Note")

            submit_button = st.form_submit_button(label="Aggiungi Manutenzione")
            cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                try:
                    add_recordSQL(session, "ManutenzioneScaffalature", {
                        "ID_Scaffalatura": id_scaffalatura,
                        "DataManutenzione": data_manutenzione,
                        "Tipo": tipo,
                        "Stato": stato,
                        "Note": note
                    })
                    st.success("Manutenzione aggiunta con successo!")
                    time.sleep(2)
                    st.session_state.show_form_add_manutenzione = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante l'aggiunta della manutenzione: {e}")
            elif cancel_button:
                st.session_state.show_form_add_manutenzione = False
                st.rerun()
        elif tipo_manutenzione == "Veicoli":
            id_veicolo = st.number_input("ID Veicolo", min_value=1)
            data_manutenzione = st.date_input("Data Manutenzione")
            tipo = st.selectbox("Tipo", ['Ispezione', 'Riparazione', 'Sostituzione'])
            stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
            note = st.text_area("Note")

            submit_button = st.form_submit_button(label="Aggiungi Manutenzione")
            cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                try:
                    add_recordSQL(session, "ManutenzioneVeicoli", {
                        "ID_Veicolo": id_veicolo,
                        "DataManutenzione": data_manutenzione,
                        "Tipo": tipo,
                        "Stato": stato,
                        "Note": note
                    })
                    st.success("Manutenzione aggiunta con successo!")
                    time.sleep(2)
                    st.session_state.show_form_add_manutenzione = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore durante l'aggiunta della manutenzione: {e}")
            elif cancel_button:
                st.session_state.show_form_add_manutenzione = False
                st.rerun()
        elif tipo_manutenzione == "Zone":
            id_zona = st.number_input("ID Zona", min_value=1)
            data_manutenzione = st.date_input("Data Manutenzione")
            tipo = st.selectbox("Tipo", ['Ispezione', 'Pulizia', 'Riparazione'])
            stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
            note = st.text_area("Note")

            submit_button = st.form_submit_button(label="Aggiungi Manutenzione")
            cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                try:
                    add_recordSQL(session, "ManutenzioneZone", {
                        "ID_Zona": id_zona,
                        "DataManutenzione": data_manutenzione,
                        "Tipo": tipo,
                        "Stato": stato,
                        "Note": note
                    })
                    st.success("Manutenzione aggiunta con successo!")
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
        if tipo_manutenzione == "Robot":
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
        elif tipo_manutenzione == "Scaffalature":
            id_scaffalatura = st.number_input("ID Scaffalatura", min_value=1)
            data_manutenzione = st.date_input("Data Manutenzione")
            tipo = st.selectbox("Tipo", ['Ispezione', 'Pulizia', 'Riparazione', 'Sostituzione'])
            stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
            note = st.text_area("Note")

            submit_button = st.form_submit_button(label="Aggiorna Manutenzione")
            cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                try:
                    update_recordSQL(session, "ManutenzioneScaffalature", {
                        "ID_Scaffalatura": id_scaffalatura,
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
        elif tipo_manutenzione == "Veicoli":
            id_veicolo = st.number_input("ID Veicolo", min_value=1)
            data_manutenzione = st.date_input("Data Manutenzione")
            tipo = st.selectbox("Tipo", ['Ispezione', 'Riparazione', 'Sostituzione'])
            stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
            note = st.text_area("Note")

            submit_button = st.form_submit_button(label="Aggiorna Manutenzione")
            cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                try:
                    update_recordSQL(session, "ManutenzioneVeicoli", {
                        "ID_Veicolo": id_veicolo,
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
        elif tipo_manutenzione == "Zone":
            id_zona = st.number_input("ID Zona", min_value=1)
            data_manutenzione = st.date_input("Data Manutenzione")
            tipo = st.selectbox("Tipo", ['Ispezione', 'Pulizia', 'Riparazione'])
            stato = st.selectbox("Stato", ['Programmata', 'Completata', 'Annullata'])
            note = st.text_area("Note")

            submit_button = st.form_submit_button(label="Aggiorna Manutenzione")
            cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                try:
                    update_recordSQL(session, "ManutenzioneZone", {
                        "ID_Zona": id_zona,
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
    tipo_manutenzione = st.selectbox("Tipo di Manutenzione", ["Robot", "Scaffalature", "Veicoli", "Zone"])
    with st.form(key='manutenzione_form_delete'):
        id_manutenzione = st.number_input("ID Manutenzione", min_value=1)

        submit_button = st.form_submit_button(label="Elimina Manutenzione")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            if tipo_manutenzione == "Robot":
                delete_recordSQL(session, "ManutenzioneRobot", f"ID_Manutenzione = {id_manutenzione}", {})
            elif tipo_manutenzione == "Scaffalature":
                delete_recordSQL(session, "ManutenzioneScaffalature", f"ID_Manutenzione = {id_manutenzione}", {})
            elif tipo_manutenzione == "Veicoli":
                delete_recordSQL(session, "ManutenzioneVeicoli", f"ID_Manutenzione = {id_manutenzione}", {})
            elif tipo_manutenzione == "Zone":
                delete_recordSQL(session, "ManutenzioneZone", f"ID_Manutenzione = {id_manutenzione}", {})
            st.success("Manutenzione eliminata con successo!")
            time.sleep(2)
            st.session_state.show_form_delete_manutenzione = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'eliminazione della manutenzione: {e}")
    elif cancel_button:
        st.session_state.show_form_delete_manutenzione = False
        st.rerun()