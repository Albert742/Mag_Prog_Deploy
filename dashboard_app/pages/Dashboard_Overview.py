# File: pages/Dashboard_Overview.py
import streamlit as st
import pandas as pd
from utils.MagDBcontroller import connessione, selectSQL

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    st.stop()

def fetch_dashboard_data():
    with connessione() as conn:
        # Query per ottenere le informazioni riassuntive dal magazzino
        query = """
        SELECT
            (SELECT COUNT(*) FROM Lotti WHERE Stato = 'Disponibile') AS Lotti_Disponibili,
            (SELECT COUNT(*) FROM Lotti WHERE Stato = 'Prenotato') AS Lotti_Prenotati,
            (SELECT COUNT(*) FROM Ordini WHERE Stato = 'In elaborazione') AS Ordini_In_Elaborazione,
            (SELECT COUNT(*) FROM Ordini WHERE Stato = 'Spedito') AS Ordini_Spediti
        """
        return pd.read_sql(query, conn)

# Titolo della pagina
st.title("Panoramica Dashboard di Magazzino")
st.sidebar.page_link('Home.py', label='Home')
st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Bottone per il logout
if st.sidebar.button("Log Out"):
    st.session_state.clear()
    st.rerun()

try:
    dashboard_data = fetch_dashboard_data()
    
    # Mostriamo le statistiche principali
    st.write("### Riepilogo Operazioni Magazzino")
    
    st.write(f"**Lotti Disponibili:** {dashboard_data['Lotti_Disponibili'][0]}")
    st.write(f"**Lotti Prenotati:** {dashboard_data['Lotti_Prenotati'][0]}")
    st.write(f"**Ordini In Elaborazione:** {dashboard_data['Ordini_In_Elaborazione'][0]}")
    st.write(f"**Ordini Spediti:** {dashboard_data['Ordini_Spediti'][0]}")
    
    # Grafico o altro tipo di visualizzazione
    st.write("### Visualizzazione Dati Magazzino")
    st.bar_chart(dashboard_data)
    
except Exception as e:
    st.error(f"Errore durante il caricamento dei dati: {e}")
