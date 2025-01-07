import streamlit as st
import pandas as pd
import time
import plotly.express as px
from utils.MagDBcontroller import connessione, select_recordsSQL
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

# Connessione al database
session = connessione()

# Funzione per visualizzare un grafico a barre
def display_bar_chart(title, data, x, y, color=None):
    fig = px.bar(data, x=x, y=y, color=color, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig)

# Funzione per visualizzare un grafico a torta
def display_pie_chart(title, data, names, values):
    fig = px.pie(data, names=names, values=values, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig)

# Funzione per visualizzare un grafico a linee
def display_line_chart(title, data, x, y, color=None):
    fig = px.line(data, x=x, y=y, color=color, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig)

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
    st.sidebar.page_link('pages/Test_Magazzino.py', label='Test Funzionalità')
elif ruolo == "Tecnico":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
    st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
elif ruolo == "Operatore":
    st.sidebar.page_link('Home.py', label='Home')
    st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')

st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")

# Panoramica Generale
st.write("## Panoramica Generale")

# Bottone per aggiornare i dati
if st.button("Aggiorna Dati"):
    st.rerun()

# Visualizza un grafico a linee della temperatura media nel tempo
sensori = select_recordsSQL(session, "LettureSensori", colonne="DataLettura, Valore", condizione="Tipo = 'Temperatura'")
if sensori:
    st.write("### Dati Sensori")
    st.write(sensori)  # Stampa i dati dei sensori per debug
    df_sensori = pd.DataFrame(sensori)
    df_sensori['DataLettura'] = pd.to_datetime(df_sensori['DataLettura'])
    df_sensori['Periodo'] = df_sensori['DataLettura'].dt.to_period('M')
    df_sensori_media = df_sensori.groupby('Periodo').mean().reset_index()
    df_sensori_media['DataLettura'] = df_sensori_media['Periodo'].dt.to_timestamp()
    df_sensori_media.drop(columns=['Periodo'], inplace=True)
    display_line_chart("Temperatura Media nel Tempo", df_sensori_media, 'DataLettura', 'Valore')
else:
    st.write("Nessun dato trovato per i sensori di temperatura.")

# Visualizza un grafico a barre degli ordini per stato
ordini = select_recordsSQL(session, "Ordini")
if ordini:
    st.write("### Dati Ordini")
    st.write(ordini)  # Stampa i dati degli ordini per debug
    df_ordini = pd.DataFrame(ordini)
    df_ordini_stato = df_ordini['Stato'].value_counts().reset_index()
    df_ordini_stato.columns = ['Stato', 'Quantità']
    display_bar_chart("Ordini per Stato", df_ordini_stato, 'Stato', 'Quantità')
else:
    st.write("Nessun dato trovato per gli ordini.")

# Visualizza un grafico a barre delle manutenzioni per tipo
manutenzioni = select_recordsSQL(session, "ManutenzioneRobot")
if manutenzioni:
    st.write("### Dati Manutenzioni")
    st.write(manutenzioni)  # Stampa i dati delle manutenzioni per debug
    df_manutenzioni = pd.DataFrame(manutenzioni)
    df_manutenzioni_tipo = df_manutenzioni['Tipo'].value_counts().reset_index()
    df_manutenzioni_tipo.columns = ['Tipo', 'Quantità']
    display_bar_chart("Manutenzioni per Tipo", df_manutenzioni_tipo, 'Tipo', 'Quantità')
else:
    st.write("Nessun dato trovato per le manutenzioni.")