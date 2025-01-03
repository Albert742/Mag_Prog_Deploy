import streamlit as st
import pandas as pd
import time
import plotly.express as px
from utils.MagDBcontroller import connessione, select_recordsSQL
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

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

# Panoramica Prodotti
st.write("## Panoramica Prodotti")

# Visualizza il numero totale di prodotti
prodotti = select_recordsSQL(session, "Prodotti")
if prodotti:
    df_prodotti = pd.DataFrame(prodotti)
    st.write("### Numero Totale di Prodotti")
    st.write(len(df_prodotti))

    # Visualizza un grafico a barre dei prodotti per tipo
    df_prodotti_tipo = df_prodotti['Tipo'].value_counts().reset_index()
    df_prodotti_tipo.columns = ['Tipo', 'Quantità']
    display_bar_chart("Prodotti per Tipo", df_prodotti_tipo, 'Tipo', 'Quantità', color='Tipo')

# Panoramica Lotti
st.write("## Panoramica Lotti")

# Visualizza il numero totale di lotti
lotti = select_recordsSQL(session, "Lotti")
if lotti:
    df_lotti = pd.DataFrame(lotti)
    st.write("### Numero Totale di Lotti")
    st.write(len(df_lotti))

    # Visualizza un grafico a torta dello stato dei lotti
    df_lotti_stato = df_lotti['Stato'].value_counts().reset_index()
    df_lotti_stato.columns = ['Stato', 'Count']
    display_pie_chart("Stato dei Lotti", df_lotti_stato, 'Stato', 'Count')

    # Visualizza un grafico a linee del numero di lotti ricevuti nel tempo
    df_lotti['DataRicevimento'] = pd.to_datetime(df_lotti['DataRicevimento'])
    df_lotti_ricevuti = df_lotti.groupby(df_lotti['DataRicevimento'].dt.to_period('M')).size().reset_index(name='Count')
    df_lotti_ricevuti['DataRicevimento'] = df_lotti_ricevuti['DataRicevimento'].dt.to_timestamp()
    display_line_chart("Lotti Ricevuti nel Tempo", df_lotti_ricevuti, 'DataRicevimento', 'Count')

    # Visualizza un grafico a barre dei lotti per prodotto
    df_lotti_prodotto = df_lotti['ID_Prodotto'].value_counts().reset_index()
    df_lotti_prodotto.columns = ['ID_Prodotto', 'Quantità']
    df_lotti_prodotto = df_lotti_prodotto.merge(df_prodotti[['ID_Prodotto', 'Nome']], on='ID_Prodotto')
    display_bar_chart("Lotti per Prodotto", df_lotti_prodotto, 'Nome', 'Quantità')

# Panoramica Generale
st.write("## Panoramica Generale")

# Visualizza un grafico a linee della temperatura media nel tempo
sensori = select_recordsSQL(session, "LettureSensori", colonne="DataLettura, Valore", condizione="Tipo = 'Temperatura'")
if sensori:
    df_sensori = pd.DataFrame(sensori)
    df_sensori['DataLettura'] = pd.to_datetime(df_sensori['DataLettura'])
    df_sensori_media = df_sensori.groupby(df_sensori['DataLettura'].dt.to_period('M')).mean().reset_index()
    df_sensori_media['DataLettura'] = df_sensori_media['DataLettura'].dt.to_timestamp()
    display_line_chart("Temperatura Media nel Tempo", df_sensori_media, 'DataLettura', 'Valore')

# Visualizza un grafico a barre degli ordini per stato
ordini = select_recordsSQL(session, "Ordini")
if ordini:
    df_ordini = pd.DataFrame(ordini)
    df_ordini_stato = df_ordini['Stato'].value_counts().reset_index()
    df_ordini_stato.columns = ['Stato', 'Quantità']
    display_bar_chart("Ordini per Stato", df_ordini_stato, 'Stato', 'Quantità')

# Visualizza un grafico a barre delle manutenzioni per tipo
manutenzioni = select_recordsSQL(session, "ManutenzioneRobot")
if manutenzioni:
    df_manutenzioni = pd.DataFrame(manutenzioni)
    df_manutenzioni_tipo = df_manutenzioni['Tipo'].value_counts().reset_index()
    df_manutenzioni_tipo.columns = ['Tipo', 'Quantità']
    display_bar_chart("Manutenzioni per Tipo", df_manutenzioni_tipo, 'Tipo', 'Quantità')