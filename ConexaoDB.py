import sqlite3

class ConexaoDB:
    
    def conectar_db(self):
        return sqlite3.connect('formatador.db')
