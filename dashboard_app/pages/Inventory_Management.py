import streamlit as st
import pandas as pd
import time
from sqlalchemy import text
from utils.MagDBcontroller import connessione, select_recordsSQL
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    switch_page("Login")
    st.stop()

# Titolo della pagina
st.title("Gestione Inventario")

# Sidebar menu
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

# Connessione al database
session = connessione()

# Visualizza prodotti
st.subheader("Prodotti")
prodotti = select_recordsSQL(session, "Prodotti")

if prodotti:
    df_prodotti = pd.DataFrame(prodotti)
    st.dataframe(df_prodotti)
else:
    st.error("Errore nel recuperare i prodotti dal database.")

# Visualizza zone di magazzino
st.subheader("Zone di Magazzino")
zone = select_recordsSQL(session, "Zone")

if zone:
    df_zone = pd.DataFrame(zone)
    st.dataframe(df_zone)
else:
    st.error("Errore nel recuperare le zone di magazzino dal database.")

# Visualizza scaffalature
st.subheader("Scaffalature")
scaffalature = select_recordsSQL(session, "Scaffalature")

if scaffalature:
    df_scaffalature = pd.DataFrame(scaffalature)
    st.dataframe(df_scaffalature)
else:
    st.error("Errore nel recuperare le scaffalature dal database.")

# Gestione dei lotti
st.subheader("Gestione Lotti")
lotti = select_recordsSQL(session, "Lotti")

if lotti:
    df_lotti = pd.DataFrame(lotti)
    st.dataframe(df_lotti)
    
    # Opzioni per modificare stato del lotto
    lotto_id = st.selectbox("Seleziona un Lotto", df_lotti['ID_Lotto'])
    nuovo_stato = st.selectbox("Nuovo Stato", ['Disponibile', 'In transito', 'Prenotato'])
    
    if st.button("Aggiorna Stato Lotto"):
        # Update the lotto state
        try:
            sql_update = f"""
                UPDATE Lotti
                SET Stato = :stato
                WHERE ID_Lotto = :lotto_id
            """
            session.execute(text(sql_update), {"stato": nuovo_stato, "lotto_id": lotto_id})
            session.commit()
            st.success(f"Stato del lotto {lotto_id} aggiornato con successo!")
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento dello stato del lotto: {e}")
else:
    st.error("Errore nel recuperare i lotti dal database.")
