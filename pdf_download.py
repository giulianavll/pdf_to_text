import requests
from bs4 import BeautifulSoup
import os
import json
import re
# import fitz
from PyPDF2 import PdfReader

def replace_multiple_spaces(text):
    # text = re.sub(r"\s+", " ", text)
    # text = re.sub(r"(?!\n)\s+", " ", text)  # mantiene los saltos de linea
    text = " ".join(text.split())
    text = re.sub(r" \n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def replace_symbols_paragraph(text):
    rpta = ""
    len_text = len(text)
    i = 0
    while i < len_text:
        if text[i] != "\n":
            rpta += text[i]
            i += 1
        else:
            flag = True
            while i + 1 < len_text and flag:
                if text[i + 1] == " ":
                    i += 1
                else:
                    if text[i + 1].isupper():
                        rpta += "#@#" + text[i + 1]
                    else:
                        rpta += " " + text[i + 1]
                    i += 2
                    flag = False
    return rpta


def replace_special_characters(text):
    replacements = {
        # Comillas
        "\u201c": '"',  # Comilla doble izquierda, comillas curvas
        "\u201d": '"',  # Comilla doble derecha, comillas curvas
        "\u2018": "'",  # Comilla simple izquierda
        "\u2019": "'",  # Comilla simple derecha
        # Guiones
        "\u2013": "-",  # Guion en rango
        "\u2014": "--",  # Guion largo
        # Puntos suspensivos
        "\u2026": "...",  # Puntos suspensivos
        # Caracteres de espacio en blanco
        "\u00A0": " ",  # Espacio en blanco sin separación
        "\u00a0": " ",  # Espacio en blanco sin separación
        "\u000C": " ",  # Unicode Character 'FORM FEED (FF)' (U+000C)
        "\u000c": " ",  # Unicode Character 'FORM FEED (FF)' (U+000C)
        "\u2002": " ",  # Espacio en em
        "\u2003": " ",  # Espacio en en
        "\u2009": " ",  # Espacio en estrecho
    }

    # Realizar los reemplazos
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    return text


def dowload_pdf(folder_root,link):
       name = "TribunaldarrondissementDiekirchcommerce"
       folder_path = folder_root
       isExist = os.path.exists(folder_path)
       if not isExist:
          print("not")
          os.makedirs(folder_path)
       url_o = link
       element = 0
       while element >= 0:
              extension = "" 
              if element >0:
                     extension = "b="+str(element)
              element = element + 20
              url = url_o+extension
              print("nn",url)
              response = requests.get(url)
              if response.status_code == 200:
                     print("hello")
                     soup = BeautifulSoup(response.text, 'html.parser')
                     links = soup.find_all('a')
                     # Recorre los enlaces y descarga los PDFs
                     some_pdf =0  
                     for link in links:
                         href =link.get('href')
                         if href:
                                 if href.endswith(".pdf"):
                                     some_pdf =+1
                                     pdf_url = href
                                     pdf_name = pdf_url.split("/")[-1]
                                     pdf_folder = pdf_name.split(".")[0]
                                     print("doc",pdf_name)
                                     folder_pdf = folder_path+"/"+ pdf_folder
                                     isExist = os.path.exists(folder_pdf)
                                     if not isExist:
                                        os.makedirs(folder_pdf)
                                     complete_folder = folder_pdf+"/"+pdf_name
                                     response = requests.get(pdf_url)
                                     if response.status_code == 200:
                                          with open(complete_folder, 'wb') as pdf_file:
                                                pdf_file.write(response.content)
                                                print("Descarga completada.")
                                     else:
                                          print(f"No se pudo acceder a la página web. Código de estado: {response.status_code}")
                     if some_pdf==0: 
                            element=-1
              else:
                     element =-1
def get_json(pdf_text,text_name,path):
     print("convert json",text_name)
     ajson={}
     lower_text = pdf_text.lower()
     index_faits = lower_text.find("\nfaits:\n")
     index_judgment = lower_text.find("\njugement\n")
     index_motifs = lower_text.find("\npar ces motifs\n")
     ajson["meta_name"] = text_name
     ajson["content"] = pdf_text
     #ajson["head"]= pdf_text[:index_faits]
     #ajson["faits"] = pdf_text[index_faits:index_judgment]
     #ajson["judgment"] = pdf_text[index_judgment:index_motifs]
     #ajson["motifs"] = pdf_text[index_motifs:]
     with open(f"{path}/text_name.json", "w", encoding="utf-8") as out:
        json.dump(ajson, out, indent=4, ensure_ascii=False)
     return 
# def convert_pdf_text_2(path_file,name):  
    
#     print("get text",name)    
#     pdf_text = ""
#     pdf_file = path_file+"/"+name+".pdf"
#     doc = fitz.open(pdf_file)  # open a document
#     for index, page in enumerate(doc):  # iterate the document pages
#         text = page.get_text()
#         text = replace_special_characters(text)
#         text = replace_multiple_spaces(text)
#         text = text.encode("utf-8", "ignore").decode("utf-8")
#         pdf_text = pdf_text +text
#     get_json(pdf_text,name,path_file)
#     return 


def convert_pdf_text(path_file,name):  
    print("get text",name)    
    pdf_text = ""
    pdf_file = path_file+"/"+name+".pdf"
    print("get text",pdf_file)    
    with open(pdf_file, "rb") as pdf:
       reader = PdfReader(pdf)
       for index, page in enumerate(reader.pages):
            text = page.extract_text()
            text = replace_special_characters(text)
            text = replace_multiple_spaces(text)
            text = replace_symbols_paragraph(text)
            # text = text.encode("ascii", "ignore").decode("ascii")
            text = text.encode("utf-8", "ignore").decode("utf-8")
            pdf_text = pdf_text +text
    get_json(pdf_text,name,path_file)
#
def pdf_to_json(folder_path):
       for f in os.listdir(folder_path):
              if os.path.isdir(os.path.join(folder_path, f)):
                   #pdf_path= folder_path+"/"+f+"/"+f+".pdf"
              #      with open(pdf_path, 'wb') as pdf_file:
              #        pdf_contents = pdf_file.read()
                   convert_pdf_text(folder_path+"/"+f,f)
              
parent = "/home/giuliana/Documentos/Free/decision/"
name ="TribunaldarrondissementDiekirchcommerce"
folder_root = os.path.join(parent,name)
link = 'https://justice.public.lu/fr/jurisprudence/juridictions-judiciaires.html?r=f%2Fanon_juridiction%2Ftribunal+d%27arrondissement+diekirch+commerce&'
dowload_pdf(folder_root,link)     
print("OTHER TASk") 
pdf_to_json(folder_root)    

            
