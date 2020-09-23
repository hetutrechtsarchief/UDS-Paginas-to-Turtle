#!/usr/bin/env python3
import sys,argparse,re
import time
import csv
import mysql.connector
import datetime
import io
import urllib.parse

def makeSafeURIPart(s):
  # spreadsheet: [–’&|,\.() ""$/':;]"; "-") ;"-+";"-"); "[.-]$"; ""))
  s = re.sub(r"[–’+?&=|,\.() \"$/']", "-", s) # replace different characters by a dash
  s = re.sub(r"-+", "-", s) # replace multiple dashes by 1 dash
  s = re.sub(r"[^a-zA-Z0-9\-]", "", s) # strip anything else now that is not a alpha or numeric character or a dash
  s = re.sub(r"^-|-$", "", s) # prevent starting or ending with . or -
  if len(s)==0:
    #raise ValueError("makeSafeURIPart results in empty string")
    # log.warning("makeSafeURIPart results in empty string")
    # fix this by replacing by 'x' for example
    s="x"
  return s.lower()

def makeSafeLiteral(s):
  return re.sub(r"\"", "\\\"", s) # replace " quote by ""

parser = argparse.ArgumentParser(description='csv to ttl')
parser.add_argument('--csv',help='input csv file', required=True)
args = parser.parse_args()

# print prefixes
print('@prefix page: <http://documentatie.org/id/pagina/> .')
print('@prefix kaartsoort: <http://documentatie.org/id/kaartsoort/> .')
print('@prefix trefwoord: <http://documentatie.org/id/trefwoord/> .')
print('@prefix dct: <http://purl.org/dc/terms/> .')
print('@prefix idUDSpaginaURL: <http://www.documentatie.org/idUDSpagina.asp?id=> .')
print('@prefix sdo: <https://schema.org/> .')
print('@prefix def: <http://documentatie.org/def> .')

print()

with open(args.csv, newline='', encoding='utf-8') as f:
  reader = csv.reader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

  try:
    header = next(reader) # skip header

    for row in reader:

      id = row[1]
      url = row[2]
      encodedURL = urllib.parse.quote(url)
      trefwoord = row[3]
      alfabetisering = row[4]
      Iduds = row[6]
      twdURI =  makeSafeURIPart(trefwoord)
      volgnummer = None
      kaartsoort = None

      item = []
      item.append(f'page:{id} dct:subject trefwoord:{twdURI}')
      item.append(f'def:idUDSpaginaURL idUDSpaginaURL:{id}')
      item.append(f'def:fileURL <http://www.documentatie.org{encodedURL}>')

      # volgnummer
      for r in re.findall(r"\[(.*)\]", alfabetisering): # url [0000 0001]
        volgnummer = r
        
      if volgnummer:
        item.append(f'def:volgnummer "{r}"')

      # soort kaart
      for r in re.findall(r"\s_(.*)\s\[", alfabetisering): # 
        if r.find("beginkaart")>-1:
          kaartsoort = "beginkaart"
        else:
          for s in re.findall(r".*(\d[ab]{0,1})", r):   # find number 
            kaartsoort = f'kaart_{s}'
     
      if kaartsoort:
        item.append(f'def:kaartsoort kaartsoort:{kaartsoort}')

      if trefwoord and kaartsoort and volgnummer:
        label = makeSafeLiteral(' - '.join([trefwoord,kaartsoort,volgnummer]))
        item.append(f'rdfs:label "{label}"')

      print(' ; '.join(item) + ' .')



  except csv.Error:
    print("CSV Error",file=sys.stderr)
    pass



