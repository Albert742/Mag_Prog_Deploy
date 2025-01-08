"""
Modulo contenente funzioni per il funzionamento e test.
"""
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx
import hashlib
from utils.MagDBcontroller import connessione, add_recordSQL, select_recordsSQL
#from MagDBcontroller import connessione, add_recordSQL, select_recordsSQL
import random
import datetime
import time
import threading

# Funzione per creare un ID dipendente unico
def create_employee_id(codicefiscale, nome, cognome, ruolo, dataassunzione):
    """
    Crea un ID dipendente unico dato il codice fiscale, nome, cognome, ruolo e data di assunzione.
    """
    concatenated_string = f"{codicefiscale}{nome}{cognome}{ruolo}{dataassunzione}"
    hashed_string = hashlib.sha256(concatenated_string.encode()).hexdigest()
    employee_id = hashed_string[:10]
    return employee_id

# Funzione per ottenere l'IP dell'utente
def get_remote_ip():
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

# Funzione per registrare le azioni nella tabella LogUtenti
def log_azione(id_utente, tipo, esito, dettagli=""):
    ip = get_remote_ip()
    log_data = {
        "ID_Utente": id_utente,
        "Tipo": tipo,
        "Esito": esito,
        "IP": ip,
        "Dettagli": dettagli
    }
    with connessione() as conn:
        if conn:
            add_recordSQL(conn, "LogUtenti", log_data)

# Funzione per registrare il logout nella tabella LogUtenti
def log_logout(id_utente):
    """
    Registra il logout nella tabella LogUtenti.
    """
    ip = get_remote_ip()
    log_data = {
        "ID_Utente": id_utente,
        "Tipo": "Logout",
        "Esito": "Successo",
        "IP": ip,
        "Dettagli": f"Utente {id_utente} ha effettuato il logout con successo."
    }
    with connessione() as conn:
        if conn:
            add_recordSQL(conn, "LogUtenti", log_data)

# Flag per controllare l'esecuzione della generazione dei dati dei sensori
stop_event = threading.Event()

