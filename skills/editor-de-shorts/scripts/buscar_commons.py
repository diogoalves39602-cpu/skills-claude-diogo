"""Busca imagens livres no Wikimedia Commons (sem NC/GFDL, largura >= 900). Uso: python buscar_commons.py "termo 1" "termo 2"
Leia os titulos antes de baixar: buscas genericas podem trazer conteudo adulto."""
import json,sys,urllib.parse,urllib.request,time
sys.stdout.reconfigure(encoding="utf-8")
for q in sys.argv[1:]:
  for tries in range(4):
    try:
      u="https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=12&gsrsearch="+urllib.parse.quote(q+" filetype:bitmap")+"&prop=imageinfo&iiprop=size|extmetadata&iiextmetadatafilter=LicenseShortName"
      d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"ShortsVideoBot/1.0 (diogoalves39602@gmail.com)"})))
      break
    except Exception as e: time.sleep(8)
  print("==",q)
  for p in d.get('query',{}).get('pages',{}).values():
    ii=p['imageinfo'][0]; lic=ii['extmetadata'].get('LicenseShortName',{}).get('value','')
    if ii['width']>=900 and 'NC' not in lic and 'GFDL' not in lic: print(f"  {ii['width']}x{ii['height']} {lic} | {p['title'][5:]}")
  time.sleep(3)
