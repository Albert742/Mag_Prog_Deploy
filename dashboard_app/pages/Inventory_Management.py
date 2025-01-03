import streamlit as st
import pandas as pd
import time
from sqlalchemy import text
from utils.MagDBcontroller import connessione, select_recordsSQL, update_recordSQL
from streamlit_extras.switch_page_button import switch_page

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima.")
    switch_page("Login")
    st.stop()

# Connessione al database
session = connessione()

# Funzione per visualizzare una tabella con stile
def display_table(title, data, id_mappings=None, index_column=None):
    st.subheader(title)
    if data:
        df = pd.DataFrame(data)
        if index_column:
            df.set_index(index_column, inplace=True)
        if id_mappings:
            for column, mapping in id_mappings.items():
                df = map_ids_to_names(df, column, mapping['table'], mapping['id_column'], mapping['name_column'])
        # Rinomina le colonne per renderle più leggibili
        df.columns = [col.replace('_', ' ').title() for col in df.columns]
        st.dataframe(df)
    else:
        st.error(f"Errore nel recuperare i dati per {title} dal database.")

def map_ids_to_names(df, column, table, id_column, name_column):
    session = connessione()
    records = select_recordsSQL(session, table, f"{id_column}, {name_column}")
    id_to_name = {record[id_column]: record[name_column] for record in records}
    df[column + "_nome"] = df[column].map(id_to_name)
    # Posiziona la colonna del nome subito dopo la colonna dell'ID
    cols = df.columns.tolist()
    idx = cols.index(column)
    cols.insert(idx + 1, cols.pop(cols.index(column + "_nome")))
    df = df[cols]
    return df

# Funzione per aggiornare lo stato di un lotto
def update_stato_lotto(lotto_id, nuovo_stato):
    update_data = {"Stato": nuovo_stato}
    condizione = "ID_Lotto = :lotto_id"
    args = {"lotto_id": lotto_id}
    rows_updated = update_recordSQL(session, "Lotti", update_data, condizione, args)
    return rows_updated

# Funzione per aggiornare un prodotto
def update_prodotto(prodotto_id, nome, produttore, tipo, quantita_confezione, unita_misura):
    update_data = {
        "Nome": nome,
        "Produttore": produttore,
        "Tipo": tipo,
        "QuantitàConfezione": quantita_confezione,
        "UnitaMisura": unita_misura
    }
    condizione = "ID_Prodotto = :prodotto_id"
    args = {"prodotto_id": prodotto_id}
    rows_updated = update_recordSQL(session, "Prodotti", update_data, condizione, args)
    return rows_updated

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

# Visualizza prodotti
prodotti = select_recordsSQL(session, "Prodotti")
display_table("Prodotti", prodotti, id_mappings={
    'ID_Fornitore': {'table': 'Fornitori', 'id_column': 'ID_Fornitore', 'name_column': 'Nome'}
}, index_column='ID_Prodotto')

# Bottone per mostrare il form di aggiornamento prodotto
if "show_form_update_prodotto" not in st.session_state:
    st.session_state.show_form_update_prodotto = False

if not st.session_state.show_form_update_prodotto:
    if st.button("Aggiorna Prodotto"):
        st.session_state.show_form_update_prodotto = True
        st.rerun()

# Sezione per aggiornare un prodotto
if st.session_state.get("show_form_update_prodotto", False):
    st.write("### Aggiorna Prodotto")
    if prodotti:
        df_prodotti = pd.DataFrame(prodotti)
        
        with st.form(key='select_prodotto_form'):
            prodotto_id = st.selectbox("Seleziona un Prodotto", df_prodotti['ID_Prodotto'])
            select_button = st.form_submit_button(label="Seleziona")
            
        if select_button:
            selected_prodotto = df_prodotti[df_prodotti['ID_Prodotto'] == prodotto_id].iloc[0]
            st.session_state.selected_prodotto = selected_prodotto.to_dict()
            
        if "selected_prodotto" in st.session_state:
            selected_prodotto = st.session_state.selected_prodotto
            with st.form(key='prodotto_form_update'):
                nome = st.text_input("Nome", value=selected_prodotto['Nome'])
                produttore = st.text_input("Produttore", value=selected_prodotto['Produttore'])
                tipo = st.selectbox("Tipo", ['Alimentare', 'Farmaceutico'], index=['Alimentare', 'Farmaceutico'].index(selected_prodotto['Tipo']))
                quantita_confezione = st.number_input("Quantità Confezione", value=float(selected_prodotto['QuantitàConfezione']))
                unita_misura = st.selectbox("Unità di Misura", ['kg', 'g', 'l', 'ml', 'compresse', 'capsule'], index=['kg', 'g', 'l', 'ml', 'compresse', 'capsule'].index(selected_prodotto['UnitaMisura']))
                
                # Crea il bottone per inviare il form
                submit_button = st.form_submit_button(label="Aggiorna Prodotto")
                cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                # Aggiorna prodotto
                try:
                    rows_updated = update_prodotto(prodotto_id, nome, produttore, tipo, quantita_confezione, unita_misura)
                    if rows_updated:
                        st.success(f"Prodotto {prodotto_id} aggiornato con successo!")
                        time.sleep(2)
                        st.session_state.show_form_update_prodotto = False
                        st.rerun()
                    else:
                        st.error("Errore durante l'aggiornamento del prodotto.")
                except Exception as e:
                    st.error(f"Errore durante l'aggiornamento del prodotto: {e}")
            elif cancel_button:
                st.session_state.show_form_update_prodotto = False
                st.rerun()

# Visualizza lotti
lotti = select_recordsSQL(session, "Lotti")
display_table("Lotti", lotti, id_mappings={
    'ID_Prodotto': {'table': 'Prodotti', 'id_column': 'ID_Prodotto', 'name_column': 'Nome'},
    'ID_Fornitore': {'table': 'Fornitori', 'id_column': 'ID_Fornitore', 'name_column': 'Nome'},
    'ID_Zona': {'table': 'Zone', 'id_column': 'ID_Zona', 'name_column': 'Nome'},
    'ID_Scaffalatura': {'table': 'Scaffalature', 'id_column': 'ID_Scaffalatura', 'name_column': 'Nome'}
}, index_column='ID_Lotto')

# Bottone per mostrare il form di aggiornamento stato lotti
if "show_form_update_lotti" not in st.session_state:
    st.session_state.show_form_update_lotti = False

if not st.session_state.show_form_update_lotti:
    if st.button("Aggiorna Stato Lotti"):
        st.session_state.show_form_update_lotti = True
        st.rerun()

# Sezione per aggiornare lo stato dei lotti
if st.session_state.get("show_form_update_lotti", False):
    st.write("### Aggiorna Stato Lotto")
    if lotti:
        df_lotti = pd.DataFrame(lotti)
        
        with st.form(key='lotto_form_update'):
            lotto_id = st.selectbox("Seleziona un Lotto", df_lotti['ID_Lotto'])
            nuovo_stato = st.selectbox("Nuovo Stato", ['Disponibile', 'Esaurito', 'Prenotato'])
            
            # Crea il bottone per inviare il form
            submit_button = st.form_submit_button(label="Aggiorna Stato Lotto")
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            # Aggiorna stato del lotto
            try:
                rows_updated = update_stato_lotto(lotto_id, nuovo_stato)
                if rows_updated:
                    st.success(f"Stato del lotto {lotto_id} aggiornato con successo!")
                    time.sleep(2)
                    st.session_state.show_form_update_lotti = False
                    st.rerun()
                else:
                    st.error("Errore durante l'aggiornamento dello stato del lotto.")
            except Exception as e:
                st.error(f"Errore durante l'aggiornamento dello stato del lotto: {e}")
        elif cancel_button:
            st.session_state.show_form_update_lotti = False
            st.rerun()