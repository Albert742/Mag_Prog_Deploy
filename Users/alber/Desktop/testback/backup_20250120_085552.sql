CREATE TABLE `baiecaricoscarico` (
  `ID_Baia` int(11) NOT NULL AUTO_INCREMENT,
  `ZonaID` int(11) NOT NULL,
  `Nome` varchar(255) NOT NULL,
  `Tipo` enum('Carico','Scarico') NOT NULL,
  `Stato` enum('Libera','Occupata','Manutenzione') DEFAULT 'Libera',
  PRIMARY KEY (`ID_Baia`),
  UNIQUE KEY `ZonaID` (`ZonaID`,`Nome`),
  CONSTRAINT `baiecaricoscarico_ibfk_1` FOREIGN KEY (`ZonaID`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO baiecaricoscarico VALUES ('1', '3', 'Baia Carico 1', 'Carico', 'Libera');
INSERT INTO baiecaricoscarico VALUES ('2', '3', 'Baia Carico 2', 'Carico', 'Libera');
INSERT INTO baiecaricoscarico VALUES ('3', '4', 'Baia Scarico 1', 'Scarico', 'Libera');
INSERT INTO baiecaricoscarico VALUES ('4', '4', 'Baia Scarico 2', 'Scarico', 'Libera');

CREATE TABLE `clienti` (
  `ID_Cliente` int(11) NOT NULL AUTO_INCREMENT,
  `Nome` varchar(255) NOT NULL,
  `Indirizzo` varchar(255) DEFAULT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `PartitaIVA` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_Cliente`),
  UNIQUE KEY `PartitaIVA` (`PartitaIVA`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO clienti VALUES ('1', 'Cliente X', 'Via Verdi 10, Milano', '0212345679', 'clienteX@email.com', 'IT11122233344');
INSERT INTO clienti VALUES ('2', 'Cliente Y', 'Piazza Roma 20, Roma', '0698765433', 'clienteY@email.com', 'IT55566677788');
INSERT INTO clienti VALUES ('3', 'Cliente Z', 'Corso Italia 15, Napoli', '0812345678', 'clienteZ@email.com', 'IT99988877766');
INSERT INTO clienti VALUES ('4', 'Cliente W', 'Via Garibaldi 5, Torino', '0112345678', 'clienteW@email.com', 'IT44433322211');
INSERT INTO clienti VALUES ('5', 'Cliente V', 'Piazza Duomo 1, Firenze', '0552345678', 'clienteV@email.com', 'IT33322211100');

CREATE TABLE `consegne` (
  `ID_Consegna` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Ordine` int(11) NOT NULL,
  `ID_Veicolo` int(11) DEFAULT NULL,
  `DataConsegna` date DEFAULT NULL,
  `Stato` enum('Pianificata','In corso','Completata','Annullata') DEFAULT 'Pianificata',
  PRIMARY KEY (`ID_Consegna`),
  KEY `ID_Ordine` (`ID_Ordine`),
  KEY `ID_Veicolo` (`ID_Veicolo`),
  CONSTRAINT `consegne_ibfk_1` FOREIGN KEY (`ID_Ordine`) REFERENCES `ordini` (`ID_Ordine`) ON DELETE CASCADE,
  CONSTRAINT `consegne_ibfk_2` FOREIGN KEY (`ID_Veicolo`) REFERENCES `veicoli` (`ID_Veicolo`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO consegne VALUES ('1', '1', '1', '2023-10-28', 'Completata');
INSERT INTO consegne VALUES ('2', '2', '2', '2023-10-30', 'In corso');
INSERT INTO consegne VALUES ('3', '3', '3', '2023-11-01', 'Pianificata');

CREATE TABLE `credenziali` (
  `ID_Utente` int(11) NOT NULL AUTO_INCREMENT,
  `Username` varchar(255) NOT NULL,
  `Password` varbinary(60) NOT NULL,
  `Ruolo` enum('Amministratore','Operatore','Tecnico','Guest') NOT NULL,
  `ID_Dipendente` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ID_Utente`),
  UNIQUE KEY `Username` (`Username`),
  KEY `ID_Dipendente` (`ID_Dipendente`),
  CONSTRAINT `credenziali_ibfk_1` FOREIGN KEY (`ID_Dipendente`) REFERENCES `dipendenti` (`ID_Dipendente`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO credenziali VALUES ('2', 'admin', 'b'$2b$12$cBhDP2AhQcRwW1FUPPMxBurowDE8dJW7vOZfb7/mpezSXFHXZUmpS'', 'Amministratore', '622741bdba');

CREATE TABLE `dettaglimovimento` (
  `ID_Movimento` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Richiesta` int(11) DEFAULT NULL,
  `ID_Lotto` int(11) NOT NULL,
  `ID_Robot` int(11) DEFAULT NULL,
  `ID_Zona_Partenza` int(11) DEFAULT NULL,
  `ID_Zona_Destinazione` int(11) DEFAULT NULL,
  `ID_Scaffalatura_Destinazione` int(11) DEFAULT NULL,
  `Stato` enum('Assegnato','In corso','Completato','Annullato') DEFAULT 'Assegnato',
  `DataMovimento` timestamp NULL DEFAULT NULL,
  `DataCompletamento` timestamp NULL DEFAULT NULL,
  `TipoMovimento` enum('Entrata','Uscita','Spostamento') NOT NULL,
  PRIMARY KEY (`ID_Movimento`),
  KEY `ID_Richiesta` (`ID_Richiesta`),
  KEY `ID_Robot` (`ID_Robot`),
  KEY `ID_Scaffalatura_Destinazione` (`ID_Scaffalatura_Destinazione`),
  KEY `ID_Lotto` (`ID_Lotto`),
  KEY `ID_Zona_Partenza` (`ID_Zona_Partenza`),
  KEY `ID_Zona_Destinazione` (`ID_Zona_Destinazione`),
  CONSTRAINT `dettaglimovimento_ibfk_1` FOREIGN KEY (`ID_Richiesta`) REFERENCES `richiestemovimento` (`ID_Richiesta`) ON DELETE CASCADE,
  CONSTRAINT `dettaglimovimento_ibfk_2` FOREIGN KEY (`ID_Robot`) REFERENCES `robot` (`ID_Robot`) ON DELETE SET NULL,
  CONSTRAINT `dettaglimovimento_ibfk_3` FOREIGN KEY (`ID_Scaffalatura_Destinazione`) REFERENCES `scaffalature` (`ID_Scaffalatura`) ON DELETE CASCADE,
  CONSTRAINT `dettaglimovimento_ibfk_4` FOREIGN KEY (`ID_Lotto`) REFERENCES `lotti` (`ID_Lotto`) ON DELETE CASCADE,
  CONSTRAINT `dettaglimovimento_ibfk_5` FOREIGN KEY (`ID_Zona_Partenza`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE,
  CONSTRAINT `dettaglimovimento_ibfk_6` FOREIGN KEY (`ID_Zona_Destinazione`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO dettaglimovimento VALUES ('1', '1', '1', '1', '1', '2', '1', 'Completato', '2023-10-27 10:00:00', '2023-10-27 10:15:00', 'Spostamento');
INSERT INTO dettaglimovimento VALUES ('2', '2', '2', '2', '1', '3', '2', 'In corso', '2023-10-28 11:00:00', NULL, 'Spostamento');
INSERT INTO dettaglimovimento VALUES ('3', '3', '3', '2', '2', '4', '3', 'Assegnato', '2023-10-29 12:00:00', NULL, 'Spostamento');
INSERT INTO dettaglimovimento VALUES ('4', '4', '4', '3', '2', '1', '2', 'Completato', '2023-11-01 09:00:00', '2023-11-01 09:30:00', 'Entrata');
INSERT INTO dettaglimovimento VALUES ('5', '5', '5', '4', '4', '2', '3', 'In corso', '2023-11-02 10:00:00', NULL, 'Uscita');

CREATE TABLE `dettagliordini` (
  `ID_DettaglioOrdine` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Ordine` int(11) NOT NULL,
  `ID_Lotto` int(11) NOT NULL,
  `Quantita` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID_DettaglioOrdine`),
  KEY `ID_Ordine` (`ID_Ordine`),
  KEY `ID_Lotto` (`ID_Lotto`),
  CONSTRAINT `dettagliordini_ibfk_1` FOREIGN KEY (`ID_Ordine`) REFERENCES `ordini` (`ID_Ordine`) ON DELETE CASCADE,
  CONSTRAINT `dettagliordini_ibfk_2` FOREIGN KEY (`ID_Lotto`) REFERENCES `lotti` (`ID_Lotto`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO dettagliordini VALUES ('1', '1', '1', '50');
INSERT INTO dettagliordini VALUES ('2', '2', '2', '100');
INSERT INTO dettagliordini VALUES ('3', '3', '3', '75');

CREATE TABLE `dipendenti` (
  `ID_Dipendente` varchar(10) NOT NULL,
  `CodiceFiscale` varchar(16) NOT NULL,
  `Nome` varchar(255) NOT NULL,
  `Cognome` varchar(255) NOT NULL,
  `Ruolo` enum('Amministratore','Tecnico','Operatore') NOT NULL,
  `Mansione` enum('Manager','Tecnico IT','Manutenzione','Magazziniere','Responsabile Magazzino','Addetto Carico/Scarico','Operatore Logistico','Coordinatore Magazzino','Pianificatore','Controllo Qualit‡') NOT NULL,
  `DataAssunzione` date DEFAULT NULL,
  PRIMARY KEY (`ID_Dipendente`),
  UNIQUE KEY `CodiceFiscale` (`CodiceFiscale`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO dipendenti VALUES ('19256d0ed7', 'VRDBRT85C03H501X', 'Roberto', 'Verdi', 'Tecnico', 'Manutenzione', '2022-03-01');
INSERT INTO dipendenti VALUES ('622741bdba', 'RSSMRA80A01H501R', 'Mario', 'Rossi', 'Amministratore', 'Manager', '2020-01-01');
INSERT INTO dipendenti VALUES ('862df6e9e6', 'GLLGNN90B02H501Z', 'Giovanni', 'Gialli', 'Operatore', 'Magazziniere', '2021-02-01');

CREATE TABLE `fornitori` (
  `ID_Fornitore` int(11) NOT NULL AUTO_INCREMENT,
  `Nome` varchar(255) NOT NULL,
  `Indirizzo` varchar(255) DEFAULT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  `PartitaIVA` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_Fornitore`),
  UNIQUE KEY `PartitaIVA` (`PartitaIVA`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO fornitori VALUES ('1', 'Fornitore A', 'Via Roma 1, Milano', '0212345678', 'fornitoreA@email.com', 'IT12345678901');
INSERT INTO fornitori VALUES ('2', 'Fornitore B', 'Corso Italia 2, Roma', '0698765432', 'fornitoreB@email.com', 'IT98765432109');
INSERT INTO fornitori VALUES ('3', 'Fornitore C', 'Piazza Verdi 3, Napoli', '0815554433', 'fornitoreC@email.com', 'IT11223344556');
INSERT INTO fornitori VALUES ('4', 'Fornitore D', 'Via Dante 4, Torino', '0116667788', 'fornitoreD@email.com', 'IT66554433221');
INSERT INTO fornitori VALUES ('5', 'Fornitore E', 'Via Garibaldi 5, Palermo', '0917778899', 'fornitoreE@email.com', 'IT22334455667');

CREATE TABLE `letturesensori` (
  `ID_Lettura` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Sensore` int(11) NOT NULL,
  `Tipo` enum('Temperatura','Umidit‡','Presenza') NOT NULL,
  `Valore` float NOT NULL,
  `DataLettura` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID_Lettura`),
  KEY `ID_Sensore` (`ID_Sensore`),
  CONSTRAINT `letturesensori_ibfk_1` FOREIGN KEY (`ID_Sensore`) REFERENCES `sensori` (`ID_Sensore`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


CREATE TABLE `logmagazzino` (
  `ID_LogMagazzino` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Sensore` int(11) DEFAULT NULL,
  `ID_Lotto` int(11) DEFAULT NULL,
  `TipoNotifica` enum('Avviso','Alarme') NOT NULL,
  `TipoEvento` enum('Scadenza Lotto','Temperatura','Umidit‡') NOT NULL,
  `Messaggio` text DEFAULT NULL,
  `DataOra` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID_LogMagazzino`),
  KEY `ID_Sensore` (`ID_Sensore`),
  KEY `ID_Lotto` (`ID_Lotto`),
  CONSTRAINT `logmagazzino_ibfk_1` FOREIGN KEY (`ID_Sensore`) REFERENCES `sensori` (`ID_Sensore`) ON DELETE CASCADE,
  CONSTRAINT `logmagazzino_ibfk_2` FOREIGN KEY (`ID_Lotto`) REFERENCES `lotti` (`ID_Lotto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;


CREATE TABLE `logutenti` (
  `ID_LogUtente` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Utente` int(11) DEFAULT NULL,
  `DataOra` timestamp NULL DEFAULT current_timestamp(),
  `Tipo` enum('Accesso','Registrazione','Logout') NOT NULL,
  `Esito` enum('Successo','Fallito') NOT NULL,
  `Dettagli` varchar(255) DEFAULT NULL,
  `IP` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_LogUtente`),
  KEY `ID_Utente` (`ID_Utente`),
  CONSTRAINT `logutenti_ibfk_1` FOREIGN KEY (`ID_Utente`) REFERENCES `credenziali` (`ID_Utente`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO logutenti VALUES ('5', '2', '2025-01-20 08:38:59', 'Registrazione', 'Successo', 'Utente admin registrato con successo.', '::1');
INSERT INTO logutenti VALUES ('6', '2', '2025-01-20 08:39:04', 'Accesso', 'Successo', 'Utente admin ha effettuato l'accesso con successo.', '::1');

CREATE TABLE `lotti` (
  `ID_Lotto` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Prodotto` int(11) NOT NULL,
  `ID_Fornitore` int(11) NOT NULL,
  `ID_Zona` int(11) NOT NULL,
  `ID_Scaffalatura` int(11) NOT NULL,
  `Lotto` varchar(255) DEFAULT NULL,
  `Scadenza` date DEFAULT NULL,
  `Quantit‡Prodotto` int(11) NOT NULL DEFAULT 1,
  `PesoLotto` decimal(10,2) DEFAULT NULL,
  `PrezzoAcquisto` decimal(10,2) DEFAULT NULL,
  `ValoreLotto` decimal(10,2) DEFAULT NULL,
  `DataPrenotazione` date DEFAULT NULL,
  `DataRicevimento` date DEFAULT NULL,
  `Stato` enum('Disponibile','Esaurito','Prenotato') DEFAULT 'Disponibile',
  PRIMARY KEY (`ID_Lotto`),
  UNIQUE KEY `ID_Prodotto` (`ID_Prodotto`,`Lotto`),
  KEY `ID_Fornitore` (`ID_Fornitore`),
  KEY `ID_Zona` (`ID_Zona`),
  KEY `ID_Scaffalatura` (`ID_Scaffalatura`),
  CONSTRAINT `lotti_ibfk_1` FOREIGN KEY (`ID_Prodotto`) REFERENCES `prodotti` (`ID_Prodotto`) ON DELETE CASCADE,
  CONSTRAINT `lotti_ibfk_2` FOREIGN KEY (`ID_Fornitore`) REFERENCES `fornitori` (`ID_Fornitore`) ON DELETE CASCADE,
  CONSTRAINT `lotti_ibfk_3` FOREIGN KEY (`ID_Zona`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE,
  CONSTRAINT `lotti_ibfk_4` FOREIGN KEY (`ID_Scaffalatura`) REFERENCES `scaffalature` (`ID_Scaffalatura`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO lotti VALUES ('1', '1', '1', '1', '1', 'L001', '2024-12-31', '100', '100.00', '200.00', '240.00', '2022-12-15', '2023-01-01', 'Disponibile');
INSERT INTO lotti VALUES ('2', '2', '1', '1', '2', 'L002', '2024-11-30', '150', '150.00', '750.00', '900.00', '2023-02-01', '2023-02-15', 'Disponibile');
INSERT INTO lotti VALUES ('3', '3', '2', '2', '3', 'L003', '2024-10-31', '200', '4.00', '20.00', '24.00', '2023-03-01', '2023-03-10', 'Esaurito');
INSERT INTO lotti VALUES ('4', '4', '2', '2', '4', 'L004', '2024-09-30', '180', '5.40', '9.00', '10.80', '2023-04-15', NULL, 'Prenotato');
INSERT INTO lotti VALUES ('5', '5', '3', '3', '5', 'L005', '2024-08-31', '250', '125.00', '750.00', '900.00', '2023-04-25', '2023-05-05', 'Disponibile');
INSERT INTO lotti VALUES ('6', '6', '3', '3', '6', 'L006', '2024-07-31', '220', '44.00', '440.00', '528.00', '2023-06-01', '2023-06-15', 'Esaurito');
INSERT INTO lotti VALUES ('7', '7', '4', '1', '1', 'L007', '2024-06-30', '160', '160.00', '480.00', '576.00', '2023-07-05', NULL, 'Prenotato');
INSERT INTO lotti VALUES ('8', '8', '4', '1', '2', 'L008', '2024-05-31', '140', '8.40', '168.00', '201.60', '2023-08-01', '2023-08-20', 'Disponibile');
INSERT INTO lotti VALUES ('9', '9', '5', '2', '3', 'L009', '2024-04-30', '130', '32.50', '520.00', '624.00', '2023-09-10', '2023-09-25', 'Esaurito');
INSERT INTO lotti VALUES ('10', '10', '5', '2', '4', 'L010', '2024-03-31', '190', '3.80', '28.50', '34.20', '2023-10-01', NULL, 'Prenotato');

CREATE TABLE `manutenzionerobot` (
  `ID_Manutenzione` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Robot` int(11) NOT NULL,
  `DataManutenzione` date NOT NULL,
  `Tipo` enum('Ispezione','Riparazione','Sostituzione') NOT NULL,
  `Stato` enum('Programmata','Completata','Annullata') DEFAULT 'Programmata',
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID_Manutenzione`),
  KEY `ID_Robot` (`ID_Robot`),
  CONSTRAINT `manutenzionerobot_ibfk_1` FOREIGN KEY (`ID_Robot`) REFERENCES `robot` (`ID_Robot`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO manutenzionerobot VALUES ('1', '1', '2023-11-10', 'Ispezione', 'Programmata', 'Controllo generale');
INSERT INTO manutenzionerobot VALUES ('2', '2', '2023-11-15', 'Riparazione', 'Programmata', 'Sostituzione batteria');
INSERT INTO manutenzionerobot VALUES ('3', '3', '2023-11-20', 'Sostituzione', 'Programmata', 'Sostituzione motore');

CREATE TABLE `manutenzionescaffalature` (
  `ID_Manutenzione` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Scaffalatura` int(11) NOT NULL,
  `DataManutenzione` date NOT NULL,
  `Tipo` enum('Ispezione','Pulizia','Riparazione','Sostituzione') NOT NULL,
  `Stato` enum('Programmata','Completata','Annullata') DEFAULT 'Programmata',
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID_Manutenzione`),
  KEY `ID_Scaffalatura` (`ID_Scaffalatura`),
  CONSTRAINT `manutenzionescaffalature_ibfk_1` FOREIGN KEY (`ID_Scaffalatura`) REFERENCES `scaffalature` (`ID_Scaffalatura`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO manutenzionescaffalature VALUES ('1', '1', '2023-11-05', 'Ispezione', 'Programmata', 'Verifica Bulloneria');
INSERT INTO manutenzionescaffalature VALUES ('2', '2', '2023-11-08', 'Riparazione', 'Programmata', 'Sostituzione mensole');
INSERT INTO manutenzionescaffalature VALUES ('3', '3', '2023-11-12', 'Pulizia', 'Programmata', 'Pulizia generale');

CREATE TABLE `manutenzioneveicoli` (
  `ID_Manutenzione` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Veicolo` int(11) NOT NULL,
  `DataManutenzione` date NOT NULL,
  `Tipo` enum('Ispezione','Riparazione','Sostituzione') NOT NULL,
  `Stato` enum('Programmata','Completata','Annullata') DEFAULT 'Programmata',
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID_Manutenzione`),
  KEY `ID_Veicolo` (`ID_Veicolo`),
  CONSTRAINT `manutenzioneveicoli_ibfk_1` FOREIGN KEY (`ID_Veicolo`) REFERENCES `veicoli` (`ID_Veicolo`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO manutenzioneveicoli VALUES ('1', '1', '2023-11-12', 'Ispezione', 'Programmata', 'Controllo freni e livelli');
INSERT INTO manutenzioneveicoli VALUES ('2', '2', '2023-11-18', 'Riparazione', 'Programmata', 'Sostituzione pneumatici');
INSERT INTO manutenzioneveicoli VALUES ('3', '3', '2023-11-22', 'Sostituzione', 'Programmata', 'Sostituzione batteria');

CREATE TABLE `manutenzionezone` (
  `ID_Manutenzione` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Zona` int(11) NOT NULL,
  `DataManutenzione` date NOT NULL,
  `Tipo` enum('Ispezione','Pulizia','Riparazione') NOT NULL,
  `Stato` enum('Programmata','Completata','Annullata') DEFAULT 'Programmata',
  `Note` text DEFAULT NULL,
  PRIMARY KEY (`ID_Manutenzione`),
  KEY `ID_Zona` (`ID_Zona`),
  CONSTRAINT `manutenzionezone_ibfk_1` FOREIGN KEY (`ID_Zona`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO manutenzionezone VALUES ('1', '1', '2023-11-20', 'Pulizia', 'Programmata', 'Pulizia e sanificazione');
INSERT INTO manutenzionezone VALUES ('2', '2', '2023-11-25', 'Riparazione', 'Programmata', 'Riparazione illuminazione');
INSERT INTO manutenzionezone VALUES ('3', '3', '2023-11-30', 'Ispezione', 'Programmata', 'Ispezione generale');

CREATE TABLE `ordini` (
  `ID_Ordine` int(11) NOT NULL AUTO_INCREMENT,
  `DataOrdine` timestamp NULL DEFAULT current_timestamp(),
  `Tipo` enum('Entrata','Uscita') NOT NULL,
  `ID_Fornitore` int(11) DEFAULT NULL,
  `ID_Cliente` int(11) DEFAULT NULL,
  `Stato` enum('In elaborazione','Spedito','Concluso') DEFAULT 'In elaborazione',
  PRIMARY KEY (`ID_Ordine`),
  KEY `ID_Fornitore` (`ID_Fornitore`),
  KEY `ID_Cliente` (`ID_Cliente`),
  CONSTRAINT `ordini_ibfk_1` FOREIGN KEY (`ID_Fornitore`) REFERENCES `fornitori` (`ID_Fornitore`) ON DELETE SET NULL,
  CONSTRAINT `ordini_ibfk_2` FOREIGN KEY (`ID_Cliente`) REFERENCES `clienti` (`ID_Cliente`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO ordini VALUES ('1', '2023-10-25 09:00:00', 'Entrata', '1', NULL, 'In elaborazione');
INSERT INTO ordini VALUES ('2', '2023-10-26 10:00:00', 'Uscita', NULL, '1', 'Spedito');
INSERT INTO ordini VALUES ('3', '2023-10-27 11:00:00', 'Entrata', '2', NULL, 'Concluso');

CREATE TABLE `prodotti` (
  `ID_Prodotto` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Fornitore` int(11) DEFAULT NULL,
  `Nome` varchar(255) NOT NULL,
  `Produttore` varchar(255) DEFAULT NULL,
  `Tipo` enum('Alimentare','Farmaceutico') NOT NULL,
  `Quantit‡Confezione` decimal(10,2) NOT NULL,
  `UnitaMisura` enum('kg','g','l','ml','compresse','capsule') NOT NULL,
  PRIMARY KEY (`ID_Prodotto`),
  UNIQUE KEY `Nome` (`Nome`),
  KEY `ID_Fornitore` (`ID_Fornitore`),
  CONSTRAINT `prodotti_ibfk_1` FOREIGN KEY (`ID_Fornitore`) REFERENCES `fornitori` (`ID_Fornitore`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO prodotti VALUES ('1', '1', 'Pasta di Grano Duro', 'Pastificio Italia', 'Alimentare', '1.00', 'kg');
INSERT INTO prodotti VALUES ('2', '1', 'Olio Extra Vergine di Oliva', 'Oleificio Sole', 'Alimentare', '1.00', 'l');
INSERT INTO prodotti VALUES ('3', '2', 'Paracetamolo 500mg', 'Farmaceutica ABC', 'Farmaceutico', '20.00', 'compresse');
INSERT INTO prodotti VALUES ('4', '2', 'Aspirina 100mg', 'Farmaceutica XYZ', 'Farmaceutico', '30.00', 'compresse');
INSERT INTO prodotti VALUES ('5', '3', 'Biscotti Frollini', 'Biscottificio Dolce', 'Alimentare', '500.00', 'g');
INSERT INTO prodotti VALUES ('6', '3', 'Sciroppo per la Tosse', 'Farmaceutica ABC', 'Farmaceutico', '200.00', 'ml');
INSERT INTO prodotti VALUES ('7', '4', 'Riso Carnaroli', 'Riseria Bella', 'Alimentare', '1.00', 'kg');
INSERT INTO prodotti VALUES ('8', '4', 'Vitamina C 1000mg', 'Integratori Plus', 'Farmaceutico', '60.00', 'capsule');
INSERT INTO prodotti VALUES ('9', '5', 'CaffË Macinato', 'CaffË Aroma', 'Alimentare', '250.00', 'g');
INSERT INTO prodotti VALUES ('10', '5', 'Ibuprofene 400mg', 'Farmaceutica XYZ', 'Farmaceutico', '20.00', 'compresse');

CREATE TABLE `richiestemovimento` (
  `ID_Richiesta` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Lotto` int(11) NOT NULL,
  `ID_Zona_Partenza` int(11) NOT NULL,
  `ID_Zona_Destinazione` int(11) NOT NULL,
  `ID_Scaffalatura_Destinazione` int(11) NOT NULL,
  `ID_Robot` int(11) DEFAULT NULL,
  `Priorita` enum('Bassa','Media','Alta') DEFAULT 'Bassa',
  `DataRichiesta` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`ID_Richiesta`),
  KEY `ID_Lotto` (`ID_Lotto`),
  KEY `ID_Robot` (`ID_Robot`),
  KEY `ID_Zona_Partenza` (`ID_Zona_Partenza`),
  KEY `ID_Zona_Destinazione` (`ID_Zona_Destinazione`),
  KEY `ID_Scaffalatura_Destinazione` (`ID_Scaffalatura_Destinazione`),
  CONSTRAINT `richiestemovimento_ibfk_1` FOREIGN KEY (`ID_Lotto`) REFERENCES `lotti` (`ID_Lotto`) ON DELETE CASCADE,
  CONSTRAINT `richiestemovimento_ibfk_2` FOREIGN KEY (`ID_Robot`) REFERENCES `robot` (`ID_Robot`) ON DELETE SET NULL,
  CONSTRAINT `richiestemovimento_ibfk_3` FOREIGN KEY (`ID_Zona_Partenza`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE,
  CONSTRAINT `richiestemovimento_ibfk_4` FOREIGN KEY (`ID_Zona_Destinazione`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE,
  CONSTRAINT `richiestemovimento_ibfk_5` FOREIGN KEY (`ID_Scaffalatura_Destinazione`) REFERENCES `scaffalature` (`ID_Scaffalatura`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO richiestemovimento VALUES ('1', '1', '1', '2', '1', '1', 'Alta', '2023-10-27 10:00:00');
INSERT INTO richiestemovimento VALUES ('2', '2', '1', '3', '2', '2', 'Media', '2023-10-28 11:00:00');
INSERT INTO richiestemovimento VALUES ('3', '3', '2', '4', '3', '2', 'Bassa', '2023-10-29 12:00:00');
INSERT INTO richiestemovimento VALUES ('4', '4', '3', '1', '4', '3', 'Alta', '2023-10-30 13:00:00');
INSERT INTO richiestemovimento VALUES ('5', '5', '4', '2', '1', '4', 'Media', '2023-10-31 14:00:00');

CREATE TABLE `robot` (
  `ID_Robot` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Sensore` int(11) NOT NULL,
  `ID_Zona` int(11) NOT NULL,
  `Nome` varchar(255) NOT NULL,
  `Stato` enum('Disponibile','Occupato','Manutenzione') DEFAULT 'Disponibile',
  `PosizioneAttuale` varchar(255) DEFAULT NULL,
  `Capacita` int(11) DEFAULT NULL,
  `ID_Ricarica` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID_Robot`),
  KEY `ID_Sensore` (`ID_Sensore`),
  KEY `ID_Zona` (`ID_Zona`),
  KEY `ID_Ricarica` (`ID_Ricarica`),
  CONSTRAINT `robot_ibfk_1` FOREIGN KEY (`ID_Sensore`) REFERENCES `sensori` (`ID_Sensore`) ON DELETE CASCADE,
  CONSTRAINT `robot_ibfk_2` FOREIGN KEY (`ID_Zona`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE,
  CONSTRAINT `robot_ibfk_3` FOREIGN KEY (`ID_Ricarica`) REFERENCES `stazionericarica` (`ID_Ricarica`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO robot VALUES ('1', '1', '1', 'Robot A', 'Disponibile', 'Scaffale A1', '100', '1');
INSERT INTO robot VALUES ('2', '1', '1', 'Robot B', 'Disponibile', 'Scaffale A2', '120', '1');
INSERT INTO robot VALUES ('3', '4', '2', 'Robot C', 'Disponibile', 'Scaffale B1', '150', '2');
INSERT INTO robot VALUES ('4', '4', '2', 'Robot D', 'Disponibile', 'Scaffale B2', '130', '2');
INSERT INTO robot VALUES ('5', '7', '3', 'Robot E', 'Disponibile', 'Scaffale C1', '110', '3');
INSERT INTO robot VALUES ('6', '10', '4', 'Robot F', 'Disponibile', 'Scaffale D1', '140', '4');

CREATE TABLE `scaffalature` (
  `ID_Scaffalatura` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Zona` int(11) NOT NULL,
  `Nome` varchar(255) NOT NULL,
  `Capacit‡Lotti` int(11) NOT NULL DEFAULT 100,
  PRIMARY KEY (`ID_Scaffalatura`),
  UNIQUE KEY `Nome` (`Nome`),
  KEY `ID_Zona` (`ID_Zona`),
  CONSTRAINT `scaffalature_ibfk_1` FOREIGN KEY (`ID_Zona`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO scaffalature VALUES ('1', '1', 'Scaffale A1', '100');
INSERT INTO scaffalature VALUES ('2', '1', 'Scaffale A2', '80');
INSERT INTO scaffalature VALUES ('3', '2', 'Scaffale B1', '150');
INSERT INTO scaffalature VALUES ('4', '2', 'Scaffale B2', '120');
INSERT INTO scaffalature VALUES ('5', '3', 'Scaffale C1', '50');
INSERT INTO scaffalature VALUES ('6', '4', 'Scaffale D1', '60');

CREATE TABLE `sensori` (
  `ID_Sensore` int(11) NOT NULL AUTO_INCREMENT,
  `Tipo` enum('Presenza','Temperatura','Umidit‡') NOT NULL,
  `ID_Zona` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID_Sensore`),
  KEY `ID_Zona` (`ID_Zona`),
  CONSTRAINT `sensori_ibfk_1` FOREIGN KEY (`ID_Zona`) REFERENCES `zone` (`ID_Zona`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO sensori VALUES ('1', 'Presenza', '1');
INSERT INTO sensori VALUES ('2', 'Temperatura', '1');
INSERT INTO sensori VALUES ('3', 'Umidit‡', '1');
INSERT INTO sensori VALUES ('4', 'Presenza', '2');
INSERT INTO sensori VALUES ('5', 'Temperatura', '2');
INSERT INTO sensori VALUES ('6', 'Umidit‡', '2');
INSERT INTO sensori VALUES ('7', 'Presenza', '3');
INSERT INTO sensori VALUES ('8', 'Temperatura', '3');
INSERT INTO sensori VALUES ('9', 'Umidit‡', '3');
INSERT INTO sensori VALUES ('10', 'Presenza', '4');
INSERT INTO sensori VALUES ('11', 'Temperatura', '4');
INSERT INTO sensori VALUES ('12', 'Umidit‡', '4');

CREATE TABLE `stazionericarica` (
  `ID_Ricarica` int(11) NOT NULL AUTO_INCREMENT,
  `ZonaID` int(11) NOT NULL,
  `Nome` varchar(255) NOT NULL,
  `Stato` enum('Libera','Occupata','Inoperativa') DEFAULT 'Libera',
  PRIMARY KEY (`ID_Ricarica`),
  UNIQUE KEY `ZonaID` (`ZonaID`,`Nome`),
  CONSTRAINT `stazionericarica_ibfk_1` FOREIGN KEY (`ZonaID`) REFERENCES `zone` (`ID_Zona`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO stazionericarica VALUES ('1', '1', 'Stazione Ricarica 1', 'Libera');
INSERT INTO stazionericarica VALUES ('2', '2', 'Stazione Ricarica 2', 'Libera');
INSERT INTO stazionericarica VALUES ('3', '3', 'Stazione Ricarica 3', 'Libera');
INSERT INTO stazionericarica VALUES ('4', '4', 'Stazione Ricarica 4', 'Libera');

CREATE TABLE `turnidipendenti` (
  `ID_Turno` int(11) NOT NULL AUTO_INCREMENT,
  `ID_Dipendente` varchar(10) NOT NULL,
  `DataInizio` timestamp NOT NULL,
  `DataFine` timestamp NOT NULL,
  `Mansione` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID_Turno`),
  KEY `ID_Dipendente` (`ID_Dipendente`),
  CONSTRAINT `turnidipendenti_ibfk_1` FOREIGN KEY (`ID_Dipendente`) REFERENCES `dipendenti` (`ID_Dipendente`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO turnidipendenti VALUES ('1', '622741bdba', '2023-10-27 09:00:00', '2023-10-27 18:00:00', 'Manager');
INSERT INTO turnidipendenti VALUES ('2', '862df6e9e6', '2023-10-27 08:00:00', '2023-10-27 16:00:00', 'Magazziniere');
INSERT INTO turnidipendenti VALUES ('3', '19256d0ed7', '2023-10-27 09:00:00', '2023-10-27 17:00:00', 'Manutenzione');

CREATE TABLE `veicoli` (
  `ID_Veicolo` int(11) NOT NULL AUTO_INCREMENT,
  `Tipo` enum('Bilico','Furgone','Carrello_Elevatore') NOT NULL,
  `Capacita` int(11) NOT NULL,
  `Stato` enum('Disponibile','In uso','Manutenzione') DEFAULT 'Disponibile',
  `Targa` varchar(20) NOT NULL,
  PRIMARY KEY (`ID_Veicolo`),
  UNIQUE KEY `Targa` (`Targa`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO veicoli VALUES ('1', 'Bilico', '10000', 'Disponibile', 'AA123BB');
INSERT INTO veicoli VALUES ('2', 'Furgone', '2000', 'Disponibile', 'CC456DD');
INSERT INTO veicoli VALUES ('3', 'Carrello_Elevatore', '500', 'Disponibile', 'EE789FF');

CREATE TABLE `zone` (
  `ID_Zona` int(11) NOT NULL AUTO_INCREMENT,
  `Nome` varchar(255) NOT NULL,
  `Tipo` enum('Stoccaggio_Alimentari','Stoccaggio_Farmaceutici','Carico','Scarico') NOT NULL,
  `Descrizione` text DEFAULT NULL,
  PRIMARY KEY (`ID_Zona`),
  UNIQUE KEY `Nome` (`Nome`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

INSERT INTO zone VALUES ('1', 'Stoccaggio A01', 'Stoccaggio_Alimentari', 'Zona di stoccaggio per prodotti alimentari');
INSERT INTO zone VALUES ('2', 'Stoccaggio F01', 'Stoccaggio_Farmaceutici', 'Zona di stoccaggio per prodotti farmaceutici');
INSERT INTO zone VALUES ('3', 'Baia Carico01', 'Carico', 'Zona per il carico delle merci');
INSERT INTO zone VALUES ('4', 'Baia Scarico01', 'Scarico', 'Zona per lo scarico delle merci');

