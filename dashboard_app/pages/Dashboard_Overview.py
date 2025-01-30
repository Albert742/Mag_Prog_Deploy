import streamlit as st
import pandas as pd
import time
import plotly.express as px
from utils.MagDBcontroller import connessione, select_recordsSQL
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

# Titolo della pagina
st.title("Dashboard Panoramica")

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
    st.sidebar.page_link('pages/Internal_Logistic_Managment.py', label='Gestione Logistica Interna')
    st.sidebar.page_link('pages/External_Logistic_Managment.py', label='Gestione Logistica Esterna')
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

# Funzione per visualizzare un grafico a barre
def display_bar_chart(title, data, x, y, color=None):
    fig = px.bar(data, x=x, y=y, color=color, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig)

# Funzione per visualizzare un grafico a barre con colori diversi per barra
def display_colored_bar_chart(title, data, x, y, color):
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

# Funzione per visualizzare un grafico a linee della temperatura media per zona
def display_avg_temp_line_chart(title, data, x, y, color):
    fig = px.line(data, x=x, y=y, color=color, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig)

# Funzione per visualizzare un grafico a dispersione
def display_scatter_chart(title, data, x, y, color=None):
    fig = px.scatter(data, x=x, y=y, color=color, title=title, color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig)

# Funzione per visualizzare un grafico a torta delle zone per tipo
def display_zone_pie_chart(title, data, names, values):
    fig = px.pie(data, names=names, values=values, title=title, color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig)

placeholder = st.empty()

with placeholder.container():
    
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
        
        # Visualizza un grafico a dispersione dei lotti per zona
        lotti = select_recordsSQL(session, "Lotti", colonne="ID_Lotto, ID_Zona, QuantitàProdotto")
        zone = select_recordsSQL(session, "Zone", colonne="ID_Zona, Nome")
        
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

    if lotti and zone:
        st.write("### Lotti per Zona")
        df_lotti = pd.DataFrame(lotti)
        df_zone = pd.DataFrame(zone)

        df_merged = df_lotti.merge(df_zone, on="ID_Zona")
        display_scatter_chart("Lotti per Zona", df_merged, 'Nome', 'QuantitàProdotto', 'Nome')
    else:
            st.write("Nessun dato trovato per i lotti.")

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

    # Visualizza un grafico a linee della temperatura media per zona
    letturasensori = select_recordsSQL(session, "LettureSensori", colonne="ID_Sensore, DataLettura, Valore", condizione="Tipo = 'Temperatura'")
    sensori = select_recordsSQL(session, "Sensori", colonne="ID_Sensore, ID_Zona")
    zone = select_recordsSQL(session, "Zone", colonne="ID_Zona, Nome")

    if letturasensori and sensori and zone:
        st.write("### Temperatura Media per Zona")
        df_letturasensori = pd.DataFrame(letturasensori)
        df_sensori = pd.DataFrame(sensori)
        df_zone = pd.DataFrame(zone)

        df_merged = df_letturasensori.merge(df_sensori, on="ID_Sensore").merge(df_zone, left_on="ID_Zona", right_on="ID_Zona")
        df_avg_temp = df_merged.groupby(['Nome', 'DataLettura'])['Valore'].mean().reset_index()
        df_avg_temp.columns = ['Zona', 'DataLettura', 'Temperatura Media']

        display_avg_temp_line_chart("Temperatura Media per Zona", df_avg_temp, 'DataLettura', 'Temperatura Media', 'Zona')
    else:
        st.write("Nessun dato trovato per i sensori di temperatura.")

    # Visualizza un grafico a linee delle letture dei sensori di umidità
    letturasensori = select_recordsSQL(session, "LettureSensori", colonne="ID_Sensore, DataLettura, Valore", condizione="Tipo = 'Umidità'")
    sensori = select_recordsSQL(session, "Sensori", colonne="ID_Sensore, ID_Zona")
    zone = select_recordsSQL(session, "Zone", colonne="ID_Zona, Nome")

    if letturasensori and sensori and zone:
        st.write("### Letture Sensori di Umidità")
        df_letturasensori = pd.DataFrame(letturasensori)
        df_sensori = pd.DataFrame(sensori)
        df_zone = pd.DataFrame(zone)

        df_merged = df_letturasensori.merge(df_sensori, on="ID_Sensore").merge(df_zone, left_on="ID_Zona", right_on="ID_Zona")
        df_merged = df_merged.sort_values(by='DataLettura')

        display_line_chart("Letture Sensori di Umidità", df_merged, 'DataLettura', 'Valore', 'Nome')
    else:
        st.write("Nessun dato trovato per i sensori di umidità.")

    # Visualizza un grafico a barre degli ordini per stato
    ordini = select_recordsSQL(session, "Ordini")
    if ordini:
        df_ordini = pd.DataFrame(ordini)
        df_ordini_stato = df_ordini['Stato'].value_counts().reset_index()
        df_ordini_stato.columns = ['Stato', 'Quantità']
        display_colored_bar_chart("Ordini per Stato", df_ordini_stato, 'Stato', 'Quantità', 'Stato')
    else:
        st.write("Nessun dato trovato per gli ordini.")

    # Visualizza un grafico a barre delle manutenzioni per tipo
    manutenzioni = select_recordsSQL(session, "ManutenzioneRobot")
    if manutenzioni:
        df_manutenzioni = pd.DataFrame(manutenzioni)
        df_manutenzioni_tipo = df_manutenzioni['Tipo'].value_counts().reset_index()
        df_manutenzioni_tipo.columns = ['Tipo', 'Quantità']
        display_colored_bar_chart("Manutenzioni per Tipo", df_manutenzioni_tipo, 'Tipo', 'Quantità', 'Tipo')
    else:
        st.write("Nessun dato trovato per le manutenzioni.")
    
    time.sleep(10)    
    st.rerun()

