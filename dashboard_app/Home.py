import streamlit as st
import time
from utils.MagUtils import log_logout
from streamlit_extras.switch_page_button import switch_page

# Funzione per la pagina di ingresso della dashboard
def warehouse_dashboard_home():
    
    # Check authentication state and display appropriate button
    if "authenticated" not in st.session_state or not st.session_state.get("authenticated", False):
        st.sidebar.write("Utente Guest.")
        if st.sidebar.button("Log In"):
           switch_page("Login")
    elif st.sidebar.button("Log Out"):
        log_logout(st.session_state.get("id_utente"))
        st.success("Logout effettuato con successo. Verrai reindirizzato alla pagina di login.")
        time.sleep(2)
        switch_page("Login")
        st.session_state.clear()
        st.rerun()
    else:
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

    # Contenuto della pagina
    st.image("logo.jpg", use_container_width=True)
    st.write("# Benvenuto nella Dashboard di Gestione Magazzino di Food&Pharma 📦")

    if st.session_state.get("authenticated", False):
        st.sidebar.success("Naviga in un'altra pagina utilizzando il menu.")
    else:
        st.sidebar.info("Esegui il login per visualizzare le altre pagine.")

    st.markdown(
        """
        ### Panoramica
        Questa dashboard è stata progettata per gestire le operazioni del magazzino in modo efficiente, comprese:

        - **Gestione Inventari**: Tenere traccia delle quantità di stock, delle posizioni dei prodotti e delle date di scadenza.
        - **Elaborazione Ordini**: Creare, aggiornare e monitorare gli ordini per operazioni fluide.
        - **Gestione Dipendenti**: Assegnare ruoli e autorizzazioni ai dipendenti per un'organizzazione efficace.
        - **Gestione Manutenzioni**: Pianificare e monitorare le manutenzioni del magazzino.
        

        ### Funzionalità Principali
        - **Dati in Tempo Reale**: Rimani aggiornato con informazioni in tempo reale sul tuo magazzino.
        - **Interfaccia Utente Amichevole**: Semplifica le operazioni del magazzino complesse con un layout intuitivo.
        - **Reporting**: Visualizza dati aggregati per una panoramica completa del tuo magazzino.

        ### Guida all'Avvio
        Effettua l'accesso è utilizza il menu a sinistra per navigare tra le diverse pagine.
        """
    )

    st.info(
        "Consiglio: Segna questo pagina come preferita per accedere rapidamente alla pagina.",
        icon="🔖",
    )

if __name__ == "__main__":
    warehouse_dashboard_home()