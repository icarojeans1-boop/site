# Baixa as fotos dos stories pedidos em ig/pedido.json para ig/stories/<id>.jpg
# Roda no GitHub Actions (a nuvem do Claude nao consegue baixar do Instagram).
import json, os, time, urllib.request

BASE = 'ig'
PASTA = os.path.join(BASE, 'stories')
DIAS_GUARDAR = 8
os.makedirs(PASTA, exist_ok=True)

pedido = json.load(open(os.path.join(BASE, 'pedido.json'), encoding='utf-8'))
idx_path = os.path.join(PASTA, 'indice.json')
indice = json.load(open(idx_path, encoding='utf-8')) if os.path.exists(idx_path) else {}

ok, erro = [], []
for it in pedido.get('itens', []):
    sid, url = str(it['id']), it['url']
    destino = os.path.join(PASTA, sid + '.jpg')
    if os.path.exists(destino):
        ok.append(sid)
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        dados = urllib.request.urlopen(req, timeout=60).read()
        open(destino, 'wb').write(dados)
        indice[sid] = {k: it.get(k) for k in ('timestamp', 'tipo')}
        indice[sid]['baixado'] = int(time.time())
        ok.append(sid)
    except Exception as e:
        erro.append({'id': sid, 'erro': str(e)[:200]})

# limpeza: apaga fotos com mais de DIAS_GUARDAR dias
limite = time.time() - DIAS_GUARDAR * 86400
for sid in list(indice):
    if indice[sid].get('baixado', 0) < limite:
        for p in (os.path.join(PASTA, sid + '.jpg'),):
            if os.path.exists(p):
                os.remove(p)
        del indice[sid]
pasta_post = os.path.join(BASE, 'post')
if os.path.isdir(pasta_post):
    for f in os.listdir(pasta_post):
        p = os.path.join(pasta_post, f)
        if os.path.getmtime(p) < limite and f[:4].isdigit():
            # nomes AAAA-MM-DD_... : apaga pela data do nome
            try:
                if time.mktime(time.strptime(f[:10], '%Y-%m-%d')) < limite:
                    os.remove(p)
            except ValueError:
                pass

json.dump(indice, open(idx_path, 'w', encoding='utf-8'), indent=0)
json.dump({'pedido': pedido.get('pedido'), 'ok': ok, 'erro': erro, 'quando': int(time.time())},
          open(os.path.join(BASE, 'status.json'), 'w', encoding='utf-8'), indent=0)
print('ok', len(ok), 'erro', len(erro))
