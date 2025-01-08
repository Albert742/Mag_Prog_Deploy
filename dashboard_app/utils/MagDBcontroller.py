from sqlalchemy import create_engine, text, insert, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError
import time
import toml

def connessione():
    """
    Esegue la connessione al database specificato nel file secrets.toml
    e restituisce un oggetto Session per l'interazione con il database.

    Se la connessione non riesce dopo 3 tentativi, restituisce None.
    """

    toml_data = toml.load(".streamlit/secrets.toml")
    host = toml_data["mysql"]["host"]
    user = toml_data["mysql"]["username"]
    password = toml_data["mysql"]["password"]
    database = toml_data["mysql"]["database"]
    port = toml_data["mysql"]["port"]

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    engine = None
    session = None
    max_retries = 3
    retry_delay = 2

    for attempt in range(1, max_retries + 1):
        try:
            engine = create_engine(connection_string)
            Session = sessionmaker(bind=engine)
            session = Session()
            print(f"Connessione al database riuscita (tentativo {attempt}).")
            return session
        except OperationalError as e:
            print(f"Errore di connessione al database (tentativo {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                print(f"Riprovando tra {retry_delay} secondi...")
                time.sleep(retry_delay)
            else:
                print("Numero massimo di tentativi di connessione raggiunto.")
                return None

    return None

def create_database():
    """
    Crea il database se non esiste già.
    """
    toml_data = toml.load(".streamlit/secrets.toml")
    host = toml_data["mysql"]["host"]
    user = toml_data["mysql"]["username"]
    password = toml_data["mysql"]["password"]
    database = toml_data["mysql"]["database"]
    port = toml_data["mysql"]["port"]

    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/"

    engine = create_engine(connection_string)
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database}"))
        print(f"Database '{database}' creato con successo (se non esisteva già).")

def create_tableSQL(session, nome_tabella, definizione):
    """
    Crea una tabella nel database se non esiste.

    Args:
        session: La sessione di connessione al database.
        nome_tabella: Il nome della tabella da creare.
        definizione: La definizione della tabella, ad esempio "id INT PRIMARY KEY, campo VARCHAR(255)".

    Returns:
        bool: True se l'operazione va a buon fine, False in caso di errore.
    """
    try:
        table_name = get_table_name(session, nome_tabella)
        if table_name:
            print(f"La tabella {nome_tabella} esiste già.")
            return False

        with session.begin():
            sql = f"CREATE TABLE IF NOT EXISTS `{nome_tabella}` ({definizione})"
            session.execute(text(sql))
        return True
    except Exception as e:
        session.rollback()
        print(f"Errore durante la creazione della tabella {nome_tabella}: {e}")
        return False

def init_tables(session):
    """
        Inizializza le tabelle del database.
        
        Args:
            session: La sessione di connessione al database.
        
        Returns:
            None
    """
    tabelle = {
        "Fornitori": """
            ID_Fornitore INT PRIMARY KEY AUTO_INCREMENT,
            Nome VARCHAR(255) NOT NULL,
            Indirizzo VARCHAR(255),
            Telefono VARCHAR(20),
            Email VARCHAR(255) UNIQUE,
            PartitaIVA VARCHAR(20) UNIQUE NOT NULL
        """,
        "Prodotti": """
            ID_Prodotto INT PRIMARY KEY AUTO_INCREMENT,
            ID_Fornitore INT,
            Nome VARCHAR(255) UNIQUE NOT NULL,
            Produttore VARCHAR(255),
            Tipo ENUM('Alimentare', 'Farmaceutico') NOT NULL,
            QuantitàConfezione DECIMAL(10, 2) NOT NULL,
            UnitaMisura ENUM('kg', 'g', 'l', 'ml', 'compresse', 'capsule') NOT NULL,
            FOREIGN KEY (ID_Fornitore) REFERENCES Fornitori(ID_Fornitore) ON DELETE SET NULL
        """,
        "Zone": """
            ID_Zona INT PRIMARY KEY AUTO_INCREMENT,
            Nome VARCHAR(255) UNIQUE NOT NULL,
            Tipo ENUM('Stoccaggio_Alimentari', 'Stoccaggio_Farmaceutici', 'Carico', 'Scarico') NOT NULL,
            Descrizione TEXT
        """,
        "Scaffalature": """
            ID_Scaffalatura INT PRIMARY KEY AUTO_INCREMENT,
            ID_Zona INT NOT NULL,
            Nome VARCHAR(255) UNIQUE NOT NULL,
            CapacitàLotti INT NOT NULL DEFAULT 100,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE
        """,
        "Lotti": """
            ID_Lotto INT PRIMARY KEY AUTO_INCREMENT,
            ID_Prodotto INT NOT NULL,
            ID_Fornitore INT NOT NULL,
            ID_Zona INT NOT NULL,
            ID_Scaffalatura INT NOT NULL,
            Lotto VARCHAR(255),
            Scadenza DATE,
            QuantitàProdotto INT NOT NULL DEFAULT 1,
            PesoLotto DECIMAL(10, 2),
            PrezzoAcquisto DECIMAL(10, 2),
            ValoreLotto DECIMAL(10, 2),
            DataPrenotazione DATE,
            DataRicevimento DATE,
            Stato ENUM('Disponibile', 'Esaurito', 'Prenotato') DEFAULT 'Disponibile',
            FOREIGN KEY (ID_Prodotto) REFERENCES Prodotti(ID_Prodotto) ON DELETE CASCADE,
            FOREIGN KEY (ID_Fornitore) REFERENCES Fornitori(ID_Fornitore) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Scaffalatura) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE,
            UNIQUE (ID_Prodotto, Lotto)
        """,
        "Clienti": """
            ID_Cliente INT PRIMARY KEY AUTO_INCREMENT,
            Nome VARCHAR(255) NOT NULL,
            Indirizzo VARCHAR(255),
            Telefono VARCHAR(20),
            Email VARCHAR(255) UNIQUE,
            PartitaIVA VARCHAR(20) UNIQUE NOT NULL
        """,
        "Ordini": """
            ID_Ordine INT PRIMARY KEY AUTO_INCREMENT,
            DataOrdine TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Tipo ENUM('Entrata', 'Uscita') NOT NULL,
            ID_Fornitore INT,
            ID_Cliente INT,
            Stato ENUM('In elaborazione', 'Spedito', 'Concluso') DEFAULT 'In elaborazione',
            FOREIGN KEY (ID_Fornitore) REFERENCES Fornitori(ID_Fornitore) ON DELETE SET NULL,
            FOREIGN KEY (ID_Cliente) REFERENCES Clienti(ID_Cliente) ON DELETE SET NULL
        """,
        "DettagliOrdini": """
            ID_DettaglioOrdine INT PRIMARY KEY AUTO_INCREMENT,
            ID_Ordine INT NOT NULL,
            ID_Lotto INT NOT NULL,
            Quantita INT,
            FOREIGN KEY (ID_Ordine) REFERENCES Ordini(ID_Ordine) ON DELETE CASCADE,
            FOREIGN KEY (ID_Lotto) REFERENCES Lotti(ID_Lotto) ON DELETE CASCADE
        """,
        "BaieCaricoScarico": """
            ID_Baia INT PRIMARY KEY AUTO_INCREMENT,
            ZonaID INT NOT NULL,
            Nome VARCHAR(255) NOT NULL,
            Tipo ENUM('Carico', 'Scarico') NOT NULL,
            Stato ENUM('Libera', 'Occupata', 'Manutenzione') DEFAULT 'Libera',
            FOREIGN KEY (ZonaID) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            UNIQUE (ZonaID, Nome)
        """,
        "Sensori": """
            ID_Sensore INT PRIMARY KEY AUTO_INCREMENT,
            Tipo ENUM('Presenza', 'Temperatura', 'Umidità') NOT NULL,
            ID_Zona INT,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE SET NULL
            """,
        "LettureSensori": """
            ID_Lettura INT PRIMARY KEY AUTO_INCREMENT,
            ID_Sensore INT NOT NULL,
            Tipo ENUM('Temperatura', 'Umidità', 'Presenza') NOT NULL,
            Valore FLOAT NOT NULL,
            DataLettura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_Sensore) REFERENCES Sensori(ID_Sensore) ON DELETE CASCADE
        """,
        "StazioneRicarica": """
            ID_Ricarica INT PRIMARY KEY AUTO_INCREMENT,
            ZonaID INT NOT NULL,
            Nome VARCHAR(255) NOT NULL,
            Stato ENUM('Libera', 'Occupata', 'Inoperativa') DEFAULT 'Libera',
            FOREIGN KEY (ZonaID) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            UNIQUE (ZonaID, Nome)
        """,
        "Robot": """
            ID_Robot INT PRIMARY KEY AUTO_INCREMENT,
            ID_Sensore INT NOT NULL,
            ID_Zona INT NOT NULL,
            Nome VARCHAR(255) NOT NULL,
            Stato ENUM('Disponibile', 'Occupato', 'Manutenzione') DEFAULT 'Disponibile',
            PosizioneAttuale VARCHAR(255),
            Capacita INT,
            ID_Ricarica INT,
            FOREIGN KEY (ID_Sensore) REFERENCES Sensori(ID_Sensore) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Ricarica) REFERENCES StazioneRicarica(ID_Ricarica) ON DELETE SET NULL
        """,
        "RichiesteMovimento": """
            ID_Richiesta INT PRIMARY KEY AUTO_INCREMENT,
            ID_Lotto INT NOT NULL,
            ID_Zona_Partenza INT NOT NULL,
            ID_Zona_Destinazione INT NOT NULL,
            ID_Scaffalatura_Destinazione INT NOT NULL,
            ID_Robot INT,
            Priorita ENUM('Bassa', 'Media', 'Alta') DEFAULT 'Bassa',
            DataRichiesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_Lotto) REFERENCES Lotti(ID_Lotto) ON DELETE CASCADE,
            FOREIGN KEY (ID_Robot) REFERENCES Robot(ID_Robot) ON DELETE SET NULL,
            FOREIGN KEY (ID_Zona_Partenza) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona_Destinazione) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Scaffalatura_Destinazione) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE
        """,
        "DettagliMovimento": """
            ID_Movimento INT PRIMARY KEY AUTO_INCREMENT,
            ID_Richiesta INT,
            ID_Lotto INT NOT NULL,
            ID_Robot INT,
            ID_Zona_Partenza INT,
            ID_Zona_Destinazione INT,
            ID_Scaffalatura_Destinazione INT,
            Stato ENUM('Assegnato', 'In corso', 'Completato', 'Annullato') DEFAULT 'Assegnato',
            DataMovimento TIMESTAMP,
            DataCompletamento TIMESTAMP,
            TipoMovimento ENUM('Entrata', 'Uscita', 'Spostamento') NOT NULL,
            FOREIGN KEY (ID_Richiesta) REFERENCES RichiesteMovimento(ID_Richiesta) ON DELETE CASCADE,
            FOREIGN KEY (ID_Robot) REFERENCES Robot(ID_Robot) ON DELETE SET NULL,
            FOREIGN KEY (ID_Scaffalatura_Destinazione) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE,
            FOREIGN KEY (ID_Lotto) REFERENCES Lotti(ID_Lotto) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona_Partenza) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona_Destinazione) REFERENCES Zone(ID_Zona) ON DELETE CASCADE
        """,
        "Veicoli": """
            ID_Veicolo INT PRIMARY KEY AUTO_INCREMENT,
            Tipo ENUM('Bilico', 'Furgone', 'Carrello_Elevatore') NOT NULL,
            Capacita INT NOT NULL,
            Stato ENUM('Disponibile', 'In uso', 'Manutenzione') DEFAULT 'Disponibile',
            Targa VARCHAR(20) NOT NULL UNIQUE
        """,
        "Consegne": """
            ID_Consegna INT PRIMARY KEY AUTO_INCREMENT,
            ID_Ordine INT NOT NULL,
            ID_Veicolo INT,
            DataConsegna DATE,
            Stato ENUM('Pianificata', 'In corso', 'Completata', 'Annullata') DEFAULT 'Pianificata',
            FOREIGN KEY (ID_Ordine) REFERENCES Ordini(ID_Ordine) ON DELETE CASCADE,
            FOREIGN KEY (ID_Veicolo) REFERENCES Veicoli(ID_Veicolo) ON DELETE SET NULL
        """,
        "ManutenzioneRobot": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Robot INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo ENUM('Ispezione', 'Riparazione', 'Sostituzione') NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Robot) REFERENCES Robot(ID_Robot) ON DELETE CASCADE
        """,
        "ManutenzioneScaffalature": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Scaffalatura INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo ENUM('Ispezione', 'Pulizia', 'Riparazione', 'Sostituzione') NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Scaffalatura) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE
        """,
        "ManutenzioneZone": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Zona INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo ENUM('Ispezione', 'Pulizia', 'Riparazione') NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE
        """,
        "ManutenzioneVeicoli": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Veicolo INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo ENUM('Ispezione', 'Riparazione', 'Sostituzione') NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Veicolo) REFERENCES Veicoli(ID_Veicolo) ON DELETE CASCADE
        """,
        "Dipendenti": """
            ID_Dipendente VARCHAR(10) PRIMARY KEY,
            CodiceFiscale VARCHAR(16) NOT NULL UNIQUE,
            Nome VARCHAR(255) NOT NULL,
            Cognome VARCHAR(255) NOT NULL,
            Ruolo ENUM('Amministratore', 'Tecnico', 'Operatore') NOT NULL,
            Mansione ENUM('Manager', 'Tecnico IT', 'Manutenzione', 'Magazziniere', 'Responsabile Magazzino', 'Addetto Carico/Scarico', 'Operatore Logistico', 'Coordinatore Magazzino', 'Pianificatore', 'Controllo Qualità') NOT NULL,
            DataAssunzione DATE
        """,
        "TurniDipendenti": """
            ID_Turno INT PRIMARY KEY AUTO_INCREMENT,
            ID_Dipendente VARCHAR(10) NOT NULL,
            DataInizio TIMESTAMP NOT NULL,
            DataFine TIMESTAMP NOT NULL,
            Mansione VARCHAR(255),
            FOREIGN KEY (ID_Dipendente) REFERENCES Dipendenti(ID_Dipendente) ON DELETE CASCADE
        """,
        "Credenziali": """
            ID_Utente INT PRIMARY KEY AUTO_INCREMENT,
            Username VARCHAR(255) NOT NULL UNIQUE,
            Password VARBINARY(60) NOT NULL,
            Ruolo ENUM('Amministratore', 'Operatore', 'Tecnico', 'Guest') NOT NULL,
            ID_Dipendente VARCHAR(10),
            FOREIGN KEY (ID_Dipendente) REFERENCES Dipendenti(ID_Dipendente) ON DELETE SET NULL
        """,
        "LogUtenti": """
            ID_LogUtente INT PRIMARY KEY AUTO_INCREMENT,
            ID_Utente INT,
            DataOra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Tipo ENUM('Accesso', 'Registrazione', 'Logout') NOT NULL,
            Esito ENUM('Successo', 'Fallito') NOT NULL,
            Dettagli VARCHAR(255),
            IP VARCHAR(255),
            FOREIGN KEY (ID_Utente) REFERENCES Credenziali(ID_Utente) ON DELETE CASCADE
        """,
        "LogMagazzino": """
            ID_LogMagazzino INT PRIMARY KEY AUTO_INCREMENT,
            ID_Sensore INT,
            ID_Lotto INT,
            TipoNotifica ENUM('Avviso', 'Alarme') NOT NULL,
            TipoEvento ENUM('Scadenza Lotto', 'Temperatura', 'Umidità') NOT NULL,
            Messaggio TEXT,
            DataOra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_Sensore) REFERENCES Sensori(ID_Sensore) ON DELETE CASCADE,
            FOREIGN KEY (ID_Lotto) REFERENCES Lotti(ID_Lotto) ON DELETE CASCADE
        """,
    }
    for nome_tabella, definizione in tabelle.items():
        create_tableSQL(session, nome_tabella, definizione)

def initSQL():
    """
    Funzione per inizializzare le tabelle del database.
    
    Creazione delle tabelle del database in base alla definizione contenuta nel dizionario tabelle.
    
    Returns:
        None
    """
    with connessione() as conn:
        if conn:
            init_tables(conn)

def populateSQL():
    """
    Popola le tabelle del database con dati di esempio.

    Creazione di dati di esempio per le tabelle del database.
    I dati vengono inseriti utilizzando la funzione insert di SQLAlchemy.
    Viene eseguita una transazione per l'inserimento dei dati.
    Se l'inserimento ha successo, la transazione viene confermata e vengono stampati
    il numero di record inseriti. Se l'inserimento fallisce, la transazione viene
    annullata e viene stampato l'errore.
    """
    with connessione() as conn:
        if conn:
            metadata = MetaData()
            metadata.reflect(bind=conn.bind)  # Reflect the database schema
            def get_table(metadata, table_name):
                # Try to get the table with the exact name
                table = metadata.tables.get(table_name)
                if table is None:
                    # If not found, try to get the table with the lowercase name
                    table = metadata.tables.get(table_name.lower())
                if table is None:
                    # If still not found, try to get the table with the uppercase name
                    table = metadata.tables.get(table_name.upper())
                return table
            
            # Fornitori
            fornitori_table = get_table(metadata, "Fornitori")
            fornitori_data = [
                {"Nome": "Fornitore A", "Indirizzo": "Via Roma 1, Milano", "Telefono": "0212345678", "Email": "fornitoreA@email.com", "PartitaIVA": "IT12345678901"},
                {"Nome": "Fornitore B", "Indirizzo": "Corso Italia 2, Roma", "Telefono": "0698765432", "Email": "fornitoreB@email.com", "PartitaIVA": "IT98765432109"},
                {"Nome": "Fornitore C", "Indirizzo": "Piazza Verdi 3, Napoli", "Telefono": "0815554433", "Email": "fornitoreC@email.com", "PartitaIVA": "IT11223344556"},
                {"Nome": "Fornitore D", "Indirizzo": "Via Dante 4, Torino", "Telefono": "0116667788", "Email": "fornitoreD@email.com", "PartitaIVA": "IT66554433221"},
                {"Nome": "Fornitore E", "Indirizzo": "Via Garibaldi 5, Palermo", "Telefono": "0917778899", "Email": "fornitoreE@email.com", "PartitaIVA": "IT22334455667"},
            ]
            try:
                result = conn.execute(insert(fornitori_table).values(fornitori_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} fornitori.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei fornitori: {e}")

            # Prodotti
            prodotti_table = get_table(metadata, "Prodotti")
            prodotti_data = [
                {"ID_Fornitore": 1, "Nome": "Pasta di Grano Duro", "Produttore": "Pastificio Italia", "Tipo": "Alimentare", "QuantitàConfezione": 1.0, "UnitaMisura": "kg"},
                {"ID_Fornitore": 1, "Nome": "Olio Extra Vergine di Oliva", "Produttore": "Oleificio Sole", "Tipo": "Alimentare", "QuantitàConfezione": 1.0, "UnitaMisura": "l"},
                {"ID_Fornitore": 2, "Nome": "Paracetamolo 500mg", "Produttore": "Farmaceutica ABC", "Tipo": "Farmaceutico", "QuantitàConfezione": 20.0, "UnitaMisura": "compresse"},
                {"ID_Fornitore": 2, "Nome": "Aspirina 100mg", "Produttore": "Farmaceutica XYZ", "Tipo": "Farmaceutico", "QuantitàConfezione": 30.0, "UnitaMisura": "compresse"},
                {"ID_Fornitore": 3, "Nome": "Biscotti Frollini", "Produttore": "Biscottificio Dolce", "Tipo": "Alimentare", "QuantitàConfezione": 500, "UnitaMisura": "g"},
                {"ID_Fornitore": 3, "Nome": "Sciroppo per la Tosse", "Produttore": "Farmaceutica ABC", "Tipo": "Farmaceutico", "QuantitàConfezione": 200.0, "UnitaMisura": "ml"},
                {"ID_Fornitore": 4, "Nome": "Riso Carnaroli", "Produttore": "Riseria Bella", "Tipo": "Alimentare", "QuantitàConfezione": 1.0, "UnitaMisura": "kg"},
                {"ID_Fornitore": 4, "Nome": "Vitamina C 1000mg", "Produttore": "Integratori Plus", "Tipo": "Farmaceutico", "QuantitàConfezione": 60.0, "UnitaMisura": "capsule"},
                {"ID_Fornitore": 5, "Nome": "Caffè Macinato", "Produttore": "Caffè Aroma", "Tipo": "Alimentare", "QuantitàConfezione": 250.0, "UnitaMisura": "g"},
                {"ID_Fornitore": 5, "Nome": "Ibuprofene 400mg", "Produttore": "Farmaceutica XYZ", "Tipo": "Farmaceutico", "QuantitàConfezione": 20.0, "UnitaMisura": "compresse"}
            ]
            try:
                result = conn.execute(insert(prodotti_table).values(prodotti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} prodotti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei prodotti: {e}")

            # Zone
            zone_table = get_table(metadata, "Zone")
            zone_data = [
                {"Nome": "Stoccaggio A01", "Tipo": "Stoccaggio_Alimentari", "Descrizione": "Zona di stoccaggio per prodotti alimentari"},
                {"Nome": "Stoccaggio F01", "Tipo": "Stoccaggio_Farmaceutici", "Descrizione": "Zona di stoccaggio per prodotti farmaceutici"},
                {"Nome": "Baia Carico01", "Tipo": "Carico", "Descrizione": "Zona per il carico delle merci"},
                {"Nome": "Baia Scarico01", "Tipo": "Scarico", "Descrizione": "Zona per lo scarico delle merci"}
            ]
            try:
                result = conn.execute(insert(zone_table).values(zone_data))
                conn.commit()
                print(f"Inserite {result.rowcount} zone.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle zone: {e}")
                
            # Scaffalature
            scaffalature_table = get_table(metadata, "Scaffalature")
            scaffalature_data = [
                {"ID_Zona": 1, "Nome": "Scaffale A1", "CapacitàLotti": 100},
                {"ID_Zona": 1, "Nome": "Scaffale A2", "CapacitàLotti": 80},
                {"ID_Zona": 2, "Nome": "Scaffale B1", "CapacitàLotti": 150},
                {"ID_Zona": 2, "Nome": "Scaffale B2", "CapacitàLotti": 120},
                {"ID_Zona": 3, "Nome": "Scaffale C1", "CapacitàLotti": 50},
                {"ID_Zona": 4, "Nome": "Scaffale D1", "CapacitàLotti": 60}
            ]
            try:
                result = conn.execute(insert(scaffalature_table).values(scaffalature_data))
                conn.commit()
                print(f"Inserite {result.rowcount} scaffalature.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle scaffalature: {e}")

            # Lotti
            lotti_table = get_table(metadata, "Lotti")
            lotti_data = [
                {"ID_Prodotto": 1, "ID_Fornitore": 1, "ID_Zona": 1, "ID_Scaffalatura": 1, "Lotto": "L001", "Scadenza": "2024-12-31", "QuantitàProdotto": 100, "PesoLotto": 100.0, "PrezzoAcquisto": 200.0, "ValoreLotto": 240.0, "DataRicevimento": "2023-01-01", "DataPrenotazione": "2022-12-15", "Stato": "Disponibile"},
                {"ID_Prodotto": 2, "ID_Fornitore": 1, "ID_Zona": 1, "ID_Scaffalatura": 2, "Lotto": "L002", "Scadenza": "2024-11-30", "QuantitàProdotto": 150, "PesoLotto": 150.0, "PrezzoAcquisto": 750.0, "ValoreLotto": 900.0, "DataRicevimento": "2023-02-15", "DataPrenotazione": "2023-02-01", "Stato": "Disponibile"},
                {"ID_Prodotto": 3, "ID_Fornitore": 2, "ID_Zona": 2, "ID_Scaffalatura": 3, "Lotto": "L003", "Scadenza": "2024-10-31", "QuantitàProdotto": 200, "PesoLotto": 4.0, "PrezzoAcquisto": 20.0, "ValoreLotto": 24.0, "DataRicevimento": "2023-03-10", "DataPrenotazione": "2023-03-01", "Stato": "Esaurito"},
                {"ID_Prodotto": 4, "ID_Fornitore": 2, "ID_Zona": 2, "ID_Scaffalatura": 4, "Lotto": "L004", "Scadenza": "2024-09-30", "QuantitàProdotto": 180, "PesoLotto": 5.4, "PrezzoAcquisto": 9.0, "ValoreLotto": 10.8, "DataRicevimento": None, "DataPrenotazione": "2023-04-15", "Stato": "Prenotato"},
                {"ID_Prodotto": 5, "ID_Fornitore": 3, "ID_Zona": 3, "ID_Scaffalatura": 5, "Lotto": "L005", "Scadenza": "2024-08-31", "QuantitàProdotto": 250, "PesoLotto": 125.0, "PrezzoAcquisto": 750.0, "ValoreLotto": 900.0, "DataRicevimento": "2023-05-05", "DataPrenotazione": "2023-04-25", "Stato": "Disponibile"},
                {"ID_Prodotto": 6, "ID_Fornitore": 3, "ID_Zona": 3, "ID_Scaffalatura": 6, "Lotto": "L006", "Scadenza": "2024-07-31", "QuantitàProdotto": 220, "PesoLotto": 44.0, "PrezzoAcquisto": 440.0, "ValoreLotto": 528.0, "DataRicevimento": "2023-06-15", "DataPrenotazione": "2023-06-01", "Stato": "Esaurito"},
                {"ID_Prodotto": 7, "ID_Fornitore": 4, "ID_Zona": 1, "ID_Scaffalatura": 1, "Lotto": "L007", "Scadenza": "2024-06-30", "QuantitàProdotto": 160, "PesoLotto": 160.0, "PrezzoAcquisto": 480.0, "ValoreLotto": 576.0, "DataRicevimento": None,"DataPrenotazione": "2023-07-05", "Stato": "Prenotato"},
                {"ID_Prodotto": 8, "ID_Fornitore": 4, "ID_Zona": 1, "ID_Scaffalatura": 2, "Lotto": "L008", "Scadenza": "2024-05-31", "QuantitàProdotto": 140, "PesoLotto": 8.4, "PrezzoAcquisto": 168.0, "ValoreLotto": 201.6, "DataRicevimento": "2023-08-20", "DataPrenotazione": "2023-08-01", "Stato": "Disponibile"},
                {"ID_Prodotto": 9, "ID_Fornitore": 5, "ID_Zona": 2, "ID_Scaffalatura": 3, "Lotto": "L009", "Scadenza": "2024-04-30", "QuantitàProdotto": 130, "PesoLotto": 32.5, "PrezzoAcquisto": 520.0, "ValoreLotto": 624.0, "DataRicevimento": "2023-09-25", "DataPrenotazione": "2023-09-10", "Stato": "Esaurito"},
                {"ID_Prodotto": 10, "ID_Fornitore": 5, "ID_Zona": 2, "ID_Scaffalatura": 4, "Lotto": "L010", "Scadenza": "2024-03-31", "QuantitàProdotto": 190, "PesoLotto": 3.8, "PrezzoAcquisto": 28.5, "ValoreLotto": 34.2, "DataRicevimento": None,"DataPrenotazione": "2023-10-01", "Stato": "Prenotato"}
            ]
            try:
                result = conn.execute(insert(lotti_table).values(lotti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} lotti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei lotti: {e}")
            # Clienti
            clienti_table = get_table(metadata, "Clienti")
            clienti_data = [
                {"Nome": "Cliente X", "Indirizzo": "Via Verdi 10, Milano", "Telefono": "0212345679", "Email": "clienteX@email.com", "PartitaIVA": "IT11122233344"},
                {"Nome": "Cliente Y", "Indirizzo": "Piazza Roma 20, Roma", "Telefono": "0698765433", "Email": "clienteY@email.com", "PartitaIVA": "IT55566677788"},
                {"Nome": "Cliente Z", "Indirizzo": "Corso Italia 15, Napoli", "Telefono": "0812345678", "Email": "clienteZ@email.com", "PartitaIVA": "IT99988877766"},
                {"Nome": "Cliente W", "Indirizzo": "Via Garibaldi 5, Torino", "Telefono": "0112345678", "Email": "clienteW@email.com", "PartitaIVA": "IT44433322211"},
                {"Nome": "Cliente V", "Indirizzo": "Piazza Duomo 1, Firenze", "Telefono": "0552345678", "Email": "clienteV@email.com", "PartitaIVA": "IT33322211100"}
            ]
            try:
                result = conn.execute(insert(clienti_table).values(clienti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} clienti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei clienti: {e}")
            # Ordini
            ordini_table = get_table(metadata, "Ordini")
            ordini_data = [
                {"DataOrdine": "2023-10-25 09:00:00", "Tipo": "Entrata", "ID_Fornitore": 1, "ID_Cliente": None, "Stato": "In elaborazione"},
                {"DataOrdine": "2023-10-26 10:00:00", "Tipo": "Uscita", "ID_Fornitore": None, "ID_Cliente": 1, "Stato": "Spedito"},
                {"DataOrdine": "2023-10-27 11:00:00", "Tipo": "Entrata", "ID_Fornitore": 2, "ID_Cliente": None, "Stato": "Concluso"}
            ]
            try:
                result = conn.execute(insert(ordini_table).values(ordini_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} ordini.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento degli ordini: {e}")

            # DettagliOrdini
            dettagli_ordini_table = get_table(metadata, "DettagliOrdini")
            dettagli_ordini_data = [
                {"ID_Ordine": 1, "ID_Lotto": 1, "Quantita": 50},
                {"ID_Ordine": 2, "ID_Lotto": 2, "Quantita": 100},
                {"ID_Ordine": 3, "ID_Lotto": 3, "Quantita": 75}
            ]
            try:
                result = conn.execute(insert(dettagli_ordini_table).values(dettagli_ordini_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} dettagli ordini.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei dettagli ordini: {e}")
                
            # BaieCaricoScarico
            baie_table = get_table(metadata, "BaieCaricoScarico")
            baie_data = [
                {"ZonaID": 3, "Nome": "Baia Carico 1", "Tipo": "Carico", "Stato": "Libera"},
                {"ZonaID": 3, "Nome": "Baia Carico 2", "Tipo": "Carico", "Stato": "Libera"},
                {"ZonaID": 4, "Nome": "Baia Scarico 1", "Tipo": "Scarico", "Stato": "Libera"},
                {"ZonaID": 4, "Nome": "Baia Scarico 2", "Tipo": "Scarico", "Stato": "Libera"},
            ]
            try:
                result = conn.execute(insert(baie_table).values(baie_data))
                conn.commit()
                print(f"Inserite {result.rowcount} baie di carico/scarico.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle baie: {e}")

            # Sensori
            sensori_table = get_table(metadata, "Sensori")
            sensori_data = [
                {"Tipo": "Presenza", "ID_Zona": 1},
                {"Tipo": "Temperatura", "ID_Zona": 1},
                {"Tipo": "Umidità", "ID_Zona": 1},
                {"Tipo": "Presenza", "ID_Zona": 2},
                {"Tipo": "Temperatura", "ID_Zona": 2},
                {"Tipo": "Umidità", "ID_Zona": 2},
                {"Tipo": "Presenza", "ID_Zona": 3},
                {"Tipo": "Temperatura", "ID_Zona": 3},
                {"Tipo": "Umidità", "ID_Zona": 3},
                {"Tipo": "Presenza", "ID_Zona": 4},
                {"Tipo": "Temperatura", "ID_Zona": 4},
                {"Tipo": "Umidità", "ID_Zona": 4},
                
            ]

            try:
                result = conn.execute(insert(sensori_table).values(sensori_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} sensori.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei sensori: {e}")


            # StazioneRicarica
            stazione_ricarica_table = get_table(metadata, "StazioneRicarica")
            stazioni_ricarica_data = [
                {"ZonaID": 1, "Nome": "Stazione Ricarica 1", "Stato": "Libera"},
                {"ZonaID": 2, "Nome": "Stazione Ricarica 2", "Stato": "Libera"},
                {"ZonaID": 3, "Nome": "Stazione Ricarica 3", "Stato": "Libera"},
                {"ZonaID": 4, "Nome": "Stazione Ricarica 4", "Stato": "Libera"}
            ]
            try:
                result = conn.execute(insert(stazione_ricarica_table).values(stazioni_ricarica_data))
                conn.commit()
                print(f"Inserite {result.rowcount} stazioni di ricarica.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle stazioni di ricarica: {e}")

            # Robot
            robot_table = get_table(metadata, "Robot")
            robot_data = [
                {"ID_Sensore": 1, "ID_Zona": 1, "Nome": "Robot A", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale A1", "Capacita": 100, "ID_Ricarica": 1},
                {"ID_Sensore": 1, "ID_Zona": 1, "Nome": "Robot B", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale A2", "Capacita": 120, "ID_Ricarica": 1},
                {"ID_Sensore": 4, "ID_Zona": 2, "Nome": "Robot C", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale B1", "Capacita": 150, "ID_Ricarica": 2},
                {"ID_Sensore": 4, "ID_Zona": 2, "Nome": "Robot D", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale B2", "Capacita": 130, "ID_Ricarica": 2},
                {"ID_Sensore": 7, "ID_Zona": 3, "Nome": "Robot E", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale C1", "Capacita": 110, "ID_Ricarica": 3},
                {"ID_Sensore": 10, "ID_Zona": 4, "Nome": "Robot F", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale D1", "Capacita": 140, "ID_Ricarica": 4}
            ]
            try:
                result = conn.execute(insert(robot_table).values(robot_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} robot.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei robot: {e}")

            # RichiesteMovimento
            richieste_table = get_table(metadata, "RichiesteMovimento")
            richieste_data = [
                {"ID_Lotto": 1, "ID_Zona_Partenza": 1, "ID_Zona_Destinazione": 2, "ID_Scaffalatura_Destinazione": 1, "ID_Robot": 1, "Priorita": "Alta", "DataRichiesta": "2023-10-27 10:00:00"},
                {"ID_Lotto": 2, "ID_Zona_Partenza": 1, "ID_Zona_Destinazione": 3, "ID_Scaffalatura_Destinazione": 2, "ID_Robot": 2, "Priorita": "Media", "DataRichiesta": "2023-10-28 11:00:00"},
                {"ID_Lotto": 3, "ID_Zona_Partenza": 2, "ID_Zona_Destinazione": 4, "ID_Scaffalatura_Destinazione": 3, "ID_Robot": 2, "Priorita": "Bassa", "DataRichiesta": "2023-10-29 12:00:00"},
                {"ID_Lotto": 4, "ID_Zona_Partenza": 3, "ID_Zona_Destinazione": 1, "ID_Scaffalatura_Destinazione": 4, "ID_Robot": 3, "Priorita": "Alta", "DataRichiesta": "2023-10-30 13:00:00"},
                {"ID_Lotto": 5, "ID_Zona_Partenza": 4, "ID_Zona_Destinazione": 2, "ID_Scaffalatura_Destinazione": 1, "ID_Robot": 4, "Priorita": "Media", "DataRichiesta": "2023-10-31 14:00:00"}
            ]
            try:
                result = conn.execute(insert(richieste_table).values(richieste_data))
                conn.commit()
                print(f"Inserite {result.rowcount} richieste di movimento.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle richieste di movimento: {e}")

            # DettagliMovimento
            dettagli_movimento_table = get_table(metadata, "DettagliMovimento")
            dettagli_movimento_data = [
                {"ID_Richiesta": 1, "ID_Lotto": 1, "ID_Robot": 1, "ID_Zona_Partenza": 1, "ID_Zona_Destinazione": 2, "ID_Scaffalatura_Destinazione": 1, "Stato": "Completato", "DataMovimento": "2023-10-27 10:00:00", "DataCompletamento": "2023-10-27 10:15:00", "TipoMovimento": "Spostamento"},
                {"ID_Richiesta": 2, "ID_Lotto": 2, "ID_Robot": 2, "ID_Zona_Partenza": 1, "ID_Zona_Destinazione": 3, "ID_Scaffalatura_Destinazione": 2, "Stato": "In corso", "DataMovimento": "2023-10-28 11:00:00", "DataCompletamento": None, "TipoMovimento": "Spostamento"},
                {"ID_Richiesta": 3, "ID_Lotto": 3, "ID_Robot": 2, "ID_Zona_Partenza": 2, "ID_Zona_Destinazione": 4, "ID_Scaffalatura_Destinazione": 3, "Stato": "Assegnato", "DataMovimento": "2023-10-29 12:00:00", "DataCompletamento": None, "TipoMovimento": "Spostamento"},
                {"ID_Richiesta": 4, "ID_Lotto": 4, "ID_Robot": 3, "ID_Zona_Partenza": 2, "ID_Zona_Destinazione": 1, "ID_Scaffalatura_Destinazione": 2, "Stato": "Completato", "DataMovimento": "2023-11-01 09:00:00", "DataCompletamento": "2023-11-01 09:30:00", "TipoMovimento": "Entrata"},
                {"ID_Richiesta": 5, "ID_Lotto": 5, "ID_Robot": 4, "ID_Zona_Partenza": 4, "ID_Zona_Destinazione": 2, "ID_Scaffalatura_Destinazione": 3, "Stato": "In corso", "DataMovimento": "2023-11-02 10:00:00", "DataCompletamento": None, "TipoMovimento": "Uscita"}
            ]

            try:
                result = conn.execute(insert(dettagli_movimento_table).values(dettagli_movimento_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} dettagli movimento.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei dettagli movimento: {e}")

            # Veicoli
            veicoli_table = get_table(metadata, "Veicoli")
            veicoli_data = [
                {"Tipo": "Bilico", "Capacita": 10000, "Stato": "Disponibile", "Targa": "AA123BB"},
                {"Tipo": "Furgone", "Capacita": 2000, "Stato": "Disponibile", "Targa": "CC456DD"},
                {"Tipo": "Carrello_Elevatore", "Capacita": 500, "Stato": "Disponibile", "Targa": "EE789FF"}
            ]
            try:
                result = conn.execute(insert(veicoli_table).values(veicoli_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} veicoli.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei veicoli: {e}")

            # Consegne
            consegne_table = get_table(metadata, "Consegne")
            consegne_data = [
                {"ID_Ordine": 1, "ID_Veicolo": 1, "DataConsegna": "2023-10-28", "Stato": "Completata"},
                {"ID_Ordine": 2, "ID_Veicolo": 2, "DataConsegna": "2023-10-30", "Stato": "In corso"},
                {"ID_Ordine": 3, "ID_Veicolo": 3, "DataConsegna": "2023-11-01", "Stato": "Pianificata"}
            ]
            try:
                result = conn.execute(insert(consegne_table).values(consegne_data))
                conn.commit()
                print(f"Inserite {result.rowcount} consegne.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle consegne: {e}")

            # ManutenzioneRobot
            manutenzione_robot_table = get_table(metadata, "ManutenzioneRobot")
            manutenzione_robot_data = [
                {"ID_Robot": 1, "DataManutenzione": "2023-11-10", "Tipo": "Ispezione", "Stato": "Programmata", "Note": "Controllo generale"},
                {"ID_Robot": 2, "DataManutenzione": "2023-11-15", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Sostituzione batteria"},
                {"ID_Robot": 3, "DataManutenzione": "2023-11-20", "Tipo": "Sostituzione", "Stato": "Programmata", "Note": "Sostituzione motore"}
            ]
            try:
                result = conn.execute(insert(manutenzione_robot_table).values(manutenzione_robot_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni robot.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni robot: {e}")

            # ManutenzioneScaffalature
            manutenzione_scaffalature_table = get_table(metadata, "ManutenzioneScaffalature")
            manutenzione_scaffalature_data = [
                {"ID_Scaffalatura": 1, "DataManutenzione": "2023-11-05", "Tipo": "Ispezione", "Stato": "Programmata", "Note": "Verifica Bulloneria"},
                {"ID_Scaffalatura": 2, "DataManutenzione": "2023-11-08", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Sostituzione mensole"},
                {"ID_Scaffalatura": 3, "DataManutenzione": "2023-11-12", "Tipo": "Pulizia", "Stato": "Programmata", "Note": "Pulizia generale"}
            ]
            try:
                result = conn.execute(insert(manutenzione_scaffalature_table).values(manutenzione_scaffalature_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni scaffalature.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni scaffalature: {e}")

            # ManutenzioneZone
            manutenzione_zone_table = get_table(metadata, "ManutenzioneZone")
            manutenzione_zone_data = [
                {"ID_Zona": 1, "DataManutenzione": "2023-11-20", "Tipo": "Pulizia", "Stato": "Programmata", "Note": "Pulizia e sanificazione"},
                {"ID_Zona": 2, "DataManutenzione": "2023-11-25", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Riparazione illuminazione"},
                {"ID_Zona": 3, "DataManutenzione": "2023-11-30", "Tipo": "Ispezione", "Stato": "Programmata", "Note": "Ispezione generale"}
            ]
            try:
                result = conn.execute(insert(manutenzione_zone_table).values(manutenzione_zone_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni zone.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni zone: {e}")

            # ManutenzioneVeicoli
            manutenzione_veicoli_table = get_table(metadata, "ManutenzioneVeicoli")
            manutenzione_veicoli_data = [
                {"ID_Veicolo": 1, "DataManutenzione": "2023-11-12", "Tipo": "Ispezione", "Stato": "Programmata", "Note": "Controllo freni e livelli"},
                {"ID_Veicolo": 2, "DataManutenzione": "2023-11-18", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Sostituzione pneumatici"},
                {"ID_Veicolo": 3, "DataManutenzione": "2023-11-22", "Tipo": "Sostituzione", "Stato": "Programmata", "Note": "Sostituzione batteria"}
            ]
            try:
                result = conn.execute(insert(manutenzione_veicoli_table).values(manutenzione_veicoli_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni veicoli.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni veicoli: {e}")

            # Dipendenti
            import MagUtils
            id1= MagUtils.create_employee_id("RSSMRA80A01H501R", "Mario", "Rossi", "Amministratore", "2020-01-01")
            id2= MagUtils.create_employee_id("GLLGNN90B02H501Z", "Giovanni", "Gialli", "Operatore", "2021-02-01")
            id3= MagUtils.create_employee_id("VRDBRT85C03H501X", "Roberto", "Verdi", "Tecnico", "2022-03-01")
            dipendenti_table = get_table(metadata, "Dipendenti")
            dipendenti_data = [
                {"ID_Dipendente": id1, "CodiceFiscale": "RSSMRA80A01H501R", "Nome": "Mario", "Cognome": "Rossi", "Ruolo": "Amministratore", "Mansione": "Manager", "DataAssunzione": "2020-01-01"},
                {"ID_Dipendente": id2, "CodiceFiscale": "GLLGNN90B02H501Z", "Nome": "Giovanni", "Cognome": "Gialli", "Ruolo": "Operatore", "Mansione": "Magazziniere", "DataAssunzione": "2021-02-01"},
                {"ID_Dipendente": id3, "CodiceFiscale": "VRDBRT85C03H501X", "Nome": "Roberto", "Cognome": "Verdi", "Ruolo": "Tecnico", "Mansione": "Manutenzione", "DataAssunzione": "2022-03-01"}
            ]
            try:
                result = conn.execute(insert(dipendenti_table).values(dipendenti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} dipendenti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei dipendenti: {e}")

            # TurniDipendenti
            import MagUtils
            id1= MagUtils.create_employee_id("RSSMRA80A01H501R", "Mario", "Rossi", "Amministratore", "2020-01-01")
            id2= MagUtils.create_employee_id("GLLGNN90B02H501Z", "Giovanni", "Gialli", "Operatore", "2021-02-01")
            id3= MagUtils.create_employee_id("VRDBRT85C03H501X", "Roberto", "Verdi", "Tecnico", "2022-03-01")
            turni_table = get_table(metadata, "TurniDipendenti")
            turni_data = [
                {"ID_Dipendente": id1 , "DataInizio": "2023-10-27 09:00:00", "DataFine": "2023-10-27 18:00:00", "Mansione": "Manager"},
                {"ID_Dipendente": id2, "DataInizio": "2023-10-27 08:00:00", "DataFine": "2023-10-27 16:00:00", "Mansione": "Magazziniere"},
                {"ID_Dipendente": id3, "DataInizio": "2023-10-27 09:00:00", "DataFine": "2023-10-27 17:00:00", "Mansione": "Manutenzione"}
            ]
            try:
                result = conn.execute(insert(turni_table).values(turni_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} turni dipendenti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei turni: {e}")

def get_table_name(session, nome_tabella):
    """
    Restituisce il nome della tabella esistente nel database, indipendentemente dalle maiuscole/minuscole.

    Args:
        session: L'oggetto sessione SQLAlchemy.
        nome_tabella (str): Il nome della tabella da cercare.

    Returns:
        str: Il nome della tabella esistente nel database.
    """
    metadata = MetaData()
    metadata.reflect(bind=session.bind)
    table_names = metadata.tables.keys()
    for table_name in table_names:
        if table_name.lower() == nome_tabella.lower():
            return table_name
    return None

def add_recordSQL(session, nome_tabella, dati):
    """
    Aggiunge un nuovo record a una tabella.

    Args:
        session: L'oggetto sessione SQLAlchemy.
        nome_tabella (str): Il nome della tabella in cui inserire il record.
        dati (dict): Un dizionario che mappa i nomi delle colonne ai valori da inserire.

    Returns:
        bool: True se l'inserimento ha avuto successo, False in caso di errore.
    """
    try:
        table_name = get_table_name(session, nome_tabella)
        if not table_name:
            print(f"Errore: La tabella {nome_tabella} non esiste.")
            return False

        with session.begin():
            colonne = ", ".join(f"`{key}`" for key in dati.keys())
            valori = ", ".join(f":{key}" for key in dati.keys())
            sql = f"INSERT INTO `{table_name}` ({colonne}) VALUES ({valori})"
            session.execute(text(sql), dati)
        return True
    except Exception as e:
        session.rollback()
        print(f"Errore durante l'inserimento del record nella tabella {nome_tabella}: {e}")
        return False

def update_recordSQL(session, nome_tabella, dati_aggiornamento, condizione, args):
    """
    Aggiorna i record in una tabella in base a una condizione.

    Args:
        session: L'oggetto sessione SQLAlchemy.
        nome_tabella (str): Il nome della tabella da aggiornare.
        dati_aggiornamento (dict): Un dizionario dove le chiavi sono i nomi delle colonne e i valori sono i nuovi valori.
        condizione (str): La clausola SQL WHERE per specificare quali record aggiornare (es., "ID=5").

    Returns:
        int: Il numero di righe che sono state aggiornate.
        Restituisce False in caso di errore.
    """
    try:
        table_name = get_table_name(session, nome_tabella)
        if not table_name:
            print(f"Errore: La tabella {nome_tabella} non esiste.")
            return False

        with session.begin():
            set_clause = ", ".join([f"{key} = :{key}" for key in dati_aggiornamento])
            sql = f"UPDATE `{table_name}` SET {set_clause} WHERE {condizione}"
            result = session.execute(text(sql), dati_aggiornamento | args)
        return result.rowcount
    except Exception as e:
        session.rollback()
        print(f"Errore durante l'aggiornamento dalla tabella {nome_tabella}: {e}")
        return False

def delete_recordSQL(session, nome_tabella, condizione, args):
    """
    Elimina i record da una tabella in base a una condizione.

    Args:
        session: L'oggetto sessione SQLAlchemy.
        nome_tabella (str): Il nome della tabella da cui eliminare.
        condizione (str): La clausola SQL WHERE che specifica quali record eliminare (es., "ID = 5").

    Returns:
        int: Il numero di righe che sono state eliminate.
        Restituisce False in caso di errore.
    """
    try:
        table_name = get_table_name(session, nome_tabella)
        if not table_name:
            print(f"Errore: La tabella {nome_tabella} non esiste.")
            return False

        with session.begin():
            sql = f"DELETE FROM `{table_name}` WHERE {condizione}"
            result = session.execute(text(sql), args or {})
            rows_deleted = result.rowcount
        return rows_deleted if rows_deleted > 0 else 0
    except Exception as e:
        session.rollback()
        print(f"Errore durante l'eliminazione dalla tabella {nome_tabella}: {e}")
        return False

def select_recordsSQL(session, nome_tabella, colonne="*", condizione=None, args=None, ordina_per=None, limite=None):
    """
    Seleziona i record da una tabella in base a condizioni, ordinamento e limite opzionali.

    Args:
        session: L'oggetto sessione SQLAlchemy.
        nome_tabella (str): Il nome della tabella da cui selezionare.
        colonne (str, optional): Lista di colonne separate da virgola da selezionare. Default a * per selezionare tutte le colonne.
        condizione (str, optional): La clausola SQL WHERE (es., "ID > :id"). Default a None.
        args (dict, optional) : Dizionario di parametri
        ordina_per (str, optional): La clausola SQL ORDER BY (es., "Nome ASC"). Default a None.
        limite (int, optional): La clausola SQL LIMIT. Default a None.

    Returns:
        list: Una lista di dizionari, dove ogni dizionario rappresenta un record.
        Restituisce False in caso di errore.
    """
    try:
        table_name = get_table_name(session, nome_tabella)
        if not table_name:
            print(f"Errore: La tabella {nome_tabella} non esiste.")
            return False

        with session.begin():
            sql = f"SELECT {colonne} FROM `{table_name}`"
            if condizione:
                sql += f" WHERE {condizione}"
            if ordina_per:
                sql += f" ORDER BY {ordina_per}"
            if limite:
                sql += f" LIMIT {limite}"

            result = session.execute(text(sql), args or {})
            if result.returns_rows:
                column_names = result.keys()
                records = [dict(zip(column_names, row)) for row in result.fetchall()]
                return records
            else:
                return []
    except Exception as e:
        print(f"Errore durante la selezione dei record dalla tabella {nome_tabella}: {e}")
        return False

def Test_menu():
    while True:
        print("\nMenu di Test funzionalità:")
        print("1. Crea database se non esiste")
        print("2. Inizializza tabelle")
        print("3. Popola tabelle con dati di esempio")
        print("4. Aggiungi record")
        print("5. Aggiorna record")
        print("6. Elimina record")
        print("7. Seleziona record")
        print("8. Esci")

        choice = input("Inserisci la tua scelta: ")

        try:
            if choice == '1':
                create_database()
            elif choice == '2':
                initSQL()
            elif choice == '3':
                populateSQL()
            elif choice == '4':
                table_name = input("Nome della tabella: ")
                record_data = {}
                while True:
                    column_name = input("Nome colonna (o premi invio per terminare): ")
                    if not column_name:
                        break
                    value = input(f"Valore per {column_name}: ")
                    record_data[column_name] = value

                with connessione() as session:
                    success = add_recordSQL(session, table_name, record_data)
                    if success:
                        print(f"Record aggiunto alla tabella {table_name} con successo.")
                    else:
                        print(f"Errore nell'aggiunta del record alla tabella {table_name}. Controllare la presenza di errori nel log o verificare la correttezza dei dati inseriti.")
            elif choice == '5':
                table_name = input("Nome della tabella: ")
                update_data = {}
                condition_parts = []
                args = {}
                while True:
                    column_name = input("Nome colonna da aggiornare (o premi invio per terminare): ")
                    if not column_name:
                        break
                    value = input(f"Nuovo valore per {column_name}: ")
                    update_data[column_name] = value

                while True:
                    col_cond = input("Condizione per colonna (es. ID_Dipendente=:id, premi invio per terminare): ")
                    if not col_cond:
                        break
                    parts = col_cond.split("=")
                    if len(parts) == 2:
                        condition_parts.append(col_cond)
                        args[parts[1].replace(":", "")] = input(f"Valore per {parts[0].strip()}: ")

                condition = " AND ".join(condition_parts) if condition_parts else None
                if condition is None:
                    condition = input("Condizione WHERE (es. ID_Dipendente='TEC001', premi invio se nessuna condizione):")

                with connessione() as session:
                    rows_updated = update_recordSQL(session, table_name, update_data, condition, args)
                    if rows_updated:
                        print(f"Record aggiornato con successo. Righe aggiornate: {rows_updated}")
                    else:
                        print(f"Errore nell'aggiornamento del record nella tabella {table_name}.")
            elif choice == '6':
                table_name = input("Nome della tabella: ")
                condition_parts = []
                args = {}
                while True:
                    col_cond = input("Condizione per colonna (es. ID_Prodotto=:id, premi invio per terminare): ")
                    if not col_cond:
                        break
                    parts = col_cond.split("=")
                    if len(parts) == 2:
                        condition_parts.append(col_cond)
                        try:
                            args[parts[1].replace(":", "")] = int(input(f"Valore per {parts[0].strip()}: "))
                        except ValueError:
                            args[parts[1].replace(":", "")] = input(f"Valore per {parts[0].strip()}: ")

                condition = " AND ".join(condition_parts) if condition_parts else None
                if condition is None:
                    condition = input("Condizione WHERE (es. ID_Prodotto=1, premi invio se nessuna condizione): ")

                with connessione() as session:
                    rows_deleted = delete_recordSQL(session, table_name, condition, args)
                    if rows_deleted is False:
                        print(f"Errore nell'eliminazione dei record dalla tabella {table_name}.")
                    elif rows_deleted > 0:
                        print(f"Eliminati {rows_deleted} record dalla tabella {table_name}.")
                    else:
                        print(f"Nessun record eliminato dalla tabella {table_name}.")
            elif choice == '7':
                table_name = input("Nome della tabella: ")
                columns = input("Colonne da selezionare (separate da virgole, o * per tutte): ")
                condition = input("Condizione WHERE (opzionale, premi invio per nessuna condizione): ")
                order_by = input("Ordinamento ORDER BY (opzionale, premi invio per nessun ordinamento): ")
                limit = input("Limite LIMIT (opzionale, premi invio per nessun limite): ")

                args = {}
                if condition:
                    if ":id" in condition:
                        args["id"] = int(input("Inserisci l'ID: "))

                with connessione() as session:
                    results = select_recordsSQL(session, table_name, columns, condition, args, order_by, limit)
                    if results:
                        print("\nRisultati:")
                        for record in results:
                            print(record)
                    else:
                        print("Nessun risultato trovato.")
            elif choice == '8':
                print("Uscita dal programma. Arrivederci")
                break
            else:
                print("Scelta non valida.")
        except Exception as e:
            print(f"Errore imprevisto: {e}")
            
if __name__ == '__main__':
    Test_menu()