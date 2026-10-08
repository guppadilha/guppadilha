import datetime as dt
import re
import sys
import urllib.request
from pathlib import Path

USUARIO = "guppadilha"
SAIDA = Path(__file__).resolve().parent.parent / "contribuicoes.svg"


# Calendário público de contribuições
def calendario(usuario):
    pedido = urllib.request.Request(
        f"https://github.com/users/{usuario}/contributions",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    html = urllib.request.urlopen(pedido, timeout=30).read().decode("utf-8")
    datas = dict(re.findall(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="([^"]+)"', html))
    datas = {id_: data for data, id_ in datas.items()}
    dias = {}
    for id_, texto in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        if id_ not in datas:
            continue
        numero = re.match(r"\s*(\d+) contribution", texto)
        dias[dt.date.fromisoformat(datas[id_])] = int(numero.group(1)) if numero else 0
    if not dias:
        sys.exit("calendario vazio")
    return dict(sorted(dias.items()))


# Sequências de dias com contribuição
def sequencias(dias):
    hoje = max(dias)
    atual = 0
    dia = hoje if dias[hoje] else hoje - dt.timedelta(days=1)
    while dias.get(dia, 0):
        atual += 1
        dia -= dt.timedelta(days=1)
    maior = corrente = 0
    for quantidade in dias.values():
        corrente = corrente + 1 if quantidade else 0
        maior = max(maior, corrente)
    return atual, maior


def numero(valor):
    return f"{valor:,}".replace(",", ".")


# Card em SVG
def svg(total, atual, maior):
    colunas = [
        (numero(total), "Contribuições no último ano"),
        (f"{atual} {'dia' if atual == 1 else 'dias'}", "Sequência atual"),
        (f"{maior} {'dia' if maior == 1 else 'dias'}", "Maior sequência"),
    ]
    blocos = "".join(
        f'<text x="{90 + i * 160}" y="62" class="valor" fill="#1f2328" text-anchor="middle" font-size="24" font-weight="700" font-family="Segoe UI, Helvetica, Arial, sans-serif">{valor}</text>'
        f'<text x="{90 + i * 160}" y="88" class="rotulo" fill="#59636e" text-anchor="middle" font-size="12" font-family="Segoe UI, Helvetica, Arial, sans-serif">{rotulo}</text>'
        for i, (valor, rotulo) in enumerate(colunas)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="480" height="120" viewBox="0 0 480 120" role="img" aria-label="Contribuições no GitHub">
<style>
.fundo {{ fill: #ffffff; stroke: #e1e4e8; }}
.valor {{ font: 700 24px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: #1f2328; text-anchor: middle; }}
.rotulo {{ font: 400 12px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; fill: #59636e; text-anchor: middle; }}
.linha {{ stroke: #e1e4e8; }}
@media (prefers-color-scheme: dark) {{
  .fundo {{ fill: #0d1117; stroke: #30363d; }}
  .valor {{ fill: #f0f6fc; }}
  .rotulo {{ fill: #9198a1; }}
  .linha {{ stroke: #30363d; }}
}}
</style>
<rect class="fundo" fill="#ffffff" stroke="#e1e4e8" x="0.5" y="0.5" width="479" height="119" rx="8"/>
<line class="linha" stroke="#e1e4e8" x1="170" y1="30" x2="170" y2="96"/>
<line class="linha" stroke="#e1e4e8" x1="330" y1="30" x2="330" y2="96"/>
{blocos}
</svg>
"""


if __name__ == "__main__":
    dias = calendario(USUARIO)
    atual, maior = sequencias(dias)
    SAIDA.write_text(svg(sum(dias.values()), atual, maior), encoding="utf-8")
    print(f"total {sum(dias.values())} | sequencia atual {atual} | maior {maior}")
