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

# Connessione al database
session = connessione()

# Titolo della pagina
st.title("Gestione Ordini")

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

# Visualizza ordini
ordini = select_recordsSQL(session, "Ordini")
if ordini:
    df_ordini = pd.DataFrame(ordini)
    st.write("### Ordini")
    st.dataframe(df_ordini)
else:
    st.error("Errore nel recuperare i dati degli ordini dal database.")

# Bottone per mostrare il form di aggiunta ordine
if "show_form_add_ordine" not in st.session_state:
    st.session_state.show_form_add_ordine = False
if not st.session_state.show_form_add_ordine:
    if st.button("Aggiungi Ordine"):
        st.session_state.show_form_add_ordine = True
        st.rerun()

# Sezione per aggiungere un ordine
if st.session_state.get("show_form_add_ordine", False):
    st.write("### Aggiungi Ordine")
    with st.form(key='ordine_form_add'):
        data_ordine = st.date_input("Data Ordine")
        tipo = st.selectbox("Tipo", ['Entrata', 'Uscita'])
        id_fornitore = st.number_input("ID Fornitore", min_value=0)
        id_cliente = st.number_input("ID Cliente", min_value=0)
        stato = st.selectbox("Stato", ['In elaborazione', 'Spedito', 'Concluso'])

        submit_button = st.form_submit_button(label="Aggiungi Ordine")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "Ordini", {
                "DataOrdine": data_ordine,
                "Tipo": tipo,
                "ID_Fornitore": id_fornitore if id_fornitore != 0 else None,
                "ID_Cliente": id_cliente if id_cliente != 0 else None,
                "Stato": stato
            })
            st.success("Ordine aggiunto con successo!")
            time.sleep(2)
            st.session_state.show_form_add_ordine = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta dell'ordine: {e}")
    elif cancel_button:
        st.session_state.show_form_add_ordine = False
        st.rerun()

# Bottone per mostrare il form di aggiornamento ordine
if "show_form_update_ordine" not in st.session_state:
    st.session_state.show_form_update_ordine = False

if not st.session_state.show_form_update_ordine:
    if st.button("Aggiorna Ordine"):
        st.session_state.show_form_update_ordine = True
        st.rerun()

# Sezione per aggiornare un ordine
if st.session_state.get("show_form_update_ordine", False):
    st.write("### Aggiorna Ordine")
    with st.form(key='ordine_form_update'):
        id_ordine = st.number_input("ID Ordine", min_value=1)
        data_ordine = st.date_input("Data Ordine")
        tipo = st.selectbox("Tipo", ['Entrata', 'Uscita'])
        id_fornitore = st.number_input("ID Fornitore", min_value=0)
        id_cliente = st.number_input("ID Cliente", min_value=0)
        stato = st.selectbox("Stato", ['In elaborazione', 'Spedito', 'Concluso'])

        submit_button = st.form_submit_button(label="Aggiorna Ordine")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            update_recordSQL(session, "Ordini", {
                "DataOrdine": data_ordine,
                "Tipo": tipo,
                "ID_Fornitore": id_fornitore if id_fornitore != 0 else None,
                "ID_Cliente": id_cliente if id_cliente != 0 else None,
                "Stato": stato
            }, f"ID_Ordine = {id_ordine}", {})
            st.success("Ordine aggiornato con successo!")
            time.sleep(2)
            st.session_state.show_form_update_ordine = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento dell'ordine: {e}")
    elif cancel_button:
        st.session_state.show_form_update_ordine = False
        st.rerun()

# Bottone per mostrare il form di eliminazione ordine
if "show_form_delete_ordine" not in st.session_state:
    st.session_state.show_form_delete_ordine = False

if not st.session_state.show_form_delete_ordine:
    if st.button("Elimina Ordine"):
        st.session_state.show_form_delete_ordine = True
        st.rerun()

# Sezione per eliminare un ordine
if st.session_state.get("show_form_delete_ordine", False):
    st.write("### Elimina Ordine")
    with st.form(key='ordine_form_delete'):
        id_ordine = st.number_input("ID Ordine", min_value=1)

        submit_button = st.form_submit_button(label="Elimina Ordine")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            delete_recordSQL(session, "Ordini", f"ID_Ordine = {id_ordine}", {})
            st.success("Ordine eliminato con successo!")
            time.sleep(2)
            st.session_state.show_form_delete_ordine = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'eliminazione dell'ordine: {e}")
    elif cancel_button:
        st.session_state.show_form_delete_ordine = False
        st.rerun()