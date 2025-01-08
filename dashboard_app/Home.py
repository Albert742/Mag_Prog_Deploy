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
        st.sidebar.page_link('pages/Employee_Management.py', label='Gestione Dipendenti')
        st.sidebar.page_link('pages/Orders_Managment.py', label='Gestione Ordini')
        st.sidebar.page_link('pages/Maintenance_Management.py', label='Gestione Manutenzioni')
        st.sidebar.page_link('pages/Test_Magazzino.py', label='Test Funzionalità')
    elif ruolo == "Tecnico":
        st.sidebar.page_link('Home.py', label='Home')
        st.sidebar.page_link('pages/Dashboard_Overview.py', label='Panoramica Dashboard')
        st.sidebar.page_link('pages/Inventory_Management.py', label='Gestione Inventario')
        st.sidebar.page_link('pages/Orders_Managment.py', label='Gestione Ordini')
        st.sidebar.page_link('pages/Maintenance_Management.py', label='Gestione Manutenzioni')
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
        - **Gestione Zone e Scaffalature**: Sovrintendere e gestire le zone di stoccaggio e le loro configurazioni.
        - **Controllo Qualità**: Monitorare le attività di controllo qualità per mantenere gli standard.

        ### Funzionalità Principali
        - **Dati in Tempo Reale**: Rimani aggiornato con informazioni in tempo reale sul tuo magazzino.
        - **Interfaccia Utente Amichevole**: Semplifica le operazioni del magazzino complesse con un layout intuitivo.
        - **Analisi e Reporting**: Genera informazioni dai dati delle operazioni del magazzino per prendere decisioni informate.

        ### Guida all'Avvio
        Utilizza il menu a sinistra per navigare tra le diverse pagine, comprese:

        - **Panoramica Inventari**: Visualizza i livelli di stock correnti e i rapporti dettagliati sull'inventario.
        - **Gestione Ordini**: Gestisci gli ordini in arrivo e in partenza in modo efficiente.
        - **Gestione Zone**: Organizza e ottimizza le zone di stoccaggio e le scaffalature.
        - **Log di Controllo Qualità**: Verifica i log di controllo qualità per assicurarti che siano rispettati gli standard.
        """
    )

    st.info(
        "Consiglio: Segna questo pagina come preferita per accedere rapidamente alla pagina.",
        icon="🔖",
    )

if __name__ == "__main__":
    warehouse_dashboard_home()