# File: pages/Employee_Management.py
import hashlib
import streamlit as st
import pandas as pd
from utils.MagDBcontroller import connessione, select_recordsSQL
from streamlit_extras.switch_page_button import switch_page

# Funzione per creare un ID dipendente univoco
def create_employee_id(codicefiscale, nome, cognome, ruolo, dataassunzione):
    """
    Crea un ID dipendente unico dato il codice fiscale, nome, cognome, ruolo e data di assunzione.
    """
    concatenated_string = f"{codicefiscale}{nome}{cognome}{ruolo}{dataassunzione}"
    hashed_string = hashlib.sha256(concatenated_string.encode()).hexdigest()
    employee_id = hashed_string[:10]
    return employee_id

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    switch_page("Login")
    st.stop()



# Funzione per verificare se un dipendente con lo stesso codice fiscale esiste già
def check_duplicate(codicefiscale):
    try:
        # Verifica la duplicazione del codice fiscale
        query = "SELECT COUNT(*) FROM Dipendenti WHERE CodiceFiscale = %s"
        result = select_recordsSQL(connessione(), "Dipendenti", query, (codicefiscale,))
        return result[0][0] > 0
    except Exception as e:
        st.error(f"Errore durante il controllo duplicati: {e}")
        return False

# Funzione per aggiungere un nuovo dipendente
def add_employee(employee_id, codicefiscale, nome, cognome, ruolo, dataassunzione):
    try:
        # Inserisce il nuovo dipendente nel database
        query = """
        INSERT INTO Dipendenti (ID_Dipendente, CodiceFiscale, Nome, Cognome, Ruolo, DataAssunzione)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (employee_id, codicefiscale, nome, cognome, ruolo, dataassunzione)
        with connessione() as conn:
            conn.execute(query, data)
    except Exception as e:
        st.error(f"Errore durante l'aggiunta del dipendente: {e}")

# Titolo della pagina
st.title("Gestione Dipendenti")
st.sidebar.page_link('Home.py', label='Home')
st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Bottone per il logout
if st.sidebar.button("Log Out"):
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

# Sezione per aggiungere un nuovo dipendente
st.write("### Aggiungi Nuovo Dipendente")
with st.form(key='employee_form'):
    codicefiscale = st.text_input("Codice Fiscale", max_chars=16)
    nome = st.text_input("Nome")
    cognome = st.text_input("Cognome")
    ruolo = st.selectbox("Ruolo", options=["Magazziniere", "Responsabile", "Amministratore", "Operaio"])
    dataassunzione = st.date_input("Data di Assunzione")
    
    # Crea il bottone per inviare il form
    submit_button = st.form_submit_button(label="Aggiungi Dipendente")

    if submit_button:
        if codicefiscale and nome and cognome and ruolo and dataassunzione:
            # Verifica se esiste già un dipendente con lo stesso codice fiscale
            if check_duplicate(codicefiscale):
                st.error("Un dipendente con questo codice fiscale esiste già.")
            else:
                # Genera l'ID dipendente
                employee_id = create_employee_id(codicefiscale, nome, cognome, ruolo, str(dataassunzione))
                
                # Aggiungi il nuovo dipendente nel database
                add_employee(employee_id, codicefiscale, nome, cognome, ruolo, dataassunzione)
                st.success("Dipendente aggiunto con successo!")
                st.rerun()  # Ricarica la pagina per visualizzare l'aggiornamento
        else:
            st.error("Tutti i campi sono obbligatori.")
