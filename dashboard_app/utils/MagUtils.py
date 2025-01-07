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

# Funzione per creare dati randomici per i sensori
def create_sensor_data():
    while not stop_event.is_set():
        with connessione() as conn:
            if conn:
                sensori = select_recordsSQL(conn, "Sensori")
                if not sensori:
                    print("Nessun sensore trovato.")
                    return

                letture = []
                for sensore in sensori:
                    id_sensore = sensore['ID_Sensore']
                    tipo = sensore['Tipo']
                    valore = None

                    if tipo == 'Temperatura':
                        valore = round(random.uniform(15.0, 35.0), 2)  # Valori di temperatura tra 15 e 35 gradi Celsius
                    elif tipo == 'Umidità':
                        valore = round(random.uniform(30.0, 70.0), 2)  # Valori di umidità tra 30% e 70%
                    elif tipo == 'Presenza':
                        valore = random.choice([0, 1])  # 0 per assenza, 1 per presenza

                    if valore is not None:
                        lettura = {
                            "ID_Sensore": id_sensore,
                            "Tipo": tipo,
                            "Valore": valore,
                            "DataLettura": datetime.datetime.now()
                        }
                        letture.append(lettura)

                for lettura in letture:
                    add_recordSQL(conn, "LettureSensori", lettura)

                print(f"Inserite {len(letture)} letture dei sensori.")

        # Aggiungi un ritardo tra le letture
        time.sleep(5)  # Ritardo di 5 secondi tra le letture

# Funzione per avviare la generazione dei dati dei sensori
def start_sensor_data_generation():
    stop_event.clear()
    threading.Thread(target=create_sensor_data).start()

# Funzione per fermare la generazione dei dati dei sensori
def stop_sensor_data_generation():
    stop_event.set()
