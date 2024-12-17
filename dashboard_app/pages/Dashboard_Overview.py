# File: pages/Dashboard_Overview.py
import streamlit as st
import pandas as pd
import altair as alt
from utils.MagDBcontroller import connessione, select_recordsSQL
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    switch_page("Login")
    st.stop()

# Titolo della pagina
st.title("Panoramica Dashboard di Magazzino")

# Sidebar menu
st.sidebar.page_link('Home.py', label='Home')
st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Bottone per il logout
if st.sidebar.button("Log Out"):
    st.session_state.clear()
    st.rerun()

# Funzione per ottenere i dati del dashboard
def fetch_dashboard_data(session):
    try:
        # Recupera il numero di lotti disponibili e prenotati
        lotti_data = select_recordsSQL(session, "Lotti", "COUNT(*) AS count, Stato", "Stato IN ('Disponibile', 'Prenotato')", None, "Stato")
        ordini_data = select_recordsSQL(session, "Ordini", "COUNT(*) AS count, Stato", "Stato IN ('In elaborazione', 'Spedito')", None, "Stato")

        # Organizzare i dati in un formato utilizzabile
        lotti_disponibili = next((item for item in lotti_data if item['Stato'] == 'Disponibile'), {}).get('count', 0)
        lotti_prenotati = next((item for item in lotti_data if item['Stato'] == 'Prenotato'), {}).get('count', 0)
        ordini_in_elaborazione = next((item for item in ordini_data if item['Stato'] == 'In elaborazione'), {}).get('count', 0)
        ordini_spediti = next((item for item in ordini_data if item['Stato'] == 'Spedito'), {}).get('count', 0)

        # Restituire i dati come dizionario
        return {
            'Lotti_Disponibili': lotti_disponibili,
            'Lotti_Prenotati': lotti_prenotati,
            'Ordini_In_Elaborazione': ordini_in_elaborazione,
            'Ordini_Spediti': ordini_spediti
        }
    except Exception as e:
        st.error(f"Errore durante il caricamento dei dati: {e}")
        return None

# Connessione al database
session = connessione()

# Ottieni i dati del dashboard
dashboard_data = fetch_dashboard_data(session)

if dashboard_data:
    # Mostriamo le statistiche principali
    st.write("### Riepilogo Operazioni Magazzino")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Lotti Disponibili", dashboard_data['Lotti_Disponibili'], delta=None, delta_color="normal")
    with col2:
        st.metric("Lotti Prenotati", dashboard_data['Lotti_Prenotati'], delta=None, delta_color="normal")
    with col3:
        st.metric("Ordini In Elaborazione", dashboard_data['Ordini_In_Elaborazione'], delta=None, delta_color="normal")
    with col4:
        st.metric("Ordini Spediti", dashboard_data['Ordini_Spediti'], delta=None, delta_color="normal")

    # Grafico a barre per visualizzare i dati
    st.write("### Visualizzazione Dati Magazzino")
    
    chart_data = pd.DataFrame({
        'Stato': ['Lotti Disponibili', 'Lotti Prenotati', 'Ordini In Elaborazione', 'Ordini Spediti'],
        'Quantità': [
            dashboard_data['Lotti_Disponibili'],
            dashboard_data['Lotti_Prenotati'],
            dashboard_data['Ordini_In_Elaborazione'],
            dashboard_data['Ordini_Spediti']
        ]
    })
    
    chart = alt.Chart(chart_data).mark_bar().encode(
        x='Stato',
        y='Quantità',
        color='Stato'
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

else:
    st.error("Impossibile recuperare i dati dal database.")
