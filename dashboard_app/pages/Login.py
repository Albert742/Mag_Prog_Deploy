import streamlit as st
from utils.MagDBcontroller import connessione, add_recordSQL, select_recordsSQL
from utils.MagUtils import log_azione
import bcrypt


# Hash password con bcrypt
def hash_password(password):
    # Genera un salt e hash la password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password

# Verifica password
def verifica_password(password, hashed_password):
    # Verifica se la password fornita corrisponde all'hash memorizzato
    return bcrypt.checkpw(password.encode(), hashed_password)

# Autentica le credenziali dell'utente
def autentica_utente(username, password):
    with connessione() as conn:
        if conn:
            condizione = "Username = :username"
            args = {"username": username}
            result = select_recordsSQL(conn, "Credenziali", "ID_Utente, Password, Ruolo", condizione, args)
            if result:
                if len(result) == 1:  # Assicura che ci sia un solo utente corrispondente
                    id_utente = result[0]['ID_Utente']
                    hashed_password = result[0]['Password']
                    ruolo = result[0]['Ruolo']
                    if verifica_password(password, hashed_password):
                        log_azione(id_utente, "Accesso", "Successo", f"Utente {username} ha effettuato l'accesso con successo.")
                        return True, ruolo, id_utente
                    else:
                        log_azione(id_utente, "Accesso", "Fallito", f"Utente {username} ha fallito l'accesso.")
    return False, None, None

# Funzione per registrare un nuovo utente
def registra_utente(username, password, employee_id):
    with connessione() as conn:
        if conn:
            # Verifica se l'ID Dipendente esiste e ottieni il ruolo
            condizione = "ID_Dipendente = :employee_id"
            args = {"employee_id": employee_id}
            result = select_recordsSQL(conn, "Dipendenti", "Ruolo", condizione, args)
            if result:
                role = result[0]['Ruolo']
                hashed_password = hash_password(password)
                new_user_data = {
                    "ID_Dipendente": employee_id,
                    "Username": username,
                    "Password": hashed_password,
                    "Ruolo": role
                }
                try:
                    success = add_recordSQL(conn, "Credenziali", new_user_data)
                    if success:
                        st.success("Registrazione avvenuta con successo! Esegui l'accesso.")
                        # Log registrazione
                        id_utente = select_recordsSQL(conn, "Credenziali", "ID_Utente", "Username = :username", {"username": username})[0]['ID_Utente']
                        log_azione(id_utente, "Registrazione", "Successo", f"Utente {username} registrato con successo.")
                    else:
                        st.error("Registrazione fallita, username già esistente o altri errori.")
                        log_azione(None, "Registrazione", "Fallito", f"Registrazione fallita per l'utente, {username} gia esistente.")
                except Exception as e:
                    st.error(f"Errore durante la registrazione: {e}")
            else:
                st.error("ID Dipendente non valido.")
                log_azione(None, "Registrazione", "Fallito", f"Registrazione fallita per l'utente {username}, ID Dipendente non valido.")

# Crea form di login/registrazione
def login_signup():
    st.title("Accesso al magazzino")

    # Seleziona login o signup
    option = st.radio("Scegli un'opzione:", ["Accedi", "Registrati"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Registrati":
        employee_id = st.text_input("ID Dipendente")
        if st.button("Registrati"):
            registra_utente(username, password, employee_id)
    elif option == "Accedi":
        if st.button("Accedi"):
            user, ruolo, id_utente = autentica_utente(username, password)
            if user:
                st.success("Accesso avvenuto con successo!")
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["ruolo"] = ruolo
                st.session_state["id_utente"] = id_utente
                st.switch_page("Home.py")
                st.rerun()
            else:
                st.error("Credenziali non valide!")

if __name__ == "__main__":
    login_signup()