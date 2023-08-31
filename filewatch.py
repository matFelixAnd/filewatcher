import time
import firebirdsql as fdb
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xml.etree.ElementTree as ET
import re


class LengthError(Exception):
    pass


try:
    conn = fdb.connect(host="127.0.0.1",
                       database="C:/Backup/Otimotex1.FDB",
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
            try:
                # Leitura do arquivo XML

                xml_file_path = event.src_path
                tree = ET.parse(xml_file_path)
                root = tree.getroot()

                # Aqui você pode processar os elementos do XML conforme sua necessidade

                nsNFE = {'ns': "http://www.portalfiscal.inf.br/nfe"}  # Primeiro atributo da nota#
                numero_nfe_xml = root.find('ns:NFe/ns:infNFe/ns:ide/ns:nNF', nsNFE)
                versao_xml = root.find('ns:NFe/ns:infNFe/ns:ide/ns:verProc', nsNFE)
                chave_xml = root.find('ns:NFe/ns:infNFe', nsNFE)
                tpag_xml = root.find('ns:NFe/ns:infNFe/ns:pag/ns:detPag/ns:tPag', nsNFE)

                # NNF -> Numero da nota/ Versão/ Chave -> Chave de acesso/ TPAG -> Tipo do pagamento

                NNF = numero_nfe_xml.text
                CHAVE = chave_xml.attrib['Id'][3:]
                TPAG = tpag_xml.text
                VERSAO = versao_xml.text

                # Verificação do comprimento do nome do arquivo
                if len(CHAVE) != 44:
                    raise LengthError("O comprimento da chave da nota fiscal nao e valido.")

                # Código pra inserção

                cur = conn.cursor()
                query = f'EXECUTE PROCEDURE SP_NFE_XML (?,?,?,?)'
                cur.execute(query, (NNF, CHAVE, TPAG, VERSAO))
                conn.commit()
                cur.close()




            # erro na leitura do xml
            except ET.ParseError as parse_error:
                cur = conn.cursor()
                query = 'INSERT INTO XML_NFE_LOG (ARQUIVO,ERRO) VALUES (?,?)'
                cur.execute(query, (event.src_patch, parse_error,))
                conn.commit
                cur.close
                return

            # erro do banco
            except fdb.Error as error:

                cur = conn.cursor()
                query = 'INSERT INTO XML_NFE_LOG (ARQUIVO,ERRO) VALUES (?, ?) '
                cur.execute(query, (event.src_path, error,))
                conn.commit()
                cur.close()
                print(f'Log de erro {error} ')
                return

            # erro no arquivo
            except ValueError as ve:

                cur = conn.cursor()
                query = 'INSERT INTO XML_NFE_LOG (ARQUIVO,ERRO) VALUES (?, ?) '
                cur.execute(query, (event.src_path, ve,))
                conn.commit()
                cur.close()
                return


if __name__ == "__main__":

    # Diretório que vai monitorar

    diretorio_monitorado = "C:\\Users\\mateus.OTIMOTEX\\Desktop\\xmlNFE"

    event_handler = XMLHandler()
    observer = Observer()
    observer.schedule(event_handler, path=diretorio_monitorado, recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
