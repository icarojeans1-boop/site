# Guarda para sempre, na galeria do site, as fotos de cada post do dia.
# Le ig/post/*.jpg (que sao apagadas depois de 8 dias), copia uma versao leve
# para img/galeria/ e registra em galeria.json. Nunca apaga nada da galeria.
import json, os
from PIL import Image

POST = os.path.join('ig', 'post')
DEST = os.path.join('img', 'galeria')
IDX = 'galeria.json'
os.makedirs(DEST, exist_ok=True)

gal = json.load(open(IDX, encoding='utf-8')) if os.path.exists(IDX) else {'fotos': []}
ja = {os.path.basename(f['img']) for f in gal['fotos']}

hist = {}
try:
    for p in json.load(open(os.path.join('ig', 'historico.json'), encoding='utf-8')).get('postados', []):
        hist[p['data']] = p
except Exception:
    pass

novas = 0
for nome in sorted(os.listdir(POST)) if os.path.isdir(POST) else []:
    if not nome.lower().endswith('.jpg') or nome in ja or not nome[:4].isdigit():
        continue
    data = nome[:10]
    try:
        im = Image.open(os.path.join(POST, nome)).convert('RGB')
        im.thumbnail((640, 960))
        im.save(os.path.join(DEST, nome), 'JPEG', quality=82, optimize=True, progressive=True)
    except Exception as e:
        print('pulei', nome, e)
        continue
    h = hist.get(data, {})
    gal['fotos'].append({'img': DEST.replace(os.sep, '/') + '/' + nome, 'data': data,
                         'tema': h.get('tema', ''), 'link': h.get('permalink', '')})
    novas += 1

def ordem(f):
    n = os.path.splitext(os.path.basename(f['img']))[0][11:]
    return (f['data'], int(n) if n.isdigit() else 0)
gal['fotos'].sort(key=ordem, reverse=True)
json.dump(gal, open(IDX, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('novas', novas, 'total', len(gal['fotos']))
