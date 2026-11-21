# Baixa as fotos do banner (stories.json) para img/banner/ e grava o caminho
# em "local" de cada item. Assim o site nao depende dos links do Instagram,
# que expiram em poucos dias. Roda no GitHub Actions.
import json, os, re, time, urllib.request
from urllib.parse import urlparse

DEST = os.path.join('img', 'banner')
DIAS_GUARDAR = 30
os.makedirs(DEST, exist_ok=True)

d = json.load(open('stories.json', encoding='utf-8'))
usados, ok, erro = set(), 0, 0
for it in d.get('itens', []):
    url = it.get('img') or ''
    nome = re.sub(r'[^A-Za-z0-9_.-]', '', os.path.basename(urlparse(url).path))[:120]
    if not nome:
        continue
    if not nome.lower().endswith(('.jpg', '.jpeg')):
        nome += '.jpg'
    caminho = os.path.join(DEST, nome)
    if not os.path.exists(caminho):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            dados = urllib.request.urlopen(req, timeout=60).read()
            if len(dados) < 1000:
                raise ValueError('arquivo vazio')
            open(caminho, 'wb').write(dados)
        except Exception as e:
            print('falhou', nome, str(e)[:120])
            erro += 1
            it.pop('local', None)
            continue
    it['local'] = DEST.replace(os.sep, '/') + '/' + nome
    usados.add(nome)
    ok += 1

# limpeza: apaga fotos que sairam do banner ha mais de DIAS_GUARDAR dias
limite = time.time() - DIAS_GUARDAR * 86400
for f in os.listdir(DEST):
    p = os.path.join(DEST, f)
    if f not in usados and os.path.getmtime(p) < limite:
        os.remove(p)
    elif f in usados:
        os.utime(p)

json.dump(d, open('stories.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok', ok, 'erro', erro)
