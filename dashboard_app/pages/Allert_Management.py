import streamlit as st
import pandas as pd
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

# Gestione Allerte
st.write("## Gestione Allerte")

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
    st.sidebar.page_link('pages/Backup_Managment.py', label='Gestione Backup')
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

# Letture dei sensori di temperatura e umidità
letture_sensori = select_recordsSQL(session, "LettureSensori", colonne="ID_Sensore, Tipo, Valore, DataLettura", condizione="Tipo IN ('Temperatura', 'Umidità')", ordina_per="DataLettura DESC")

if letture_sensori:
    st.write("### Letture dei Sensori di Temperatura e Umidità")
    df_letture_sensori = pd.DataFrame(letture_sensori)
    st.dataframe(df_letture_sensori)
else:
    st.write("Nessun dato trovato per le letture dei sensori di temperatura e umidità.")

# Controllo scadenza dei lotti
lotti_scadenza = select_recordsSQL(session, "Lotti", colonne="ID_Lotto, Lotto, Scadenza, QuantitàProdotto", condizione="Scadenza <= CURDATE()", ordina_per="Scadenza ASC")

if lotti_scadenza:
    st.write("### Lotti in Scadenza")
    df_lotti_scadenza = pd.DataFrame(lotti_scadenza)
    st.dataframe(df_lotti_scadenza)
else:
    st.write("Nessun lotto in scadenza trovato.")

# Aggiungi una nuova allerta
def add_alert(tipo, tipo_evento, messaggio, id_sensore=None, id_lotto=None):
    alert_data = {
        "TipoNotifica": tipo,
        "TipoEvento": tipo_evento,
        "Messaggio": messaggio,
        "ID_Sensore": id_sensore,
        "ID_Lotto": id_lotto
    }
    add_recordSQL(session, "LogMagazzino", alert_data)

# Analizza le letture dei sensori e crea allerte
for _, row in df_letture_sensori.iterrows():
    if row['Tipo'] == 'Temperatura' and (row['Valore'] < 0 or row['Valore'] > 30):
        add_alert("Alarme", "Temperatura", f"Temperatura anomala rilevata: {row['Valore']} °C", id_sensore=row['ID_Sensore'])
    elif row['Tipo'] == 'Umidità' and (row['Valore'] < 30 or row['Valore'] > 70):
        add_alert("Alarme", "Umidità", f"Umidità anomala rilevata: {row['Valore']}%", id_sensore=row['ID_Sensore'])

# Analizza i lotti in scadenza e crea allerte
for _, row in df_lotti_scadenza.iterrows():
    add_alert("Avviso", "Scadenza Lotto", f"Lotto in scadenza: {row['Lotto']} (Quantità: {row['QuantitàProdotto']})", id_lotto=row['ID_Lotto'])

# Visualizza le allerte
allerte = select_recordsSQL(session, "LogMagazzino", colonne="ID_LogMagazzino, TipoNotifica, TipoEvento, Messaggio, DataOra", ordina_per="DataOra DESC")

if allerte:
    st.write("### Allerte")
    df_allerte = pd.DataFrame(allerte)
    st.dataframe(df_allerte)
else:
    st.write("Nessuna allerta trovata.")
