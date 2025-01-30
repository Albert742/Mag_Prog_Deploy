import streamlit as st
import pandas as pd
import time
import datetime
from sqlalchemy import text
from utils.MagDBcontroller import connessione, select_recordsSQL, update_recordSQL, add_recordSQL, delete_recordSQL
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

# Verifica autenticazione
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Accesso non autorizzato. Effettua il login prima o accedi con un account autorizzato.")
    time.sleep(2)
    switch_page("Login")
    st.stop()

# Connessione al database
session = connessione()

# Titolo della pagina
st.title("Gestione Inventario")

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

# Funzione per aggiungere un prodotto
def add_prodotto(nome, produttore, tipo, quantita_confezione, unita_misura, id_fornitore):
    new_prodotto = {
        "Nome": nome,
        "Produttore": produttore,
        "Tipo": tipo,
        "QuantitàConfezione": quantita_confezione,
        "UnitaMisura": unita_misura,
        "ID_Fornitore": id_fornitore
    }
    success = add_recordSQL(session, "Prodotti", new_prodotto)
    return success

# Funzione per eliminare un prodotto
def delete_prodotto(prodotto_id):
    condizione = "ID_Prodotto = :prodotto_id"
    args = {"prodotto_id": prodotto_id}
    rows_deleted = delete_recordSQL(session, "Prodotti", condizione, args)
    return rows_deleted

# Funzione per aggiungere un lotto
def add_lotto(id_prodotto, id_fornitore, id_zona, id_scaffalatura, lotto, scadenza, quantita_prodotto, peso_lotto, prezzo_acquisto, valore_lotto, data_prenotazione, data_ricevimento, stato):
    new_lotto = {
        "ID_Prodotto": id_prodotto,
        "ID_Fornitore": id_fornitore,
        "ID_Zona": id_zona,
        "ID_Scaffalatura": id_scaffalatura,
        "Lotto": lotto,
        "Scadenza": scadenza,
        "QuantitàProdotto": quantita_prodotto,
        "PesoLotto": peso_lotto,
        "PrezzoAcquisto": prezzo_acquisto,
        "ValoreLotto": valore_lotto,
        "DataPrenotazione": data_prenotazione,
        "DataRicevimento": data_ricevimento,
        "Stato": stato
    }
    success = add_recordSQL(session, "Lotti", new_lotto)
    return success

# Funzione per eliminare un lotto
def delete_lotto(lotto_id):
    condizione = "ID_Lotto = :lotto_id"
    args = {"lotto_id": lotto_id}
    rows_deleted = delete_recordSQL(session, "Lotti", condizione, args)
    return rows_deleted

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
                with stylable_container(
                        "red",
                        css_styles="""
                        button:hover {
                        background-color: #d9534f;
                        color: #ffffff;
                        border-color: #d43f3a;
                    }""",
                ):
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

# Bottone per mostrare il form di aggiunta prodotto
if "show_form_add_prodotto" not in st.session_state:
    st.session_state.show_form_add_prodotto = False

if not st.session_state.show_form_add_prodotto:
    if st.button("Aggiungi Prodotto"):
        st.session_state.show_form_add_prodotto = True
        st.rerun()

# Sezione per aggiungere un prodotto
if st.session_state.get("show_form_add_prodotto", False):
    st.write("### Aggiungi Prodotto")
    with st.form(key='prodotto_form_add'):
        nome = st.text_input("Nome")
        produttore = st.text_input("Produttore")
        tipo = st.selectbox("Tipo", ['Alimentare', 'Farmaceutico'])
        quantita_confezione = st.number_input("Quantità Confezione")
        unita_misura = st.selectbox("Unità di Misura", ['kg', 'g', 'l', 'ml', 'compresse', 'capsule'])
        id_fornitore = st.selectbox("Fornitore", [f['ID_Fornitore'] for f in prodotti])

        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Aggiungi Prodotto")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if nome and produttore and tipo and quantita_confezione and unita_misura and id_fornitore:
                if add_prodotto(nome, produttore, tipo, quantita_confezione, unita_misura, id_fornitore):
                    st.success("Prodotto aggiunto con successo!")
                    time.sleep(2)
                    st.session_state.show_form_add_prodotto = False
                    st.rerun()
                else:
                    st.error("Errore durante l'aggiunta del prodotto.")
            else:
                st.error("Tutti i campi sono obbligatori.")
        elif cancel_button:
            st.session_state.show_form_add_prodotto = False
            st.rerun()

# Bottone per mostrare il form di eliminazione prodotto
if "show_form_delete_prodotto" not in st.session_state:
    st.session_state.show_form_delete_prodotto = False

if not st.session_state.show_form_delete_prodotto:
    if st.button("Elimina Prodotto"):
        st.session_state.show_form_delete_prodotto = True
        st.rerun()

# Sezione per eliminare un prodotto
if st.session_state.get("show_form_delete_prodotto", False):
    st.write("### Elimina Prodotto")
    with st.form(key='prodotto_form_delete'):
        prodotto_id = st.selectbox("Seleziona un Prodotto", [p['ID_Prodotto'] for p in prodotti])

        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Elimina Prodotto")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if prodotto_id:
                if delete_prodotto(prodotto_id):
                    st.success("Prodotto eliminato con successo!")
                    time.sleep(2)
                    st.session_state.show_form_delete_prodotto = False
                    st.rerun()
                else:
                    st.error("Errore durante l'eliminazione del prodotto.")
            else:
                st.error("Seleziona un prodotto.")
        elif cancel_button:
            st.session_state.show_form_delete_prodotto = False
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
        
        with st.form(key='select_lotto_form'):
            lotto_id = st.selectbox("Seleziona un Lotto", df_lotti['ID_Lotto'])
            select_button = st.form_submit_button(label="Seleziona")
            
        if select_button:
            selected_lotto = df_lotti[df_lotti['ID_Lotto'] == lotto_id].iloc[0]
            st.session_state.selected_lotto = selected_lotto.to_dict()
            
        if "selected_lotto" in st.session_state:
            selected_lotto = st.session_state.selected_lotto
            with st.form(key='lotto_form_update'):
                nuovo_stato = st.selectbox("Nuovo Stato", ['Disponibile', 'Esaurito', 'Prenotato'], index=['Disponibile', 'Esaurito', 'Prenotato'].index(selected_lotto['Stato']))
                
                # Crea il bottone per inviare il form
                submit_button = st.form_submit_button(label="Aggiorna Stato Lotto")
                with stylable_container(
                        "red",
                        css_styles="""
                        button:hover {
                        background-color: #d9534f;
                        color: #ffffff;
                        border-color: #d43f3a;
                    }""",
                ):
                    cancel_button = st.form_submit_button(label="Annulla")

            if submit_button:
                # Aggiorna stato del lotto
                try:
                    update_data = {"Stato": nuovo_stato}
                    if selected_lotto['Stato'] == 'Prenotato' and nuovo_stato == 'Disponibile':
                        update_data["DataRicevimento"] = datetime.datetime.now()

                    rows_updated = update_recordSQL(session, "Lotti", update_data, "ID_Lotto = :lotto_id", {"lotto_id": lotto_id})
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

# Bottone per mostrare il form di aggiunta lotto
if "show_form_add_lotto" not in st.session_state:
    st.session_state.show_form_add_lotto = False

if not st.session_state.show_form_add_lotto:
    if st.button("Aggiungi Lotto"):
        st.session_state.show_form_add_lotto = True
        st.rerun()

# Sezione per aggiungere un lotto
if st.session_state.get("show_form_add_lotto", False):
    st.write("### Aggiungi Lotto")
    with st.form(key='lotto_form_add'):
        id_prodotto = st.selectbox("Prodotto", [p['ID_Prodotto'] for p in prodotti])
        id_fornitore = st.selectbox("Fornitore", [f['ID_Fornitore'] for f in prodotti])
        id_zona = st.selectbox("Zona", [z['ID_Zona'] for z in lotti])
        id_scaffalatura = st.selectbox("Scaffalatura", [s['ID_Scaffalatura'] for s in lotti])
        lotto = st.text_input("Lotto")
        scadenza = st.date_input("Scadenza")
        quantita_prodotto = st.number_input("Quantità Prodotto")
        peso_lotto = st.number_input("Peso Lotto")
        prezzo_acquisto = st.number_input("Prezzo Acquisto")
        valore_lotto = st.number_input("Valore Lotto")
        data_prenotazione = st.date_input("Data Prenotazione")
        data_ricevimento = st.date_input("Data Ricevimento")
        stato = st.selectbox("Stato", ['Disponibile', 'Esaurito', 'Prenotato'])

        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Aggiungi Lotto")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if id_prodotto and id_fornitore and id_zona and id_scaffalatura and lotto and scadenza and quantita_prodotto and peso_lotto and prezzo_acquisto and valore_lotto and data_prenotazione and data_ricevimento and stato:
                if add_lotto(id_prodotto, id_fornitore, id_zona, id_scaffalatura, lotto, scadenza, quantita_prodotto, peso_lotto, prezzo_acquisto, valore_lotto, data_prenotazione, data_ricevimento, stato):
                    st.success("Lotto aggiunto con successo!")
                    time.sleep(2)
                    st.session_state.show_form_add_lotto = False
                    st.rerun()
                else:
                    st.error("Errore durante l'aggiunta del lotto.")
            else:
                st.error("Tutti i campi sono obbligatori.")
        elif cancel_button:
            st.session_state.show_form_add_lotto = False
            st.rerun()

# Bottone per mostrare il form di eliminazione lotto
if "show_form_delete_lotto" not in st.session_state:
    st.session_state.show_form_delete_lotto = False

if not st.session_state.show_form_delete_lotto:
    if st.button("Elimina Lotto"):
        st.session_state.show_form_delete_lotto = True
        st.rerun()

# Sezione per eliminare un lotto
if st.session_state.get("show_form_delete_lotto", False):
    st.write("### Elimina Lotto")
    with st.form(key='lotto_form_delete'):
        lotto_id = st.selectbox("Seleziona un Lotto", [l['ID_Lotto'] for l in lotti])

        # Crea il bottone per inviare il form
        submit_button = st.form_submit_button(label="Elimina Lotto")
        with stylable_container(
                "red",
                css_styles="""
                button:hover {
                background-color: #d9534f;
                color: #ffffff;
                border-color: #d43f3a;
            }""",
        ):
            cancel_button = st.form_submit_button(label="Annulla")

        if submit_button:
            if lotto_id:
                if delete_lotto(lotto_id):
                    st.success("Lotto eliminato con successo!")
                    time.sleep(2)
                    st.session_state.show_form_delete_lotto = False
                    st.rerun()
                else:
                    st.error("Errore durante l'eliminazione del lotto.")
            else:
                st.error("Seleziona un lotto.")
        elif cancel_button:
            st.session_state.show_form_delete_lotto = False
            st.rerun()