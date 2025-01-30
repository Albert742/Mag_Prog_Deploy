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
st.title("Gestione Logistica Interna")

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
    st.sidebar.page_link('pages/External_Logistic_Managment.py', label='Gestione Logistica Esterna')
    st.sidebar.page_link('pages/Internal_Logistic_Managment.py', label='Gestione Logistica Interna')
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

# Visualizza robot
robot = select_recordsSQL(session, "Robot")
if robot:
    df_robot = pd.DataFrame(robot)
    st.write("### Robot")
    st.dataframe(df_robot)
else:
    st.error("Errore nel recuperare i dati dei robot dal database.")

# Bottone per mostrare il form di aggiunta robot
if "show_form_add_robot" not in st.session_state:
    st.session_state.show_form_add_robot = False
if not st.session_state.show_form_add_robot:
    if st.button("Aggiungi Robot"):
        st.session_state.show_form_add_robot = True
        st.rerun()

# Sezione per aggiungere un robot
if st.session_state.get("show_form_add_robot", False):
    st.write("### Aggiungi Robot")
    with st.form(key='robot_form_add'):
        id_sensore = st.number_input("ID Sensore", min_value=1)
        id_zona = st.number_input("ID Zona", min_value=1)
        nome = st.text_input("Nome")
        stato = st.selectbox("Stato", ['Disponibile', 'Occupato', 'Manutenzione'])
        posizione_attuale = st.text_input("Posizione Attuale")
        capacita = st.number_input("Capacità", min_value=1)
        id_ricarica = st.number_input("ID Ricarica", min_value=1)

        submit_button = st.form_submit_button(label="Aggiungi Robot")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "Robot", {
                "ID_Sensore": id_sensore,
                "ID_Zona": id_zona,
                "Nome": nome,
                "Stato": stato,
                "PosizioneAttuale": posizione_attuale,
                "Capacita": capacita,
                "ID_Ricarica": id_ricarica
            })
            st.success("Robot aggiunto con successo!")
            time.sleep(2)
            st.session_state.show_form_add_robot = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta del robot: {e}")
    elif cancel_button:
        st.session_state.show_form_add_robot = False
        st.rerun()

# Visualizza stazioni di ricarica
stazioni_ricarica = select_recordsSQL(session, "StazioneRicarica")
if stazioni_ricarica:
    df_stazioni_ricarica = pd.DataFrame(stazioni_ricarica)
    st.write("### Stazioni di Ricarica")
    st.dataframe(df_stazioni_ricarica)
else:
    st.error("Errore nel recuperare i dati delle stazioni di ricarica dal database.")

# Bottone per mostrare il form di aggiunta stazione di ricarica
if "show_form_add_stazione_ricarica" not in st.session_state:
    st.session_state.show_form_add_stazione_ricarica = False
if not st.session_state.show_form_add_stazione_ricarica:
    if st.button("Aggiungi Stazione di Ricarica"):
        st.session_state.show_form_add_stazione_ricarica = True
        st.rerun()

# Sezione per aggiungere una stazione di ricarica
if st.session_state.get("show_form_add_stazione_ricarica", False):
    st.write("### Aggiungi Stazione di Ricarica")
    with st.form(key='stazione_ricarica_form_add'):
        zona_id = st.number_input("ID Zona", min_value=1)
        nome = st.text_input("Nome")
        stato = st.selectbox("Stato", ['Libera', 'Occupata', 'Inoperativa'])

        submit_button = st.form_submit_button(label="Aggiungi Stazione di Ricarica")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "StazioneRicarica", {
                "ZonaID": zona_id,
                "Nome": nome,
                "Stato": stato
            })
            st.success("Stazione di ricarica aggiunta con successo!")
            time.sleep(2)
            st.session_state.show_form_add_stazione_ricarica = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta della stazione di ricarica: {e}")
    elif cancel_button:
        st.session_state.show_form_add_stazione_ricarica = False
        st.rerun()

# Visualizza baie di carico/scarico
baie = select_recordsSQL(session, "BaieCaricoScarico")
if baie:
    df_baie = pd.DataFrame(baie)
    st.write("### Baie di Carico/Scarico")
    st.dataframe(df_baie)
else:
    st.error("Errore nel recuperare i dati delle baie di carico/scarico dal database.")

# Bottone per mostrare il form di aggiunta baia di carico/scarico
if "show_form_add_baia" not in st.session_state:
    st.session_state.show_form_add_baia = False
if not st.session_state.show_form_add_baia:
    if st.button("Aggiungi Baia di Carico/Scarico"):
        st.session_state.show_form_add_baia = True
        st.rerun()

# Sezione per aggiungere una baia di carico/scarico
if st.session_state.get("show_form_add_baia", False):
    st.write("### Aggiungi Baia di Carico/Scarico")
    with st.form(key='baia_form_add'):
        zona_id = st.number_input("ID Zona", min_value=1)
        nome = st.text_input("Nome")
        tipo = st.selectbox("Tipo", ['Carico', 'Scarico'])
        stato = st.selectbox("Stato", ['Libera', 'Occupata', 'Manutenzione'])

        submit_button = st.form_submit_button(label="Aggiungi Baia di Carico/Scarico")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "BaieCaricoScarico", {
                "ZonaID": zona_id,
                "Nome": nome,
                "Tipo": tipo,
                "Stato": stato
            })
            st.success("Baia di carico/scarico aggiunta con successo!")
            time.sleep(2)
            st.session_state.show_form_add_baia = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta della baia di carico/scarico: {e}")
    elif cancel_button:
        st.session_state.show_form_add_baia = False
        st.rerun()

# Visualizza richieste di movimento
richieste_movimento = select_recordsSQL(session, "RichiesteMovimento")
if richieste_movimento:
    df_richieste_movimento = pd.DataFrame(richieste_movimento)
    st.write("### Richieste di Movimento")
    st.dataframe(df_richieste_movimento)
else:
    st.error("Errore nel recuperare i dati delle richieste di movimento dal database.")

# Bottone per mostrare il form di aggiunta richiesta di movimento
if "show_form_add_richiesta_movimento" not in st.session_state:
    st.session_state.show_form_add_richiesta_movimento = False
if not st.session_state.show_form_add_richiesta_movimento:
    if st.button("Aggiungi Richiesta di Movimento"):
        st.session_state.show_form_add_richiesta_movimento = True
        st.rerun()

# Sezione per aggiungere una richiesta di movimento
if st.session_state.get("show_form_add_richiesta_movimento", False):
    st.write("### Aggiungi Richiesta di Movimento")
    with st.form(key='richiesta_movimento_form_add'):
        id_lotto = st.number_input("ID Lotto", min_value=1)
        id_zona_partenza = st.number_input("ID Zona Partenza", min_value=1)
        id_zona_destinazione = st.number_input("ID Zona Destinazione", min_value=1)
        id_scaffalatura_destinazione = st.number_input("ID Scaffalatura Destinazione", min_value=1)
        id_robot = st.number_input("ID Robot", min_value=1)
        priorita = st.selectbox("Priorità", ['Bassa', 'Media', 'Alta'])
        data_richiesta = st.date_input("Data Richiesta")

        submit_button = st.form_submit_button(label="Aggiungi Richiesta di Movimento")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "RichiesteMovimento", {
                "ID_Lotto": id_lotto,
                "ID_Zona_Partenza": id_zona_partenza,
                "ID_Zona_Destinazione": id_zona_destinazione,
                "ID_Scaffalatura_Destinazione": id_scaffalatura_destinazione,
                "ID_Robot": id_robot,
                "Priorita": priorita,
                "DataRichiesta": data_richiesta
            })
            st.success("Richiesta di movimento aggiunta con successo!")
            time.sleep(2)
            st.session_state.show_form_add_richiesta_movimento = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta della richiesta di movimento: {e}")
    elif cancel_button:
        st.session_state.show_form_add_richiesta_movimento = False
        st.rerun()

# Visualizza dettagli movimento
dettagli_movimento = select_recordsSQL(session, "DettagliMovimento")
if dettagli_movimento:
    df_dettagli_movimento = pd.DataFrame(dettagli_movimento)
    st.write("### Dettagli Movimento")
    st.dataframe(df_dettagli_movimento)
else:
    st.error("Errore nel recuperare i dati dei dettagli movimento dal database.")

# Bottone per mostrare il form di aggiunta dettaglio movimento
if "show_form_add_dettaglio_movimento" not in st.session_state:
    st.session_state.show_form_add_dettaglio_movimento = False
if not st.session_state.show_form_add_dettaglio_movimento:
    if st.button("Aggiungi Dettaglio Movimento"):
        st.session_state.show_form_add_dettaglio_movimento = True
        st.rerun()

# Sezione per aggiungere un dettaglio movimento
if st.session_state.get("show_form_add_dettaglio_movimento", False):
    st.write("### Aggiungi Dettaglio Movimento")
    with st.form(key='dettaglio_movimento_form_add'):
        id_richiesta = st.number_input("ID Richiesta", min_value=1)
        id_lotto = st.number_input("ID Lotto", min_value=1)
        id_robot = st.number_input("ID Robot", min_value=1)
        id_zona_partenza = st.number_input("ID Zona Partenza", min_value=1)
        id_zona_destinazione = st.number_input("ID Zona Destinazione", min_value=1)
        id_scaffalatura_destinazione = st.number_input("ID Scaffalatura Destinazione", min_value=1)
        stato = st.selectbox("Stato", ['Assegnato', 'In corso', 'Completato', 'Annullato'])
        data_movimento = st.date_input("Data Movimento")
        data_completamento = st.date_input("Data Completamento")
        tipo_movimento = st.selectbox("Tipo Movimento", ['Entrata', 'Uscita', 'Spostamento'])

        submit_button = st.form_submit_button(label="Aggiungi Dettaglio Movimento")
        cancel_button = st.form_submit_button(label="Annulla")

    if submit_button:
        try:
            add_recordSQL(session, "DettagliMovimento", {
                "ID_Richiesta": id_richiesta,
                "ID_Lotto": id_lotto,
                "ID_Robot": id_robot,
                "ID_Zona_Partenza": id_zona_partenza,
                "ID_Zona_Destinazione": id_zona_destinazione,
                "ID_Scaffalatura_Destinazione": id_scaffalatura_destinazione,
                "Stato": stato,
                "DataMovimento": data_movimento,
                "DataCompletamento": data_completamento,
                "TipoMovimento": tipo_movimento
            })
            st.success("Dettaglio movimento aggiunto con successo!")
            time.sleep(2)
            st.session_state.show_form_add_dettaglio_movimento = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta del dettaglio movimento: {e}")
    elif cancel_button:
        st.session_state.show_form_add_dettaglio_movimento = False
        st.rerun()