import hashlib

def create_employee_id(codice_fiscale, nome, cognome, ruolo, data_assunzione):
    """
    Crea un ID dipendente unico dato il codice fiscale, nome, cognome, ruolo e data di assunzione.
    """
    concatenated_string = f"{codice_fiscale}{nome}{cognome}{ruolo}{data_assunzione}"
    hashed_string = hashlib.sha256(concatenated_string.encode()).hexdigest()
    employee_id = hashed_string[:10]
    return employee_id

id = create_employee_id("RSSMRA80A01C351O", "Mario", "Rossi", "Operatore", "2020-05-15")
print(id)
"""
("RSSMRA80A01C351O", "Mario", "Rossi", "Operatore", "2020-05-15") = 0f8f13e503,
("BNCLSU98E54C351X", "Luisa", "Bianchi", "Tecnico", "2020-03-10") = 5f6c960209,
("VRDGLI90D43C351B", "Giulia", "Verdi", "Amministratore", "2015-01-20") = 0f0abffd80
"""