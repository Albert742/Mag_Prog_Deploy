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

# Visualizza la temperatura più recente per zona
letturasensori = select_recordsSQL(session, "LettureSensori", colonne="ID_Sensore, DataLettura, Valore", condizione="Tipo = 'Temperatura'", ordina_per="DataLettura DESC")
sensori = select_recordsSQL(session, "Sensori", colonne="ID_Sensore, ID_Zona")
zone = select_recordsSQL(session, "Zone", colonne="ID_Zona, Nome")

if letturasensori and sensori and zone:
    st.write("### Temperatura più recente per Zona")
    df_letturasensori = pd.DataFrame(letturasensori)
    df_sensori = pd.DataFrame(sensori)
    df_zone = pd.DataFrame(zone)

    df_merged = df_letturasensori.merge(df_sensori, on="ID_Sensore").merge(df_zone, left_on="ID_Zona", right_on="ID_Zona").drop_duplicates(subset=['Nome'])
    df_merged = df_merged.sort_values(by='Nome')  # Ordina per nome della zona

    for _, row in df_merged.iterrows():
        st.metric(label=f"Zona {row['Nome']} - Sensore {row['ID_Sensore']}", value=f"{row['Valore']} °C", delta=None)
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

st.rerun()