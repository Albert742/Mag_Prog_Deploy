import mariadb
import time

def connessione(**kwargs):
    """
    Connessione al database con configurazione tramite kwargs.
    """
    default_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '1234',
        'database': 'magazzino',
        'port': 3307
    }
    config = {**default_config, **kwargs}
    conn = mariadb.connect(**config)
    conn.auto_reconnect = True
    return conn

def query4db(conn, sql, args=None, commit=False, retry_count=3, retry_delay=1):
    """
    Esegue una query sul database.
    """
    for attempt in range(retry_count):
        try:
            with conn.cursor() as cursore:
                cursore.execute(sql, args or ())
                if commit:
                    conn.commit()
                    return cursore.lastrowid
            break
        except mariadb.OperationalError as e:
            if e.args[0] == 1205:  # Lock wait timeout exceeded
                time.sleep(retry_delay)
            else:
                raise
    else:
        raise mariadb.OperationalError("Failed to execute query after {} retries".format(retry_count))

def crea_tabella(conn, nome_tabella, definizione):
    """
    Crea una tabella nel database se non esiste.
    """
    sql = f"CREATE TABLE IF NOT EXISTS `{nome_tabella}` ({definizione})"
    return query4db(conn, sql, commit=True)


def inizializza(conn):
    tabelle = {
        # Gestione prodotti e fornitori
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
    }
    for nome_tabella, definizione in tabelle.items():
        crea_tabella(conn, nome_tabella, definizione)


def add_record(conn, table, fields, values):
    """
    Aggiunge un record a una tabella specificata.
    
    Args:
        conn: Oggetto connessione al database.
        table (str): Nome della tabella.
        fields (list): Lista dei nomi delle colonne in cui inserire i valori.
        values (list): Lista dei valori da inserire (nell'ordine corrispondente ai campi).
    
    Returns:
        bool: True se l'operazione è andata a buon fine, False altrimenti.
    """
    try:
        # Crea i placeholders per i valori
        placeholders = ', '.join(['%s'] * len(values))
        
        # Costruisce la query SQL
        sql = f"INSERT INTO `{table}` ({', '.join([f'`{field}`' for field in fields])}) VALUES ({placeholders})"
        
        # Esegue la query
        return query4db(conn, sql, args=values, commit=True)
    except Exception as e:
        print(f"Errore durante l'inserimento del record nella tabella {table}: {e}")
        return False


def createSQL():
    with connessione() as conn:
        inizializza(conn)

def populateSQL():
    """
    Popola il database con dati coerenti e pertinenti.
    """

    with connessione() as conn:
        pass
def alterSQL(table_name, column_name, column_type, position=None):
    """
    Aggiunge una colonna a una tabella esistente.
    """
    try:
        # Costruisce la query ALTER TABLE
        sql = f"ALTER TABLE `{table_name}` MODIFY `{column_name}` {column_type}"
        if position:
            sql += f" {position}"

        # Esegue la query
        with connessione() as conn:
            return query4db(conn, sql, commit=True)
    except Exception as e:
        print(f"Errore durante l'alterazione della tabella: {e}")
        return False

def dropSQL(tables, if_exists=True):
    """
    Elimina una o più tabelle dal database.
    """
    if isinstance(tables, str):
        tables = [tables]
    with connessione() as conn:
        query4db(conn, "SET FOREIGN_KEY_CHECKS = 0;", commit=True)
        for table_name in tables:
            sql = f"DROP TABLE IF EXISTS `{table_name}`;" if if_exists else f"DROP TABLE `{table_name}`;"
            query4db(conn, sql, commit=True)
    return query4db(conn, "SET FOREIGN_KEY_CHECKS = 1;", commit=True)

def selectSQL(table_name, columns="*", conditions=None):
    """
    Seleziona records da una tabella.
    
    """
    # Trasforma le colonne in stringa se è una lista
    if isinstance(columns, list):
        columns = ", ".join(columns)
    
    # Crea la query SQL
    sql = f"SELECT {columns} FROM {table_name}"
    if conditions:
        sql += f" WHERE {conditions}"
    
    try:
        # Gestisce la connessione al database
        with connessione() as conn:
            # Esegue la query e restituisce i risultati
            return query4db(conn, sql=sql, commit=False)
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {e}")
        return None

def updateSQL(table_name, column_name, value, conditions=None):
    """
    Aggiorna un record nella tabella.
    
    Args:
        table_name (str): Nome della tabella.
        column_name (str): Nome della colonna da aggiornare.
        value: Nuovo valore da assegnare alla colonna.
        conditions (str, optional): Clausola WHERE per filtrare i record da aggiornare.
    
    Returns:
        bool: True se l'operazione ha successo, False altrimenti.
    """
    try:
        # Costruisce la query SQL
        sql = f"UPDATE `{table_name}` SET `{column_name}` = %s"
        if conditions:
            sql += f" WHERE {conditions}"
        
        # Esegue la query con il valore specificato
        with connessione() as conn:
            return query4db(conn, sql, (value,), commit=True)
    except Exception as e:
        print(f"Errore durante l'aggiornamento della tabella: {e}")
        return False

def deleteSQL(table_name, conditions=None):
    """
    Elimina record dalla tabella.
    
    Args:
        table_name (str): Nome della tabella.
        conditions (str, optional): Clausola WHERE per filtrare i record da eliminare.
    
    Returns:
        bool: True se l'operazione ha successo, False altrimenti.
    """
    try:
        # Costruisce la query SQL
        sql = f"DELETE FROM `{table_name}`"
        if conditions:
            sql += f" WHERE {conditions}"
        
        # Esegue la query
        with connessione() as conn:
            return query4db(conn, sql, commit=True)
    except Exception as e:
        print(f"Errore durante l'eliminazione della tabella: {e}")
        return False
    
if __name__ == '__main__':
    #pass
    createSQL()
    #populateSQL()
    #askSQL()
    #alterSQL('Credenziali', 'Password', 'VARBINARY(60)')
    #dropSQL('ControlloQualitaMovimenti', if_exists=False)