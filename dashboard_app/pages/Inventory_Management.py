# File: pages/Inventory_Management.py
import streamlit as st
import pandas as pd
from utils.MagDBcontroller import connessione, selectSQL
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    switch_page("Login")
    st.stop()

def fetch_inventory_data():
    with connessione() as conn:
        # Query per ottenere i dettagli completi dell'inventario
        query = """
        SELECT 
            Prodotti.Nome AS Prodotto, 
            Prodotti.Codice AS Codice_Prodotto, 
            Zone.Nome AS Zona, 
            Scaffalature.Nome AS Scaffalatura, 
            Lotti.Quantita, 
            Lotti.Scadenza, 
            Lotti.Stato
        FROM Lotti
        JOIN Prodotti ON Lotti.ID_Prodotto = Prodotti.ID_Prodotto
        JOIN Zone ON Lotti.ID_Zona = Zone.ID_Zona
        JOIN Scaffalature ON Lotti.ID_Scaffalatura = Scaffalature.ID_Scaffalatura
        ORDER BY Prodotti.Nome, Zone.Nome, Lotti.Scadenza
        """
        return pd.read_sql(query, conn)

# Titolo della pagina
st.title("Gestione Inventario")
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
    # Carica i dati dell'inventario
    inventory_data = fetch_inventory_data()
    
    # Visualizza il riepilogo dell'inventario
    st.write("### Dettagli Inventario")
    
    # Visualizza i dati in formato tabella
    st.dataframe(inventory_data)
    
    # Opzionalmente, puoi aggiungere dei filtri per l'utente, come ad esempio per prodotto o zona
    st.write("### Filtra Inventario")
    
    prodotto_filtro = st.selectbox("Seleziona il prodotto:", options=inventory_data['Prodotto'].unique())
    zona_filtro = st.selectbox("Seleziona la zona:", options=inventory_data['Zona'].unique())
    
    # Applica i filtri
    filtered_data = inventory_data[
        (inventory_data['Prodotto'] == prodotto_filtro) & 
        (inventory_data['Zona'] == zona_filtro)
    ]
    
    # Mostra i dati filtrati
    if not filtered_data.empty:
        st.write(f"Risultati per prodotto: {prodotto_filtro} e zona: {zona_filtro}")
        st.dataframe(filtered_data)
    else:
        st.write("Nessun dato trovato per i criteri selezionati.")
        
except Exception as e:
    st.error(f"Errore durante il caricamento dei dati: {e}")
