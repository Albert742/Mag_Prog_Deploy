
import pandas as pd
import streamlit as st
import time
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL
from utils.MagUtils import create_employee_id
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

# Funzione per verificare se un dipendente con lo stesso codice fiscale esiste già
def check_duplicate(codicefiscale):
    try:
        session = connessione()
        if session:
            condizione = "CodiceFiscale = :codicefiscale"
            args = {"codicefiscale": codicefiscale}
            result = select_recordsSQL(session, "Dipendenti", "ID_Dipendente", condizione, args)
            session.close()
            return len(result) > 0
    except Exception as e:
        st.error(f"Errore durante la verifica del duplicato: {e}")
        return False

# Funzione per aggiungere un nuovo dipendente
def add_employee(employee_id, codicefiscale, nome, cognome, ruolo, mansione, dataassunzione):
    try:
        session = connessione()
        if session:
            new_employee_data = {
                "ID_Dipendente": employee_id,
                "CodiceFiscale": codicefiscale,
                "Nome": nome,
                "Cognome": cognome,
                "Ruolo": ruolo,
                "Mansione": mansione,
                "DataAssunzione": dataassunzione
            }
            success = add_recordSQL(session, "Dipendenti", new_employee_data)
            session.close()
            return success
    except Exception as e:
        st.error(f"Errore durante l'aggiunta del dipendente: {e}")
        return False

# Funzione per aggiornare un dipendente
def update_employee(employee_id, codicefiscale, nome, cognome, ruolo, mansione, dataassunzione):
    try:
        session = connessione()
        if session:
            update_data = {
                "CodiceFiscale": codicefiscale,
                "Nome": nome,
                "Cognome": cognome,
                "Ruolo": ruolo,
                "Mansione": mansione,
                "DataAssunzione": dataassunzione
            }
            condizione = "ID_Dipendente = :employee_id"
            args = {"employee_id": employee_id}
            success = update_recordSQL(session, "Dipendenti", update_data, condizione, args)
            session.close()
            return success
    except Exception as e:
        st.error(f"Errore durante l'aggiornamento del dipendente: {e}")
        return False

# Funzione per eliminare un dipendente
def delete_employee(employee_id):
    try:
        session = connessione()
        if session:
            condizione = "ID_Dipendente = :employee_id"
            args = {"employee_id": employee_id}
            success = delete_recordSQL(session, "Dipendenti", condizione, args)
            session.close()
            return success
    except Exception as e:
        st.error(f"Errore durante l'eliminazione del dipendente: {e}")
        return False

st.sidebar.page_link('Home.py', label='Home')
st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Bottone per il logout
if st.sidebar.button("Log Out"):
    st.success("Logout effettuato con successo. Verrai reindirizzato alla pagina di login.")
    time.sleep(2)
    st.session_state.clear()
    st.rerun()

# Sezione per visualizzare i dipendenti
st.write("### Elenco dei Dipendenti Attuali")
employees = select_recordsSQL(connessione(), "Dipendenti")
if employees:
    df_employees = pd.DataFrame(employees)
    st.dataframe(df_employees)
else:
    st.write("Nessun dipendente trovato.")

# Bottone per mostrare il form di aggiunta dipendente
if st.button("Aggiungi Nuovo Dipendente"):
    st.session_state.show_form_add = True

# Bottone per mostrare il form di aggiornamento dipendente
if st.button("Aggiorna Dipendente"):
    st.session_state.show_form_update = True

# Bottone per mostrare il form di eliminazione dipendente
if st.button("Elimina Dipendente"):
    st.session_state.show_form_delete = True

# Sezione per aggiungere un nuovo dipendente
if st.session_state.get("show_form_add", False):
    st.write("### Aggiungi Nuovo Dipendente")
    with st.form(key='employee_form_add'):
        codicefiscale = st.text_input("Codice Fiscale", max_chars=16)
        nome = st.text_input("Nome")
        cognome = st.text_input("Cognome")
        ruolo = st.selectbox("Ruolo", options=["Amministratore", "Operatore", "Tecnico"])
        mansione = st.selectbox("Mansione", options=["Amministratore", "Tecnico", "Manutenzione", "Magazziniere", "Responsabile Magazzino", "Addetto Carico/Scarico", "Operatore Logistico", "Coordinatore Magazzino", "Pianificatore", "Controllo Qualità"])
        dataassunzione = st.date_input("Data di Assunzione")
        
        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Aggiungi Dipendente")
        cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if codicefiscale and nome and cognome and ruolo and mansione and dataassunzione:
                # Verifica se esiste già un dipendente con lo stesso codice fiscale
                if check_duplicate(codicefiscale):
                    st.error("Un dipendente con questo codice fiscale esiste già.")
                else:
                    # Genera l'ID dipendente
                    employee_id = create_employee_id(codicefiscale, nome, cognome, ruolo, str(dataassunzione))
                    
                    # Aggiungi il nuovo dipendente nel database
                    if add_employee(employee_id, codicefiscale, nome, cognome, ruolo, mansione, dataassunzione):
                        st.success("Dipendente aggiunto con successo!")
                        time.sleep(2)
                        st.session_state.show_form_add = False
                        st.rerun()  # Ricarica la pagina per visualizzare l'aggiornamento
                    else:
                        st.error("Errore durante l'aggiunta del dipendente.")
            else:
                st.error("Tutti i campi sono obbligatori.")
        elif cancel_button:
            st.session_state.show_form_add = False
            st.rerun()  # Ricarica la pagina per nascondere il form

# Sezione per aggiornare un dipendente
if st.session_state.get("show_form_update", False):
    st.write("### Aggiorna Dipendente")
    with st.form(key='employee_form_update'):
        employee_id = st.text_input("ID Dipendente")
        codicefiscale = st.text_input("Codice Fiscale", max_chars=16)
        nome = st.text_input("Nome")
        cognome = st.text_input("Cognome")
        ruolo = st.selectbox("Ruolo", options=["Amministratore", "Tecnico", "Operaio"])
        mansione = st.selectbox("Mansione", options=["Manager", "Tecnico IT", "Manutenzione", "Magazziniere", "Responsabile Magazzino", "Addetto Carico/Scarico", "Operatore Logistico", "Coordinatore Magazzino", "Pianificatore", "Controllo Qualità"])
        dataassunzione = st.date_input("Data di Assunzione")
        
        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Aggiorna Dipendente")
        cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if employee_id and codicefiscale and nome and cognome and ruolo and mansione and dataassunzione:
                # Aggiorna il dipendente nel database
                if update_employee(employee_id, codicefiscale, nome, cognome, ruolo, mansione, dataassunzione):
                    st.success("Dipendente aggiornato con successo!")
                    time.sleep(2)
                    st.session_state.show_form_update = False
                    st.rerun()
                else:
                    st.error("Errore durante l'aggiornamento del dipendente.")
            else:
                st.error("Tutti i campi sono obbligatori.")
        elif cancel_button:
            st.session_state.show_form_update = False
            st.rerun()

# Sezione per eliminare un dipendente
if st.session_state.get("show_form_delete", False):
    st.write("### Elimina Dipendente")
    with st.form(key='employee_form_delete'):
        employee_id = st.text_input("ID Dipendente")
        
        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Elimina Dipendente")
        cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if employee_id:
                # Elimina il dipendente dal database
                if delete_employee(employee_id):
                    st.success("Dipendente eliminato con successo!")
                    time.sleep(2)
                    st.session_state.show_form_delete = False
                    st.rerun()  # Ricarica la pagina per visualizzare l'aggiornamento
                else:
                    st.error("Errore durante l'eliminazione del dipendente.")
            else:
                st.error("ID Dipendente è obbligatorio.")
        elif cancel_button:
            st.session_state.show_form_delete = False
            st.rerun()  # Ricarica la pagina per nascondere il form