import firebirdsql as fdb

class FDBConnection:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        try:
            self.conn = fdb.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            print('connected')
        except fdb.Error as e:
            print("Erro ao conectar ao banco de dados:", e)
            # Rethrow the exception to handle it at a higher level if needed
            raise

    def cursor(self):
       if self.conn:
           return self.conn.cursor()
       else:
           raise Exception("Conexão não estabelecida. Chame o método connect() primeiro.")
    
    def commit(self):
        if self.conn:
            self.conn.commit()
        else:
            raise Exception("Conexão não estabelecida. Chame o método connect() primeiro.")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()



# with FDBConnection(host="127.0.0.1", database="C:/Backup/Otimotex1.FDB", user="SYSDBA", password="masterkey", port=3050) as conn:
