import time
import re
import firebirdsql as fdb
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

try:
    conn = fdb.connect(host="127.0.0.1",
                       database="seu banco",
                       user="SYSDBA",
                       password="masterkey",
                       port=3050)
except fdb.Error as e:
    # Capturar exceção de erro de conexão
    print("Erro ao conectar ao banco de dados:", e)


    # Classe para manipular eventos do sistema de arquivos

    class XMLHandler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return

            elif event.src_path.lower().endswith('.xml'):
                # Ação após ser criado
                print(f"Novo arquivo XML criado:  {event.src_path} ")
                try:
                    obj = event.src_path[40:]
                    obj = obj.split('\\')[-1]
                    obj = re.sub('[^0-9]', '', obj)
                    obj = f'{obj}'
                    cur = conn.cursor()
                    query = f'query'
                    cur.execute(query, (obj,))
                    if len(obj) != 44:
                        raise ValueError("O campo XML deve conter exatamente 44 caracteres!")
                    conn.commit()
                    cur.close()
                    print(f'A chave de acesso: {obj} foi inserida/atualizada.')
                    return

                except fdb.Error as error:

                    # Capturar log de erro
                    print(f'Motivo do erro: {error}')
                    cur = conn.cursor()
                    query = 'query '
                    cur.execute(query, (event.src_path, error,))
                    conn.commit()
                    cur.close()
                    print(f'Log de erro {error} ')

                    return

                except ValueError as ve:
                    print(f'Motivo do erro: {ve}')
                    cur = conn.cursor()
                    query = 'query'
                    cur.execute(query, (event.src_path, ve,))
                    conn.commit()
                    cur.close()
                    print(f'Log de erro {ve} inserido')

                    return


    if __name__ == "__main__":

        # Diretório que você deseja monitorar
        diretorio_monitorado = "diretorio a ser monitorado"

        event_handler = XMLHandler()
        observer = Observer()
        observer.schedule(event_handler, path=diretorio_monitorado, recursive=False)

        print(f"Monitorando o diretório: {diretorio_monitorado}")

        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()

        observer.join()
