import xml.etree.ElementTree as ET
from xml.dom import minidom

caminho_arquivo = "caminho da nota fiscal"

root = ET.parse(caminho_arquivo).getroot()  # Fazer o parse do arquivo#
nsNFE = {'ns': "http://www.portalfiscal.inf.br/nfe"}  # Primeiro atributo da nota#



# Viajar pelo xml (CASE SENSITIVE)#
numero_nfe_xml = root.find('ns:NFe/ns:infNFe/ns:ide/ns:nNF', nsNFE)
versao_xml = root.find('ns:NFe/ns:infNFe/ns:ide/ns:verProc', nsNFE)
chave_xml = root.find('ns:NFe/ns:infNFe', nsNFE)
tpag_xml = root.find('ns:NFe/ns:infNFe/ns:pag/ns:detPag/ns:tPag', nsNFE)
# Armazenar em uma variavel para subir pro banco
NNF = numero_nfe_xml.text
VERSAO = versao_xml.text
CHAVE = chave_xml.attrib['Id'][3:]
TPAG = tpag_xml.text
print(NNF)
print(VERSAO)
print(CHAVE)
print(TPAG)
