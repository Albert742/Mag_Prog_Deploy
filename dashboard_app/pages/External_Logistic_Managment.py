import pandas as pd
import streamlit as st
import time
from utils.MagDBcontroller import connessione, select_recordsSQL, add_recordSQL, update_recordSQL, delete_recordSQL
from utils.MagUtils import create_employee_id, log_logout
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
st.title("Gestione Logistica Esterna")

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

# Visualizza clienti
clienti = select_recordsSQL(session, "Clienti")
if clienti:
    df_clienti = pd.DataFrame(clienti)
    st.write("### Clienti")
    st.dataframe(df_clienti)
else:
    st.error("Errore nel recuperare i dati dei clienti dal database.")

# Bottone per mostrare il form di aggiunta cliente
if "show_form_add_cliente" not in st.session_state:
    st.session_state.show_form_add_cliente = False
if not st.session_state.show_form_add_cliente:
    if st.button("Aggiungi Cliente"):
        st.session_state.show_form_add_cliente = True
        st.rerun()

# Sezione per aggiungere un cliente
if st.session_state.get("show_form_add_cliente", False):
    st.write("### Aggiungi Cliente")
    with st.form(key='cliente_form_add'):
        nome = st.text_input("Nome")
        indirizzo = st.text_input("Indirizzo")
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")
        partita_iva = st.text_input("Partita IVA")

        submit_button = st.form_submit_button(label="Aggiungi Cliente")
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
        try:
            add_recordSQL(session, "Clienti", {
                "Nome": nome,
                "Indirizzo": indirizzo,
                "Telefono": telefono,
                "Email": email,
                "PartitaIVA": partita_iva
            })
            st.success("Cliente aggiunto con successo!")
            time.sleep(2)
            st.session_state.show_form_add_cliente = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta del cliente: {e}")
    elif cancel_button:
        st.session_state.show_form_add_cliente = False
        st.rerun()

# Bottone per mostrare il form di aggiornamento cliente
if "show_form_update_cliente" not in st.session_state:
    st.session_state.show_form_update_cliente = False
if not st.session_state.show_form_update_cliente:
    if st.button("Aggiorna Cliente"):
        st.session_state.show_form_update_cliente = True
        st.rerun()

# Sezione per aggiornare un cliente
if st.session_state.get("show_form_update_cliente", False):
    st.write("### Aggiorna Cliente")
    with st.form(key='cliente_form_update'):
        id_cliente = st.number_input("ID Cliente", min_value=1)
        nome = st.text_input("Nome")
        indirizzo = st.text_input("Indirizzo")
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")
        partita_iva = st.text_input("Partita IVA")

        submit_button = st.form_submit_button(label="Aggiorna Cliente")
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
        try:
            update_recordSQL(session, "Clienti", {
                "Nome": nome,
                "Indirizzo": indirizzo,
                "Telefono": telefono,
                "Email": email,
                "PartitaIVA": partita_iva
            }, "ID_Cliente = :id_cliente", {"id_cliente": id_cliente})
            st.success("Cliente aggiornato con successo!")
            time.sleep(2)
            st.session_state.show_form_update_cliente = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento del cliente: {e}")
    elif cancel_button:
        st.session_state.show_form_update_cliente = False
        st.rerun()

# Bottone per mostrare il form di eliminazione cliente
if "show_form_delete_cliente" not in st.session_state:
    st.session_state.show_form_delete_cliente = False
if not st.session_state.show_form_delete_cliente:
    if st.button("Elimina Cliente"):
        st.session_state.show_form_delete_cliente = True
        st.rerun()

# Sezione per eliminare un cliente
if st.session_state.get("show_form_delete_cliente", False):
    st.write("### Elimina Cliente")
    with st.form(key='cliente_form_delete'):
        id_cliente = st.number_input("ID Cliente", min_value=1)

        submit_button = st.form_submit_button(label="Elimina Cliente")
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
        try:
            delete_recordSQL(session, "Clienti", "ID_Cliente = :id_cliente", {"id_cliente": id_cliente})
            st.success("Cliente eliminato con successo!")
            time.sleep(2)
            st.session_state.show_form_delete_cliente = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'eliminazione del cliente: {e}")
    elif cancel_button:
        st.session_state.show_form_delete_cliente = False
        st.rerun()

# Visualizza fornitori
fornitori = select_recordsSQL(session, "Fornitori")
if fornitori:
    df_fornitori = pd.DataFrame(fornitori)
    st.write("### Fornitori")
    st.dataframe(df_fornitori)
else:
    st.error("Errore nel recuperare i dati dei fornitori dal database.")

# Bottone per mostrare il form di aggiunta fornitore
if "show_form_add_fornitore" not in st.session_state:
    st.session_state.show_form_add_fornitore = False
if not st.session_state.show_form_add_fornitore:
    if st.button("Aggiungi Fornitore"):
        st.session_state.show_form_add_fornitore = True
        st.rerun()

# Sezione per aggiungere un fornitore
if st.session_state.get("show_form_add_fornitore", False):
    st.write("### Aggiungi Fornitore")
    with st.form(key='fornitore_form_add'):
        nome = st.text_input("Nome")
        indirizzo = st.text_input("Indirizzo")
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")
        partita_iva = st.text_input("Partita IVA")

        submit_button = st.form_submit_button(label="Aggiungi Fornitore")
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
        try:
            add_recordSQL(session, "Fornitori", {
                "Nome": nome,
                "Indirizzo": indirizzo,
                "Telefono": telefono,
                "Email": email,
                "PartitaIVA": partita_iva
            })
            st.success("Fornitore aggiunto con successo!")
            time.sleep(2)
            st.session_state.show_form_add_fornitore = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta del fornitore: {e}")
    elif cancel_button:
        st.session_state.show_form_add_fornitore = False
        st.rerun()

# Bottone per mostrare il form di aggiornamento fornitore
if "show_form_update_fornitore" not in st.session_state:
    st.session_state.show_form_update_fornitore = False
if not st.session_state.show_form_update_fornitore:
    if st.button("Aggiorna Fornitore"):
        st.session_state.show_form_update_fornitore = True
        st.rerun()

# Sezione per aggiornare un fornitore
if st.session_state.get("show_form_update_fornitore", False):
    st.write("### Aggiorna Fornitore")
    with st.form(key='fornitore_form_update'):
        id_fornitore = st.number_input("ID Fornitore", min_value=1)
        nome = st.text_input("Nome")
        indirizzo = st.text_input("Indirizzo")
        telefono = st.text_input("Telefono")
        email = st.text_input("Email")
        partita_iva = st.text_input("Partita IVA")
        
        submit_button = st.form_submit_button(label="Aggiorna Fornitore")
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
        try:
            update_recordSQL(session, "Fornitori", {
                "Nome": nome,
                "Indirizzo": indirizzo,
                "Telefono": telefono,
                "Email": email,
                "PartitaIVA": partita_iva
            }, "ID_Fornitore = :id_fornitore", {"id_fornitore": id_fornitore})
            st.success("Fornitore aggiornato con successo!")
            time.sleep(2)
            st.session_state.show_form_update_fornitore = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento del fornitore: {e}")
    elif cancel_button:
        st.session_state.show_form_update_fornitore = False
        st.rerun()

# Bottone per mostrare il form di eliminazione fornitore
if "show_form_delete_fornitore" not in st.session_state:
    st.session_state.show_form_delete_fornitore = False
if not st.session_state.show_form_delete_fornitore:
    if st.button("Elimina Fornitore"):
        st.session_state.show_form_delete_fornitore = True
        st.rerun()

# Sezione per eliminare un fornitore
if st.session_state.get("show_form_delete_fornitore", False):
    st.write("### Elimina Fornitore")
    with st.form(key='fornitore_form_delete'):
        id_fornitore = st.number_input("ID Fornitore", min_value=1)

        submit_button = st.form_submit_button(label="Elimina Fornitore")
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
        try:
            delete_recordSQL(session, "Fornitori", "ID_Fornitore = :id_fornitore", {"id_fornitore": id_fornitore})
            st.success("Fornitore eliminato con successo!")
            time.sleep(2)
            st.session_state.show_form_delete_fornitore = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'eliminazione del fornitore: {e}")
    elif cancel_button:
        st.session_state.show_form_delete_fornitore = False
        st.rerun()

# Visualizza ordini e dettagli ordini
ordini = select_recordsSQL(session, "Ordini")
dettagli_ordini = select_recordsSQL(session, "DettagliOrdini")
clienti = select_recordsSQL(session, "Clienti")
fornitori = select_recordsSQL(session, "Fornitori")

if ordini and dettagli_ordini:
    df_ordini = pd.DataFrame(ordini)
    df_dettagli_ordini = pd.DataFrame(dettagli_ordini)
    df_clienti = pd.DataFrame(clienti)
    df_fornitori = pd.DataFrame(fornitori)

    # Merge con i nomi dei clienti e fornitori
    df_ordini = df_ordini.merge(df_clienti[['ID_Cliente', 'Nome']], how='left', left_on='ID_Cliente', right_on='ID_Cliente', suffixes=('', '_Cliente'))
    df_ordini = df_ordini.merge(df_fornitori[['ID_Fornitore', 'Nome']], how='left', left_on='ID_Fornitore', right_on='ID_Fornitore', suffixes=('', '_Fornitore'))

    # Rinomina le colonne per chiarezza
    df_ordini.rename(columns={'Nome_Cliente': 'Nome Cliente', 'Nome_Fornitore': 'Nome Fornitore'}, inplace=True)

    # Unisci ordini e dettagli ordini
    df_ordini_completi = df_ordini.merge(df_dettagli_ordini, how='left', left_on='ID_Ordine', right_on='ID_Ordine')

    st.write("### Ordini e Dettagli Ordini")
    st.dataframe(df_ordini_completi)
else:
    st.error("Errore nel recuperare i dati degli ordini o dei dettagli ordini dal database.")
        
# Visualizza consegne
consegne = select_recordsSQL(session, "Consegne")
if consegne:
    df_consegne = pd.DataFrame(consegne)
    st.write("### Consegne")
    st.dataframe(df_consegne)
else:
    st.error("Errore nel recuperare i dati delle consegne dal database.")

# Bottone per mostrare il form di aggiornamento consegna
if "show_form_update_consegna" not in st.session_state:
    st.session_state.show_form_update_consegna = False
if not st.session_state.show_form_update_consegna:
    if st.button("Aggiorna Consegna"):
        st.session_state.show_form_update_consegna = True
        st.rerun()

# Sezione per aggiornare una consegna
if st.session_state.get("show_form_update_consegna", False):
    st.write("### Aggiorna Consegna")
    
    # Custom CSS for the cancel button
    st.markdown("""
        <style>
        .stButton > button:hover {
            background-color: red;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.form(key='consegna_form_update'):
        id_consegna = st.number_input("ID Consegna", min_value=1)
        id_ordine = st.number_input("ID Ordine", min_value=1)
        id_veicolo = st.number_input("ID Veicolo", min_value=1)
        data_consegna = st.date_input("Data Consegna")
        stato = st.selectbox("Stato", ['Pianificata', 'In corso', 'Completata', 'Annullata'])

        submit_button = st.form_submit_button(label="Aggiorna Consegna")
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
        try:
            update_recordSQL(session, "Consegne", {
                "ID_Ordine": id_ordine,
                "ID_Veicolo": id_veicolo,
                "DataConsegna": data_consegna,
                "Stato": stato
            }, "ID_Consegna = :id_consegna", {"id_consegna": id_consegna})
            st.success("Consegna aggiornata con successo!")
            time.sleep(2)
            st.session_state.show_form_update_consegna = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento della consegna: {e}")
    elif cancel_button:
        st.session_state.show_form_update_consegna = False
        st.rerun()

    if submit_button:
        try:
            update_recordSQL(session, "Consegne", {
                "ID_Ordine": id_ordine,
                "ID_Veicolo": id_veicolo,
                "DataConsegna": data_consegna,
                "Stato": stato
            }, "ID_Consegna = :id_consegna", {"id_consegna": id_consegna})
            st.success("Consegna aggiornata con successo!")
            time.sleep(2)
            st.session_state.show_form_update_consegna = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento della consegna: {e}")
    elif cancel_button:
        st.session_state.show_form_update_consegna = False
        st.rerun()

# Sezione per aggiornare un veicolo
if st.session_state.get("show_form_update_veicolo", False):
    st.write("### Aggiorna Veicolo")
    with st.form(key='veicolo_form_update'):
        id_veicolo = st.number_input("ID Veicolo", min_value=1)
        tipo = st.selectbox("Tipo", ['Bilico', 'Furgone', 'Carrello_Elevatore'])
        capacita = st.number_input("Capacità", min_value=1)
        stato = st.selectbox("Stato", ['Disponibile', 'In uso', 'Manutenzione'])
        targa = st.text_input("Targa")

        submit_button = st.form_submit_button(label="Aggiorna Veicolo")
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
        try:
            update_recordSQL(session, "Veicoli", {
                "Tipo": tipo,
                "Capacita": capacita,
                "Stato": stato,
                "Targa": targa
            }, "ID_Veicolo = :id_veicolo", {"id_veicolo": id_veicolo})
            st.success("Veicolo aggiornato con successo!")
            time.sleep(2)
            st.session_state.show_form_update_veicolo = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiornamento del veicolo: {e}")
    elif cancel_button:
        st.session_state.show_form_update_veicolo = False
        st.rerun()

# Visualizza veicoli
veicoli = select_recordsSQL(session, "Veicoli")
if veicoli:
    df_veicoli = pd.DataFrame(veicoli)
    st.write("### Veicoli")
    st.dataframe(df_veicoli)
else:
    st.error("Errore nel recuperare i dati dei veicoli dal database.")

# Bottone per mostrare il form di aggiunta veicolo
if "show_form_add_veicolo" not in st.session_state:
    st.session_state.show_form_add_veicolo = False
if not st.session_state.show_form_add_veicolo:
    if st.button("Aggiungi Veicolo"):
        st.session_state.show_form_add_veicolo = True
        st.rerun()

# Sezione per aggiungere un veicolo
if st.session_state.get("show_form_add_veicolo", False):
    st.write("### Aggiungi Veicolo")
    with st.form(key='veicolo_form_add'):
        tipo = st.selectbox("Tipo", ['Bilico', 'Furgone', 'Carrello_Elevatore'])
        capacita = st.number_input("Capacità", min_value=1)
        stato = st.selectbox("Stato", ['Disponibile', 'In uso', 'Manutenzione'])
        targa = st.text_input("Targa")

        submit_button = st.form_submit_button(label="Aggiungi Veicolo")
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
        try:
            add_recordSQL(session, "Veicoli", {
                "Tipo": tipo,
                "Capacita": capacita,
                "Stato": stato,
                "Targa": targa
            })
            st.success("Veicolo aggiunto con successo!")
            time.sleep(2)
            st.session_state.show_form_add_veicolo = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'aggiunta del veicolo: {e}")
    elif cancel_button:
        st.session_state.show_form_add_veicolo = False
        st.rerun()

# Bottone per mostrare il form di aggiornamento veicolo
if "show_form_update_veicolo" not in st.session_state:
    st.session_state.show_form_update_veicolo = False
if not st.session_state.show_form_update_veicolo:
    if st.button("Aggiorna Veicolo"):
        st.session_state.show_form_update_veicolo = True
        st.rerun()

# Bottone per mostrare il form di eliminazione veicolo
if "show_form_delete_veicolo" not in st.session_state:
    st.session_state.show_form_delete_veicolo = False
if not st.session_state.show_form_delete_veicolo:
    if st.button("Elimina Veicolo"):
        st.session_state.show_form_delete_veicolo = True
        st.rerun()

# Sezione per eliminare un veicolo
if st.session_state.get("show_form_delete_veicolo", False):
    st.write("### Elimina Veicolo")
    with st.form(key='veicolo_form_delete'):
        id_veicolo = st.number_input("ID Veicolo", min_value=1)

        submit_button = st.form_submit_button(label="Elimina Veicolo")
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
        try:
            delete_recordSQL(session, "Veicoli", "ID_Veicolo = :id_veicolo", {"id_veicolo": id_veicolo})
            st.success("Veicolo eliminato con successo!")
            time.sleep(2)
            st.session_state.show_form_delete_veicolo = False
            st.rerun()
        except Exception as e:
            st.error(f"Errore durante l'eliminazione del veicolo: {e}")
    elif cancel_button:
        st.session_state.show_form_delete_veicolo = False
        st.rerun()