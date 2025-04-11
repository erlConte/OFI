from django.conf import settings
from django.db import connections

def get_db_connection():
    """
    Restituisce la connessione al database configurata
    """
    return connections['default']

def execute_query(query, params=None):
    """
    Esegue una query SQL e restituisce i risultati
    """
    with get_db_connection().cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()

def execute_many(query, params_list):
    """
    Esegue una query SQL con multiple set di parametri
    """
    with get_db_connection().cursor() as cursor:
        cursor.executemany(query, params_list)
        return cursor.rowcount 