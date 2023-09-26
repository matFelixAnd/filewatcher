from common import *

class LengthError(Exception):
    pass

class XMLHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.lower().endswith('.xml'):
            return
        
        try:
            xml_file_path = event.src_path
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            nsNFE = {'ns': "http://www.portalfiscal.inf.br/nfe"}
            numero_nfe_xml = root.find('ns:NFe/ns:infNFe/ns:ide/ns:nNF', nsNFE)
            versao_xml = root.find('ns:NFe/ns:infNFe/ns:ide/ns:verProc', nsNFE)
            chave_xml = root.find('ns:NFe/ns:infNFe', nsNFE)
            tpag_xml = root.find('ns:NFe/ns:infNFe/ns:pag/ns:detPag/ns:tPag', nsNFE)

            NNF, CHAVE, TPAG, VERSAO = (
                numero_nfe_xml.text,
                chave_xml.attrib['Id'][3:],
                tpag_xml.text,
                versao_xml.text
            )

            if len(CHAVE) != 44:
                raise LengthError("O comprimento da chave da nota fiscal não é válido.")

            # Conectar e executar a query
            with FDBConnection(
                host="127.0.0.1",
                database="C:/Backup/Otimotex1.FDB",
                user="SYSDBA",
                password="masterkey",
                port=3050
            ) as conn:
                cursor = conn.cursor()
                query = 'EXECUTE PROCEDURE SP_NFE_XML (?,?,?,?)'
                cursor.execute(query, (NNF, CHAVE, TPAG, VERSAO))
                conn.commit()

        except (ET.ParseError, fdb.Error, ValueError, IOError, Exception, KeyboardInterrupt, MemoryError, OSError) as error:
            # Lidar com os erros e inserir no log
            with FDBConnection(
                host="127.0.0.1",
                database="C:/Backup/Otimotex1.FDB",
                user="SYSDBA",
                password="masterkey",
                port=3050
            ) as conn:
                cursor = conn.cursor()
                query = 'INSERT INTO XML_NFE_LOG (ARQUIVO,ERRO) VALUES (?, ?) '
                cursor.execute(query, (event.src_path, str(error)))
                conn.commit()

if __name__ == "__main__":
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
