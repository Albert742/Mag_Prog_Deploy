import streamlit as st
import pandas as pd
import time
from utils.MagDBcontroller import connessione, select_recordsSQL

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

# Funzione per ottenere i dati del dashboard
def fetch_dashboard_data(session):
    try:
        # Recupera il numero di lotti disponibili e prenotati
        lotti_data = select_recordsSQL(session, "Lotti", "COUNT(*) AS count, Stato", "Stato IN ('Disponibile', 'Prenotato')", None, "Stato")
        ordini_data = select_recordsSQL(session, "Ordini", "COUNT(*) AS count, Stato", "Stato IN ('In elaborazione', 'Spedito')", None, "Stato")
        prodotti_data = select_recordsSQL(session, "Prodotti", "COUNT(*) AS count", None)
        clienti_data = select_recordsSQL(session, "Clienti", "COUNT(*) AS count", None)
        fornitori_data = select_recordsSQL(session, "Fornitori", "COUNT(*) AS count", None)
        prodotti_in_stock_data = select_recordsSQL(session, "Lotti", "ID_Prodotto, SUM(Quantita) AS Quantita", "Stato = 'Disponibile'", None, "ID_Prodotto")

        # Recupera i nomi dei prodotti
        prodotti_nomi = select_recordsSQL(session, "Prodotti", "ID_Prodotto, Nome", None)

        # Organizzare i dati in un formato utilizzabile
        lotti_disponibili = next((item for item in lotti_data if item['Stato'] == 'Disponibile'), {}).get('count', 0)
        lotti_prenotati = next((item for item in lotti_data if item['Stato'] == 'Prenotato'), {}).get('count', 0)
        ordini_in_elaborazione = next((item for item in ordini_data if item['Stato'] == 'In elaborazione'), {}).get('count', 0)
        ordini_spediti = next((item for item in ordini_data if item['Stato'] == 'Spedito'), {}).get('count', 0)
        numero_prodotti = prodotti_data[0]['count'] if prodotti_data else 0
        numero_clienti = clienti_data[0]['count'] if clienti_data else 0
        numero_fornitori = fornitori_data[0]['count'] if fornitori_data else 0

        # Mappa ID_Prodotto a Nome
        prodotti_nomi_dict = {item['ID_Prodotto']: item['Nome'] for item in prodotti_nomi}

        # Aggiungi i nomi dei prodotti ai dati di stock
        for item in prodotti_in_stock_data:
            item['Nome'] = prodotti_nomi_dict.get(item['ID_Prodotto'], 'Unknown')

        # Restituire i dati come dizionario
        return {
            'Lotti_Disponibili': lotti_disponibili,
            'Lotti_Prenotati': lotti_prenotati,
            'Ordini_In_Elaborazione': ordini_in_elaborazione,
            'Ordini_Spediti': ordini_spediti,
            'Numero_Prodotti': numero_prodotti,
            'Numero_Clienti': numero_clienti,
            'Numero_Fornitori': numero_fornitori,
            'Lotti_Data': lotti_data,
            'Ordini_Data': ordini_data,
            'Prodotti_In_Stock_Data': prodotti_in_stock_data
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

    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric("Numero di Prodotti", dashboard_data['Numero_Prodotti'], delta=None, delta_color="normal")
    with col6:
        st.metric("Numero di Clienti", dashboard_data['Numero_Clienti'], delta=None, delta_color="normal")
    with col7:
        st.metric("Numero di Fornitori", dashboard_data['Numero_Fornitori'], delta=None, delta_color="normal")

    # Visualizzazione dei dati in forma di grafici
    st.write("### Dettagli dei Lotti")
    lotti_df = pd.DataFrame(dashboard_data['Lotti_Data'])
    st.bar_chart(lotti_df.set_index('Stato'))

    st.write("### Dettagli degli Ordini")
    ordini_df = pd.DataFrame(dashboard_data['Ordini_Data'])
    st.bar_chart(ordini_df.set_index('Stato'))

    st.write("### Prodotti in Stock")
    prodotti_in_stock_df = pd.DataFrame(dashboard_data['Prodotti_In_Stock_Data'])
    st.bar_chart(prodotti_in_stock_df.set_index('ID_Prodotto'))

    # Visualizzazione dei prodotti in stock con i nomi
    st.write("### Prodotti in Stock Dettagliati")
    for item in dashboard_data['Prodotti_In_Stock_Data']:
        st.write(f"{item['Nome']}: {item['Quantita']}")

    st.write("### Prodotti per Fornitore")
    prodotti_per_fornitore = select_recordsSQL(session, "Prodotti", "ID_Fornitore, COUNT(*) AS count", None, None, "ID_Fornitore")
    if prodotti_per_fornitore:
        prodotti_per_fornitore_df = pd.DataFrame(prodotti_per_fornitore)
        st.bar_chart(prodotti_per_fornitore_df.set_index('ID_Fornitore'))

    st.write("### Ordini per Cliente")
    ordini_per_cliente = select_recordsSQL(session, "Ordini", "ID_Cliente, COUNT(*) AS count", "ID_Cliente IS NOT NULL", None, "ID_Cliente")
    if ordini_per_cliente:
        ordini_per_cliente_df = pd.DataFrame(ordini_per_cliente)
        st.bar_chart(ordini_per_cliente_df.set_index('ID_Cliente'))
else:
    st.write("Nessun dato disponibile per il dashboard.")