from sqlalchemy import create_engine, text, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError
import time

def connessione(**kwargs):
    """
    Connessione al database con configurazione tramite kwargs usando SQLAlchemy.
    """
    default_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '1234',  # Replace with your actual password
        'database': 'magazzinov2',
        'port': 3307
    }
    config = {**default_config, **kwargs}

    connection_string = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

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


def query4db(session, sql, args=None, commit=False):
    """Esegue una query sul database usando SQLAlchemy."""
    try:
        result = session.execute(text(sql), args or {})
        if commit:
            session.commit()
            return result.lastrowid if result.lastrowid else True #handle insert vs. other queries
        return result
    except IntegrityError as e:
        session.rollback()  #Handle unique constraint violations etc.
        print(f"Integrity Error: {e}")
        return False
    except Exception as e:
        session.rollback()
        print(f"Errore durante l'esecuzione della query: {e}")
        return False



def crea_tabella(session, nome_tabella, definizione):
    """Crea una tabella nel database se non esiste."""
    sql = f"CREATE TABLE IF NOT EXISTS `{nome_tabella}` ({definizione})"
    return query4db(session, sql, commit=True)


def inizializza(session):
    tabelle = {
        "Fornitori": """
            ID_Fornitore INT PRIMARY KEY AUTO_INCREMENT,
            Nome VARCHAR(255) NOT NULL,
            Indirizzo VARCHAR(255),
            Telefono VARCHAR(20),
            Email VARCHAR(255),
            PartitaIVA VARCHAR(20) UNIQUE NOT NULL
        """,
        "Prodotti": """
            ID_Prodotto INT PRIMARY KEY AUTO_INCREMENT,
            ID_Fornitore INT,
            Nome VARCHAR(255) NOT NULL,
            Produttore VARCHAR(255),
            Tipo ENUM('Alimentare', 'Farmaceutico') NOT NULL,
            UnitaMisura VARCHAR(50),
            UNIQUE(Nome, Produttore),
            FOREIGN KEY (ID_Fornitore) REFERENCES Fornitori(ID_Fornitore) ON DELETE SET NULL
        """,
        # Gestione magazzino e lotti
        "Zone": """
            ID_Zona INT PRIMARY KEY AUTO_INCREMENT,
            Nome VARCHAR(255) NOT NULL,
            Tipo ENUM('Stoccaggio_Alimentari', 'Stoccaggio_Farmaceutici', 'Carico', 'Scarico') NOT NULL,
            Descrizione TEXT
        """,
        "Scaffalature": """
            ID_Scaffalatura INT PRIMARY KEY AUTO_INCREMENT,
            ID_Zona INT NOT NULL,
            Nome VARCHAR(255) NOT NULL,
            Capacita INT,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE
        """,
        "Lotti": """
            ID_Lotto INT PRIMARY KEY AUTO_INCREMENT,
            ID_Prodotto INT NOT NULL,
            ID_Zona INT NOT NULL,
            ID_Scaffalatura INT NOT NULL,
            Lotto VARCHAR(255),
            Scadenza DATE,
            Quantita INT,
            PrezzoAcquisto DECIMAL(10, 2),
            DataRicevimento DATE,
            Stato ENUM('Disponibile', 'In transito', 'Prenotato') DEFAULT 'Disponibile',
            FOREIGN KEY (ID_Prodotto) REFERENCES Prodotti(ID_Prodotto) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Scaffalatura) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE,
            UNIQUE (ID_Prodotto, Lotto)
        """,
        # Gestione clienti e ordini
        "Clienti": """
            ID_Cliente INT PRIMARY KEY AUTO_INCREMENT,
            Nome VARCHAR(255) NOT NULL,
            Indirizzo VARCHAR(255),
            Telefono VARCHAR(20),
            Email VARCHAR(255),
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
        # Gestione baie di carico/scarico e sensori
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
            Valore FLOAT,
            DataLettura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE SET NULL
        """,
        # Gestione robot
        "StazioneRicarica": """
            ID_Ricarica INT PRIMARY KEY AUTO_INCREMENT,
            ZonaID INT NOT NULL,
            Nome VARCHAR(255) NOT NULL,
            Stato ENUM('Libera', 'Occupata', 'Manutenzione') DEFAULT 'Libera',
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
            ID_Zona_Destinazione INT NOT NULL,
            ID_Scaffalatura_Destinazione INT NOT NULL,
            Priorita INT DEFAULT 1,
            Stato ENUM('In attesa', 'Assegnata', 'Completata', 'Annullata') DEFAULT 'In attesa',
            ID_Robot INT,
            DataRichiesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            DataCompletamento TIMESTAMP,
            FOREIGN KEY (ID_Lotto) REFERENCES Lotti(ID_Lotto) ON DELETE CASCADE,
            FOREIGN KEY (ID_Robot) REFERENCES Robot(ID_Robot) ON DELETE SET NULL,
            FOREIGN KEY (ID_Zona_Destinazione) REFERENCES Zone(ID_Zona) ON DELETE CASCADE,
            FOREIGN KEY (ID_Scaffalatura_Destinazione) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE
        """,
        "StoricoMovimentiMagazzino": """
            ID_Movimento INT PRIMARY KEY AUTO_INCREMENT,
            ID_Lotto INT NOT NULL,
            DataMovimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            TipoMovimento ENUM('Entrata', 'Uscita', 'Spostamento') NOT NULL,
            Quantita INT,
            ID_Zona_Partenza INT,
            ID_Zona_Arrivo INT,
            FOREIGN KEY (ID_Lotto) REFERENCES Lotti(ID_Lotto) ON DELETE CASCADE,
            FOREIGN KEY (ID_Zona_Partenza) REFERENCES Zone(ID_Zona) ON DELETE SET NULL,
            FOREIGN KEY (ID_Zona_Arrivo) REFERENCES Zone(ID_Zona) ON DELETE SET NULL
        """,
        "ControlloQualitaMovimenti": """
            ID_Controllo INT PRIMARY KEY AUTO_INCREMENT,
            ID_Richiesta INT NOT NULL,
            ID_Robot INT NOT NULL,
            Esito ENUM('Successo', 'Fallimento') NOT NULL,
            Note TEXT,
            DataControllo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ID_Richiesta) REFERENCES RichiesteMovimento(ID_Richiesta) ON DELETE CASCADE,
            FOREIGN KEY (ID_Robot) REFERENCES Robot(ID_Robot) ON DELETE CASCADE
        """,
        # Gestione veicoli e consegne
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
        # Gestione manutenzione
        "ManutenzioneRobot": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Robot INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo VARCHAR(255) NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Robot) REFERENCES Robot(ID_Robot) ON DELETE CASCADE
        """,
        "ManutenzioneScaffalature": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Scaffalatura INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo VARCHAR(255) NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Scaffalatura) REFERENCES Scaffalature(ID_Scaffalatura) ON DELETE CASCADE
        """,
        "ManutenzioneZone": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Zona INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo VARCHAR(255) NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Zona) REFERENCES Zone(ID_Zona) ON DELETE CASCADE
        """,
        "ManutenzioneVeicoli": """
            ID_Manutenzione INT PRIMARY KEY AUTO_INCREMENT,
            ID_Veicolo INT NOT NULL,
            DataManutenzione DATE NOT NULL,
            Tipo VARCHAR(255) NOT NULL,
            Stato ENUM('Programmata', 'Completata', 'Annullata') DEFAULT 'Programmata',
            Note TEXT,
            FOREIGN KEY (ID_Veicolo) REFERENCES Veicoli(ID_Veicolo) ON DELETE CASCADE
        """,
        # Gestione personale e accesso
        "Dipendenti": """
            ID_Dipendente VARCHAR(10) PRIMARY KEY,
            CodiceFiscale VARCHAR(16) NOT NULL UNIQUE,
            Nome VARCHAR(255) NOT NULL,
            Cognome VARCHAR(255) NOT NULL,
            Ruolo ENUM('Amministratore', 'Operatore', 'Tecnico') NOT NULL,
            Mansione ENUM('Amministratore', 'Tecnico', 'Manutenzione', 'Magazziniere', 'Responsabile Magazzino', 'Addetto Carico/Scarico', 'Operatore Logistico', 'Coordinatore Magazzino', 'Pianificatore', 'Controllo Qualità') NOT NULL,
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
        "AccessiUtenti": """
            ID_Accesso INT PRIMARY KEY AUTO_INCREMENT,
            ID_Utente INT NOT NULL,
            DataOra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            Esito ENUM('Successo', 'Fallito') NOT NULL,
            IP VARCHAR(255),
            FOREIGN KEY (ID_Utente) REFERENCES Credenziali(ID_Utente) ON DELETE CASCADE
        """,
        "LogEventi": """
            ID_Log INT PRIMARY KEY AUTO_INCREMENT,
            DataOra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ID_Utente INT,
            Azione VARCHAR(255) NOT NULL,
            Dettagli TEXT,
            FOREIGN KEY (ID_Utente) REFERENCES Credenziali(ID_Utente) ON DELETE SET NULL
        """,

        # Add other tables here...
    }
    for nome_tabella, definizione in tabelle.items():
        crea_tabella(session, nome_tabella, definizione)


def add_record(session, table, fields, values):
    """Aggiunge un record a una tabella specificata."""
    try:
        sql = f"INSERT INTO `{table}` ({', '.join([f'`{field}`' for field in fields])}) VALUES ({', '.join(['%s'] * len(values))})"
        return query4db(session, sql, values, commit=True)
    except Exception as e:
        print(f"Errore durante l'inserimento del record nella tabella {table}: {e}")
        return False


def createSQL():
    with connessione() as conn:
        if conn:
            inizializza(conn)


def populateSQL():
    with connessione() as conn:
        if conn:
            # Fornitori
            fornitori_data = [
                {"nome": "Fornitore A", "indirizzo": "Via Roma 1, Milano", "telefono": "0212345678", "email": "fornitoreA@email.com", "partitaiva": "IT12345678901"},
                {"nome": "Fornitore B", "indirizzo": "Corso Italia 2, Roma", "telefono": "0698765432", "email": "fornitoreB@email.com", "partitaiva": "IT98765432109"},
                {"nome": "Fornitore C", "indirizzo": "Piazza Verdi 3, Napoli", "telefono": "0815554433", "email": "fornitoreC@email.com", "partitaiva": "IT11223344556"},
                {"nome": "Fornitore D", "indirizzo": "Via Dante 4, Torino", "telefono": "0116667788", "email": "fornitoreD@email.com", "partitaiva": "IT66554433221"},
                {"nome": "Fornitore E", "indirizzo": "Via Garibaldi 5, Palermo", "telefono": "0917778899", "email": "fornitoreE@email.com", "partitaiva": "IT22334455667"},
            ]
            try:
                result = conn.execute(insert("Fornitori").values(fornitori_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} fornitori.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei fornitori: {e}")

            # Prodotti
            prodotti_data = [
                {"ID_Fornitore": 1, "Nome": "Pasta di Grano Duro", "Produttore": "Pastificio Italia", "Tipo": "Alimentare", "UnitaMisura": "kg"},
                {"ID_Fornitore": 1, "Nome": "Olio Extra Vergine di Oliva", "Produttore": "Oleificio Sole", "Tipo": "Alimentare", "UnitaMisura": "l"},
                {"ID_Fornitore": 2, "Nome": "Paracetamolo 500mg", "Produttore": "Farmaceutica ABC", "Tipo": "Farmaceutico", "UnitaMisura": "compresse"},
                {"ID_Fornitore": 2, "Nome": "Aspirina 100mg", "Produttore": "Farmaceutica XYZ", "Tipo": "Farmaceutico", "UnitaMisura": "compresse"},
                {"ID_Fornitore": 3, "Nome": "Biscotti Frollini", "Produttore": "Biscottificio Dolce", "Tipo": "Alimentare", "UnitaMisura": "kg"},
                {"ID_Fornitore": 3, "Nome": "Sciroppo per la Tosse", "Produttore": "Farmaceutica ABC", "Tipo": "Farmaceutico", "UnitaMisura": "ml"},
                {"ID_Fornitore": 4, "Nome": "Riso Carnaroli", "Produttore": "Riseria Bella", "Tipo": "Alimentare", "UnitaMisura": "kg"},
                {"ID_Fornitore": 4, "Nome": "Vitamina C 1000mg", "Produttore": "Integratori Plus", "Tipo": "Farmaceutico", "UnitaMisura": "capsule"},
                {"ID_Fornitore": 5, "Nome": "Caffè Macinato", "Produttore": "Caffè Aroma", "Tipo": "Alimentare", "UnitaMisura": "kg"},
                {"ID_Fornitore": 5, "Nome": "Ibuprofene 400mg", "Produttore": "Farmaceutica XYZ", "Tipo": "Farmaceutico", "UnitaMisura": "compresse"}
            ]
            try:
                result = conn.execute(insert("Prodotti").values(prodotti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} prodotti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei prodotti: {e}")

            # Zone
            zone_data = [
                {"Nome": "Stoccaggio Alimentari", "Tipo": "Stoccaggio_Alimentari", "Descrizione": "Zona di stoccaggio per prodotti alimentari"},
                {"Nome": "Stoccaggio Farmaceutici", "Tipo": "Stoccaggio_Farmaceutici", "Descrizione": "Zona di stoccaggio per prodotti farmaceutici"},
                {"Nome": "Baia di Carico", "Tipo": "Carico", "Descrizione": "Zona per il carico delle merci"},
                {"Nome": "Baia di Scarico", "Tipo": "Scarico", "Descrizione": "Zona per lo scarico delle merci"}
            ]
            try:
                result = conn.execute(insert("Zone").values(zone_data))
                conn.commit()
                print(f"Inserite {result.rowcount} zone.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle zone: {e}")

            # Scaffalature
            scaffalature_data = [
                {"ID_Zona": 1, "Nome": "Scaffale A1", "Capacita": 100},
                {"ID_Zona": 1, "Nome": "Scaffale A2", "Capacita": 80},
                {"ID_Zona": 2, "Nome": "Scaffale B1", "Capacita": 150},
                {"ID_Zona": 2, "Nome": "Scaffale B2", "Capacita": 120},
                {"ID_Zona": 3, "Nome": "Scaffale C1", "Capacita": 50},
                {"ID_Zona": 4, "Nome": "Scaffale D1", "Capacita": 60}
            ]
            try:
                result = conn.execute(insert("Scaffalature").values(scaffalature_data))
                conn.commit()
                print(f"Inserite {result.rowcount} scaffalature.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle scaffalature: {e}")


            # Lotti
            lotti_data = [
                {"ID_Prodotto": 1, "ID_Zona": 1, "ID_Scaffalatura": 1, "Lotto": "Lotto001", "Scadenza": "2024-12-31", "Quantita": 500, "PrezzoAcquisto": 1.50, "DataRicevimento": "2023-01-15", "Stato": "Disponibile"},
                {"ID_Prodotto": 1, "ID_Zona": 1, "ID_Scaffalatura": 2, "Lotto": "Lotto002", "Scadenza": "2025-01-31", "Quantita": 300, "PrezzoAcquisto": 1.60, "DataRicevimento": "2023-02-20", "Stato": "Disponibile"},
                {"ID_Prodotto": 2, "ID_Zona": 2, "ID_Scaffalatura": 3, "Lotto": "Lotto003", "Scadenza": "2024-06-30", "Quantita": 1000, "PrezzoAcquisto": 0.15, "DataRicevimento": "2023-03-25", "Stato": "Disponibile"},
                {"ID_Prodotto": 2, "ID_Zona": 2, "ID_Scaffalatura": 4, "Lotto": "Lotto004", "Scadenza": "2024-07-31", "Quantita": 800, "PrezzoAcquisto": 0.20, "DataRicevimento": "2023-04-10", "Stato": "Disponibile"},
                {"ID_Prodotto": 3, "ID_Zona": 1, "ID_Scaffalatura": 1, "Lotto": "Lotto005", "Scadenza": "2024-11-30", "Quantita": 750, "PrezzoAcquisto": 2.50, "DataRicevimento": "2023-05-01", "Stato": "Disponibile"},
                {"ID_Prodotto": 3, "ID_Zona": 2, "ID_Scaffalatura": 3, "Lotto": "Lotto006", "Scadenza": "2024-10-31", "Quantita": 900, "PrezzoAcquisto": 0.25, "DataRicevimento": "2023-06-05", "Stato": "Disponibile"},
                {"ID_Prodotto": 4, "ID_Zona": 1, "ID_Scaffalatura": 1, "Lotto": "Lotto007", "Scadenza": "2025-02-28", "Quantita": 400, "PrezzoAcquisto": 2.00, "DataRicevimento": "2023-07-10", "Stato": "Disponibile"},
                {"ID_Prodotto": 4, "ID_Zona": 2, "ID_Scaffalatura": 4, "Lotto": "Lotto008", "Scadenza": "2025-03-31", "Quantita": 600, "PrezzoAcquisto": 0.30, "DataRicevimento": "2023-08-15", "Stato": "Disponibile"},
                {"ID_Prodotto": 5, "ID_Zona": 1, "ID_Scaffalatura": 2, "Lotto": "Lotto009", "Scadenza": "2025-05-31", "Quantita": 200, "PrezzoAcquisto": 5.00, "DataRicevimento": "2023-09-20", "Stato": "Disponibile"},
                {"ID_Prodotto": 5, "ID_Zona": 2, "ID_Scaffalatura": 3, "Lotto": "Lotto010", "Scadenza": "2025-04-30", "Quantita": 1000, "PrezzoAcquisto": 0.40, "DataRicevimento": "2023-10-01", "Stato": "Disponibile"}
            ]
            try:
                result = conn.execute(insert("Lotti").values(lotti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} lotti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei lotti: {e}")

            # Clienti
            clienti_data = [
                {"Nome": "Cliente X", "Indirizzo": "Via Verdi 10, Milano", "Telefono": "0212345679", "Email": "clienteX@email.com", "PartitaIVA": "IT11122233344"},
                {"Nome": "Cliente Y", "Indirizzo": "Piazza Roma 20, Roma", "Telefono": "0698765433", "Email": "clienteY@email.com", "PartitaIVA": "IT55566677788"},
                {"Nome": "Cliente Z", "Indirizzo": "Via Napoli 30, Napoli", "Telefono": "0815554434", "Email": "clienteZ@email.com", "PartitaIVA": "IT99900011122"}
            ]
            try:
                result = conn.execute(insert("Clienti").values(clienti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} clienti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei clienti: {e}")


            # Ordini
            ordini_data = [
                {"DataOrdine": "2023-10-27 10:00:00", "Tipo": "Entrata", "ID_Fornitore": 1, "ID_Cliente": None, "Stato": "Concluso"},
                {"DataOrdine": "2023-10-28 11:30:00", "Tipo": "Uscita", "ID_Fornitore": None, "ID_Cliente": 1, "Stato": "Spedito"},
                {"DataOrdine": "2023-10-29 12:00:00", "Tipo": "Entrata", "ID_Fornitore": 2, "ID_Cliente": None, "Stato": "Concluso"},
                {"DataOrdine": "2023-10-30 10:00:00", "Tipo": "Uscita", "ID_Fornitore": None, "ID_Cliente": 2, "Stato": "In elaborazione"},
                {"DataOrdine": "2023-10-31 12:00:00", "Tipo": "Entrata", "ID_Fornitore": 3, "ID_Cliente": None, "Stato": "In elaborazione"},
                {"DataOrdine": "2023-11-01 10:00:00", "Tipo": "Uscita", "ID_Fornitore": None, "ID_Cliente": 3, "Stato": "In elaborazione"}
            ]
            try:
                result = conn.execute(insert("Ordini").values(ordini_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} ordini.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento degli ordini: {e}")

            # DettagliOrdini
            dettagli_ordini_data = [
                {"ID_Ordine": 1, "ID_Lotto": 1, "Quantita": 200},
                {"ID_Ordine": 1, "ID_Lotto": 2, "Quantita": 100},
                {"ID_Ordine": 2, "ID_Lotto": 3, "Quantita": 500},
                {"ID_Ordine": 3, "ID_Lotto": 4, "Quantita": 1000},
                {"ID_Ordine": 4, "ID_Lotto": 5, "Quantita": 200},
                {"ID_Ordine": 5, "ID_Lotto": 6, "Quantita": 500},
                {"ID_Ordine": 6, "ID_Lotto": 7, "Quantita": 700},
                {"ID_Ordine": 6, "ID_Lotto": 8, "Quantita": 900},
            ]
            try:
                result = conn.execute(insert("DettagliOrdini").values(dettagli_ordini_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} dettagli ordini.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei dettagli ordini: {e}")

            # BaieCaricoScarico
            baie_data = [
                {"ZonaID": 3, "Nome": "Baia Carico 1", "Tipo": "Carico", "Stato": "Libera"},
                {"ZonaID": 4, "Nome": "Baia Scarico 1", "Tipo": "Scarico", "Stato": "Libera"}
            ]
            try:
                result = conn.execute(insert("BaieCaricoScarico").values(baie_data))
                conn.commit()
                print(f"Inserite {result.rowcount} baie.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle baie: {e}")

            # Sensori
            sensori_data = [
                {"Tipo": "Presenza", "ID_Zona": 1, "Valore": 1},
                {"Tipo": "Temperatura", "ID_Zona": 1, "Valore": 25.5},
                {"Tipo": "Umidità", "ID_Zona": 1, "Valore": 50.2}
            ]
            try:
                result = conn.execute(insert("Sensori").values(sensori_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} sensori.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei sensori: {e}")

            # StazioneRicarica
            stazioni_ricarica_data = [
                {"ZonaID": 1, "Nome": "Stazione Ricarica 1", "Stato": "Libera"}
            ]
            try:
                result = conn.execute(insert("StazioneRicarica").values(stazioni_ricarica_data))
                conn.commit()
                print(f"Inserite {result.rowcount} stazioni di ricarica.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle stazioni di ricarica: {e}")

            # Robot
            robot_data = [
                {"ID_Sensore": 1, "ID_Zona": 1, "Nome": "Robot A", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale A1", "Capacita": 100, "ID_Ricarica": 1},
                {"ID_Sensore": 2, "ID_Zona": 1, "Nome": "Robot B", "Stato": "Disponibile", "PosizioneAttuale": "Scaffale A2", "Capacita": 120, "ID_Ricarica": 1}
            ]
            try:
                result = conn.execute(insert("Robot").values(robot_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} robot.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei robot: {e}")

            # RichiesteMovimento
            richieste_movimento_data = [
                {"ID_Lotto": 1, "ID_Zona_Destinazione": 2, "ID_Scaffalatura_Destinazione": 1, "Priorita": 1, "Stato": "Completata", "ID_Robot": 1, "DataRichiesta": "2023-10-27 10:00:00", "DataCompletamento": "2023-10-27 10:15:00"},
                {"ID_Lotto": 2, "ID_Zona_Destinazione": 1, "ID_Scaffalatura_Destinazione": 2, "Priorita": 1, "Stato": "Completata", "ID_Robot": 2, "DataRichiesta": "2023-10-28 11:30:00", "DataCompletamento": "2023-10-28 11:45:00"},
                {"ID_Lotto": 3, "ID_Zona_Destinazione": 1, "ID_Scaffalatura_Destinazione": 1, "Priorita": 2, "Stato": "In attesa", "ID_Robot": None, "DataRichiesta": "2023-10-29 12:00:00", "DataCompletamento": None}
            ]
            try:
                result = conn.execute(insert("RichiesteMovimento").values(richieste_movimento_data))
                conn.commit()
                print(f"Inserite {result.rowcount} richieste di movimento.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle richieste di movimento: {e}")

            # StoricoMovimentiMagazzino
            storico_movimenti_data = [
                {"ID_Lotto": 1, "DataMovimento": "2023-10-27 10:15:00", "TipoMovimento": "Spostamento", "Quantita": 200, "ID_Zona_Partenza": 1, "ID_Zona_Arrivo": 2},
                {"ID_Lotto": 2, "DataMovimento": "2023-10-28 11:45:00", "TipoMovimento": "Spostamento", "Quantita": 100, "ID_Zona_Partenza": 2, "ID_Zona_Arrivo": 1}
            ]
            try:
                result = conn.execute(insert("StoricoMovimentiMagazzino").values(storico_movimenti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} movimenti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dello storico movimenti: {e}")

            # ControlloQualitaMovimenti
            controllo_qualita_data = [
                {"ID_Richiesta": 1, "ID_Robot": 1, "Esito": "Successo", "Note": "Controllo ok", "DataControllo": "2023-10-27 10:15:00"},
                {"ID_Richiesta": 2, "ID_Robot": 2, "Esito": "Successo", "Note": "Controllo ok", "DataControllo": "2023-10-28 11:45:00"}
            ]
            try:
                result = conn.execute(insert("ControlloQualitaMovimenti").values(controllo_qualita_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} controlli qualità.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei controlli qualità: {e}")

            # Veicoli
            veicoli_data = [
                {"Tipo": "Bilico", "Capacita": 10000, "Stato": "Disponibile", "Targa": "AA123BB"},
                {"Tipo": "Furgone", "Capacita": 2000, "Stato": "Disponibile", "Targa": "CC456DD"},
                {"Tipo": "Carrello_Elevatore", "Capacita": 500, "Stato": "Disponibile", "Targa": "EE789FF"}
            ]
            try:
                result = conn.execute(insert("Veicoli").values(veicoli_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} veicoli.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei veicoli: {e}")

            # Consegne
            consegne_data = [
                {"ID_Ordine": 2, "ID_Veicolo": 1, "DataConsegna": "2023-10-28", "Stato": "Completata"},
                {"ID_Ordine": 3, "ID_Veicolo": 2, "DataConsegna": "2023-10-30", "Stato": "In corso"}
            ]
            try:
                result = conn.execute(insert("Consegne").values(consegne_data))
                conn.commit()
                print(f"Inserite {result.rowcount} consegne.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle consegne: {e}")

            # ManutenzioneRobot
            manutenzione_robot_data = [
                {"ID_Robot": 1, "DataManutenzione": "2023-11-10", "Tipo": "Ordinaria", "Stato": "Programmata", "Note": "Controllo generale"},
                {"ID_Robot": 2, "DataManutenzione": "2023-11-15", "Tipo": "Straordinaria", "Stato": "Programmata", "Note": "Sostituzione batteria"}
            ]
            try:
                result = conn.execute(insert("ManutenzioneRobot").values(manutenzione_robot_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni robot.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni robot: {e}")

            # ManutenzioneScaffalature
            manutenzione_scaffalature_data = [
                {"ID_Scaffalatura": 1, "DataManutenzione": "2023-11-05", "Tipo": "Controllo", "Stato": "Programmata", "Note": "Verifica Bulloneria"},
                {"ID_Scaffalatura": 2, "DataManutenzione": "2023-11-08", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Sostituzione mensole"}
            ]
            try:
                result = conn.execute(insert("ManutenzioneScaffalature").values(manutenzione_scaffalature_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni scaffalature.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni scaffalature: {e}")

            # ManutenzioneZone
            manutenzione_zone_data = [
                {"ID_Zona": 1, "DataManutenzione": "2023-11-20", "Tipo": "Pulizia", "Stato": "Programmata", "Note": "Pulizia e sanificazione"},
                {"ID_Zona": 2, "DataManutenzione": "2023-11-25", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Riparazione illuminazione"}
            ]
            try:
                result = conn.execute(insert("ManutenzioneZone").values(manutenzione_zone_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni zone.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni zone: {e}")

            # ManutenzioneVeicoli
            manutenzione_veicoli_data = [
                {"ID_Veicolo": 1, "DataManutenzione": "2023-11-12", "Tipo": "Controllo", "Stato": "Programmata", "Note": "Controllo freni e livelli"},
                {"ID_Veicolo": 2, "DataManutenzione": "2023-11-18", "Tipo": "Riparazione", "Stato": "Programmata", "Note": "Sostituzione pneumatici"}
            ]
            try:
                result = conn.execute(insert("ManutenzioneVeicoli").values(manutenzione_veicoli_data))
                conn.commit()
                print(f"Inserite {result.rowcount} manutenzioni veicoli.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento delle manutenzioni veicoli: {e}")

            # Dipendenti
            dipendenti_data = [
                {"ID_Dipendente": "ADM001", "CodiceFiscale": "RSSMRA80A01H501R", "Nome": "Mario", "Cognome": "Rossi", "Ruolo": "Amministratore", "Mansione": "Amministratore", "DataAssunzione": "2020-01-01"},
                {"ID_Dipendente": "OPR001", "CodiceFiscale": "GLLGNN90B02H501Z", "Nome": "Giovanni", "Cognome": "Gialli", "Ruolo": "Operatore", "Mansione": "Magazziniere", "DataAssunzione": "2021-02-01"},
                {"ID_Dipendente": "TEC001", "CodiceFiscale": "VRDBRT85C03H501X", "Nome": "Roberto", "Cognome": "Verdi", "Ruolo": "Tecnico", "Mansione": "Manutenzione", "DataAssunzione": "2022-03-01"}
            ]
            try:
                result = conn.execute(insert("Dipendenti").values(dipendenti_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} dipendenti.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei dipendenti: {e}")

            # TurniDipendenti
            turni_data = [
                {"ID_Dipendente": "ADM001", "DataInizio": "2023-10-27 09:00:00", "DataFine": "2023-10-27 18:00:00", "Mansione": "Amministratore"},
                {"ID_Dipendente": "OPR001", "DataInizio": "2023-10-27 08:00:00", "DataFine": "2023-10-27 16:00:00", "Mansione": "Magazziniere"},
                {"ID_Dipendente": "TEC001", "DataInizio": "2023-10-27 09:00:00", "DataFine": "2023-10-27 17:00:00", "Mansione": "Manutenzione"}
            ]
            try:
                result = conn.execute(insert("TurniDipendenti").values(turni_data))
                conn.commit()
                print(f"Inseriti {result.rowcount} turni.")
            except Exception as e:
                conn.rollback()
                print(f"Errore durante l'inserimento dei turni: {e}")


def alterSQL(session, table_name, column_name, column_type, position=None):
    """Aggiunge una colonna a una tabella esistente."""
    try:
        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {column_type}"
        if position:
            sql += f" {position}"
        return query4db(session, sql, commit=True)
    except Exception as e:
        print(f"Errore durante l'alterazione della tabella: {e}")
        return False


def dropSQL(session, tables, if_exists=True):
    """Elimina una o più tabelle dal database."""
    if isinstance(tables, str):
        tables = [tables]
    try:
        query4db(session, "SET FOREIGN_KEY_CHECKS = 0;", commit=True)
        for table_name in tables:
            sql = f"DROP TABLE IF EXISTS `{table_name}`" if if_exists else f"DROP TABLE `{table_name}`"
            query4db(session, sql, commit=True)
        return query4db(session, "SET FOREIGN_KEY_CHECKS = 1;", commit=True)
    except Exception as e:
        print(f"Errore durante la drop delle tabelle: {e}")
        return False

def selectSQL(session, table_name, columns="*", conditions=None):
    """Seleziona records da una tabella."""
    if isinstance(columns, list):
        columns = ", ".join(columns)
    sql = f"SELECT {columns} FROM {table_name}"
    if conditions:
        sql += f" WHERE {conditions}"
    return query4db(session, sql)


def updateSQL(session, table_name, updates, conditions=None):  #Improved update
    """Aggiorna un record nella tabella."""
    try:
        set_clause = ", ".join([f"`{k}` = %s" for k in updates.keys()])
        sql = f"UPDATE `{table_name}` SET {set_clause}"
        if conditions:
            sql += f" WHERE {conditions}"
        values = list(updates.values())
        return query4db(session, sql, values, commit=True)
    except Exception as e:
        print(f"Errore durante l'aggiornamento della tabella: {e}")
        return False


def deleteSQL(session, table_name, conditions=None):
    """Elimina record dalla tabella."""
    try:
        sql = f"DELETE FROM `{table_name}`"
        if conditions:
            sql += f" WHERE {conditions}"
        return query4db(session, sql, commit=True)
    except Exception as e:
        print(f"Errore durante l'eliminazione dalla tabella: {e}")
        return False


if __name__ == '__main__':
    #pass
    #createSQL()
    populateSQL()