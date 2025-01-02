import hashlib
def create_employee_id(codicefiscale, nome, cognome, ruolo, dataassunzione):
    """
    Crea un ID dipendente unico dato il codice fiscale, nome, cognome, ruolo e data di assunzione.
    """
    concatenated_string = f"{codicefiscale}{nome}{cognome}{ruolo}{dataassunzione}"
    hashed_string = hashlib.sha256(concatenated_string.encode()).hexdigest()
    employee_id = hashed_string[:10]
    return employee_id
