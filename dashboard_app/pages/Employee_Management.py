import pandas as pd
import streamlit as st
import time
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL
from utils.MagUtils import create_employee_id, log_logout
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima o accedi con un account autorizzato.")
    time.sleep(2)
    switch_page("Login")
    st.stop()
    
# Titolo della pagina
st.title("Gestione Dipendenti")

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

# Sezione per visualizzare i dipendenti
st.write("### Elenco dei Dipendenti Attuali")
employees = select_recordsSQL(connessione(), "Dipendenti")
if employees:
    df_employees = pd.DataFrame(employees)
    st.dataframe(df_employees)
else:
    st.write("Nessun dipendente trovato.")


# Bottone per mostrare il form di aggiunta dipendente
if "show_form_add" not in st.session_state:
    st.session_state.show_form_add = False

if not st.session_state.show_form_add:
    if st.button("Aggiungi Nuovo Dipendente"):
        st.session_state.show_form_add = True
        st.rerun()

# Sezione per aggiungere un nuovo dipendente
if st.session_state.get("show_form_add", False):
    st.write("### Aggiungi Nuovo Dipendente")
    with st.form(key='employee_form_add'):
        codicefiscale = st.text_input("Codice Fiscale", max_chars=16)
        nome = st.text_input("Nome")
        cognome = st.text_input("Cognome")
        ruolo = st.selectbox("Ruolo", options=["Amministratore", "Operatore", "Tecnico"])
        mansione = st.selectbox("Mansione", options=["Manager", "Tecnico", "Manutenzione", "Magazziniere", "Responsabile Magazzino", "Addetto Carico/Scarico", "Operatore Logistico", "Coordinatore Magazzino", "Pianificatore", "Controllo Qualità"])
        dataassunzione = st.date_input("Data di Assunzione")
        
        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Aggiungi Dipendente")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
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
                        st.rerun() 
                    else:
                        st.error("Errore durante l'aggiunta del dipendente.")
            else:
                st.error("Tutti i campi sono obbligatori.")
        elif cancel_button:
            st.session_state.show_form_add = False
            st.rerun()

# Bottone per mostrare il form di aggiornamento dipendente
if "show_form_update" not in st.session_state:
    st.session_state.show_form_update = False

if not st.session_state.show_form_update:
    if st.button("Aggiorna Dipendente"):
        st.session_state.show_form_update = True
        st.rerun()

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
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
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

# Bottone per mostrare il form di eliminazione dipendente
if "show_form_delete" not in st.session_state:
    st.session_state.show_form_delete = False

if not st.session_state.show_form_delete:
    if st.button("Elimina Dipendente"):
        st.session_state.show_form_delete = True
        st.rerun()

# Sezione per eliminare un dipendente
if st.session_state.get("show_form_delete", False):
    st.write("### Elimina Dipendente")
    with st.form(key='employee_form_delete'):
        employee_id = st.text_input("ID Dipendente")
        
        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Elimina Dipendente")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if employee_id:
                # Elimina il dipendente dal database
                if delete_employee(employee_id):
                    st.success("Dipendente eliminato con successo!")
                    time.sleep(2)
                    st.session_state.show_form_delete = False
                    st.rerun()
                else:
                    st.error("Errore durante l'eliminazione del dipendente.")
            else:
                st.error("ID Dipendente è obbligatorio.")
        elif cancel_button:
            st.session_state.show_form_delete = False
            st.rerun()
            
# Visualizza turni dipendenti
st.write("### Turni Dipendenti")
turni_dipendenti = select_recordsSQL(connessione(), "TurniDipendenti")
if turni_dipendenti:
    df_turni_dipendenti = pd.DataFrame(turni_dipendenti)
    st.dataframe(df_turni_dipendenti)
else:
    st.write("Nessun turno dipendente trovato.")

# Bottone per mostrare il form di aggiunta turno
if "show_form_add_turno" not in st.session_state:
    st.session_state.show_form_add_turno = False

if not st.session_state.show_form_add_turno:
    if st.button("Aggiungi Turno"):
        st.session_state.show_form_add_turno = True
        st.rerun()

# Sezione per aggiungere un nuovo turno
if st.session_state.get("show_form_add_turno", False):
    st.write("### Aggiungi Nuovo Turno")
    with st.form(key='turno_form_add'):
        id_dipendente = st.text_input("ID Dipendente")
        data_turno = st.date_input("Data Turno")
        ora_inizio = st.time_input("Ora Inizio")
        ora_fine = st.time_input("Ora Fine")

        submit_button = st.form_submit_button(label="Aggiungi Turno")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if id_dipendente and data_turno and ora_inizio and ora_fine:
                try:
                    session = connessione()
                    if session:
                        new_turno_data = {
                            "ID_Dipendente": id_dipendente,
                            "DataTurno": data_turno,
                            "OraInizio": ora_inizio,
                            "OraFine": ora_fine
                        }
                        add_recordSQL(session, "TurniDipendenti", new_turno_data)
                        st.success("Turno aggiunto con successo!")
                        time.sleep(2)
                        st.session_state.show_form_add_turno = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Errore durante l'aggiunta del turno: {e}")
            else:
                st.error("Tutti i campi sono obbligatori.")
        elif cancel_button:
            st.session_state.show_form_add_turno = False
            st.rerun()
