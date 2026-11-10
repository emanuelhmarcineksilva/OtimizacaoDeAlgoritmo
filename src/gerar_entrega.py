from __future__ import annotations

import html
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from src.experimento import (
    AG_CROSSOVER,
    AG_CROSSOVER_OPERADOR,
    AG_ELITISMO,
    AG_GERACOES,
    AG_MUTACAO,
    AG_POPULACAO,
    AG_TORNEIO,
    APTIDAO_MAXIMA,
    EXECUCOES,
    EXECUCOES_CALIBRACAO,
    FATOR_RESFRIAMENTO,
    N,
    ORCAMENTO,
    ORCAMENTO_CALIBRACAO,
    SEMENTE_BASE,
    TEMPERATURA_INICIAL,
    TEMPERATURA_MINIMA,
    Execucao,
    ExecucaoCalibracao,
)

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("w", W)
ET.register_namespace("r", R)
ET.register_namespace("p", P)
ET.register_namespace("a", A)

NAVY = "16324F"
BLUE = "1D70A2"
TEAL = "2A9D8F"
INK = "243447"
MUTED = "64748B"
LIGHT = "F1F5F9"
WHITE = "FFFFFF"


def _w(tag: str) -> str:
    return f"{{{W}}}{tag}"


def _get_cell_text(cell: ET.Element) -> str:
    return "".join(node.text or "" for node in cell.iter(_w("t")))


def _replace_cell_text(cell: ET.Element, text: str) -> None:
    paragraphs = cell.findall(_w("p"))
    paragraph = paragraphs[0] if paragraphs else ET.SubElement(cell, _w("p"))
    paragraph_properties = paragraph.find(_w("pPr"))
    run_properties = None
    for run in paragraph.findall(_w("r")):
        if run.find(_w("rPr")) is not None:
            run_properties = ET.fromstring(ET.tostring(run.find(_w("rPr"))))
            break
    for child in list(paragraph):
        if child is not paragraph_properties:
            paragraph.remove(child)
    for extra in paragraphs[1:]:
        cell.remove(extra)

    chunks = text.split("\n")
    for index, chunk in enumerate(chunks):
        run = ET.SubElement(paragraph, _w("r"))
        if run_properties is not None:
            run.append(ET.fromstring(ET.tostring(run_properties)))
        value = ET.SubElement(run, _w("t"))
        value.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        value.text = chunk
        if index < len(chunks) - 1:
            ET.SubElement(run, _w("br"))


def _fill_ficha(
    raiz: Path, destino: Path, escolhidas: dict[str, bool | float]
) -> None:
    original = raiz / "TDE3_Ficha_de_Projeto_6A.docx"
    ns = {"w": W}
    with zipfile.ZipFile(original) as arquivo:
        conteudo = {item.filename: arquivo.read(item.filename) for item in arquivo.infolist()}
    document = ET.fromstring(conteudo["word/document.xml"])
    tabelas = document.findall(".//w:tbl", ns)

    _replace_cell_text(tabelas[0].findall("w:tr", ns)[0].findall("w:tc", ns)[1],
                       "Trabalho individual — sem grupo.")

    campos = {
        1: [
            "N-Rainhas (N=30): encontrar uma permutação sem conflitos diagonais.",
            "A representação garante linhas e colunas únicas; trocas locais permitem explorar soluções próximas e a função objetivo é simples.",
        ],
        2: [
            "Permutação s de 0..29; s[c] indica a linha da rainha na coluna c.",
            "30! = 265.252.859.812.191.058.636.308.480.000 estados.",
            "Trocar s[i] e s[j]; C(30,2) = 30×29/2 = 435 vizinhos.",
            "Crossover simples de um ponto pode duplicar genes. No AG usa-se OX: segmento do pai 1 e ordem do pai 2, preservando a permutação; HC e SA não usam crossover. Não foi localizado código executável da Aula 9; CodigoAlgoritmoGenetico.md fornece a especificação.",
            "Minimizar f(s)=Σ(i<j) [|s[i]-s[j]|=|i-j|]. No AG, fitness=435−f(s), maximizado.",
            "Sim. Alvo conhecido: 0 conflitos; existem soluções para N≥4.",
        ],
        3: [
            f"Sorteio aleatório; HC com reinício ({'empate aleatório' if escolhidas['Hill Climbing com reinicio'] else 'primeiro empate'}); SA (α={float(escolhidas['Simulated Annealing']):.3f}); AG (k={AG_POPULACAO}, p_cross={AG_CROSSOVER}, p_mut={float(escolhidas['Algoritmo Genetico']):.2f}, G={AG_GERACOES}, E={AG_ELITISMO}, torneio t={AG_TORNEIO}, OX).",
            "Final: 10.000 avaliações por execução/método. Calibração local e AG: 2 configurações, 5 execuções/configuração, 2.000 avaliações/execução.",
            f"30 execuções finais/método; base {SEMENTE_BASE}; sementes derivadas por método + índice (0–29). Calibração: base + offsets 30000 (HC), 40000 (SA), 60000 (AG) + índice (0–4).",
        ],
    }
    for tabela_id, linhas in campos.items():
        rows = tabelas[tabela_id].findall("w:tr", ns)
        for row, texto in zip(rows, linhas):
            _replace_cell_text(row.findall("w:tc", ns)[1], texto)

    verificacao = tabelas[4].findall("w:tr", ns)
    marcas = {
        1: ("X", "A função `estado_aleatorio()` produz permutações válidas."),
        2: ("X", "`conflitos(s)` conta pares diagonais e incrementa o contador em cada avaliação."),
        3: ("X", f"N=30; APTIDAO_MAXIMA={APTIDAO_MAXIMA}; fitness=APTIDAO_MAXIMA−conflitos."),
        4: ("X", "Sorteio aleatório executado; resultados dos quatro métodos estão nos CSVs."),
        5: ("Pendente", "30! calculado; conferência com o professor ainda pendente."),
    }
    for indice, (marca, texto) in marcas.items():
        celulas = verificacao[indice].findall("w:tc", ns)
        _replace_cell_text(celulas[0], marca)
        _replace_cell_text(celulas[1], texto)

    conteudo["word/document.xml"] = ET.tostring(document, encoding="utf-8", xml_declaration=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as saida:
        for nome, dados in conteudo.items():
            saida.writestr(nome, dados)


def _escape(texto: Any) -> str:
    return html.escape(str(texto), quote=True)


def _tabela_resultados(resumo: list[dict[str, Any]]) -> str:
    linhas = []
    for row in resumo:
        linhas.append(
            "<tr>"
            f"<td>{_escape(row['metodo'])}</td>"
            f"<td>{row['sucessos']}/{row['execucoes']} ({row['taxa_sucesso_pct']}%)</td>"
            f"<td>{_escape(row['avaliacoes_sucesso_media'])} / "
            f"{_escape(row['avaliacoes_sucesso_melhor'])} / "
            f"{_escape(row['avaliacoes_sucesso_pior'])}<br>"
            f"mediana {row['avaliacoes_sucesso_mediana']}; "
            f"DP {row['avaliacoes_sucesso_desvio_padrao']}</td>"
            f"<td>{_escape(row['conflitos_falhas_media'])} / "
            f"{_escape(row['conflitos_falhas_melhor'])} / "
            f"{_escape(row['conflitos_falhas_pior'])}<br>"
            f"mediana {row['conflitos_falhas_mediana']}; "
            f"DP {row['conflitos_falhas_desvio_padrao']}</td>"
            "</tr>"
        )
    return (
        "<table><colgroup><col style='width:22%'><col style='width:14%'>"
        "<col style='width:32%'><col style='width:32%'></colgroup>"
        "<thead><tr><th>Método</th><th>Sucessos</th>"
        "<th>Avaliações até solução<br>(média / mínimo / máximo; mediana; DP)</th>"
        "<th>Melhor conflitos nas falhas<br>(média / mínimo / máximo; mediana; DP)</th>"
        "</tr></thead><tbody>" + "".join(linhas) + "</tbody></table>"
    )


def _resumo_calibracao(
    calibracao: list[ExecucaoCalibracao],
) -> list[dict[str, Any]]:
    resumo = []
    for metodo, configuracao in sorted(
        {(r.metodo, r.configuracao) for r in calibracao}
    ):
        grupo = [
            r for r in calibracao
            if r.metodo == metodo and r.configuracao == configuracao
        ]
        sucessos = [r for r in grupo if r.sucesso]
        custos = [r.avaliacoes_ate_solucao for r in sucessos]
        resumo.append(
            {
                "metodo": metodo,
                "configuracao": configuracao,
                "sucessos": len(sucessos),
                "execucoes": len(grupo),
                "avaliacoes_sucesso_media": (
                    f"{sum(c for c in custos if c is not None) / len(custos):.1f}"
                    if custos
                    else "n/a"
                ),
            }
        )
    return resumo


def _relatorio_html(
    resumo: list[dict[str, Any]],
    resultados: list[Execucao],
    calibracao: list[ExecucaoCalibracao],
    escolhidas: dict[str, bool | float],
) -> str:
    linhas_resultado = {str(row["metodo"]): row for row in resumo}
    aleatorio = linhas_resultado["Sorteio aleatorio"]
    hc = linhas_resultado["Hill Climbing com reinicio"]
    sa = linhas_resultado["Simulated Annealing"]
    ag = linhas_resultado["Algoritmo Genetico"]
    falhas_hc = int(hc["execucoes"]) - int(hc["sucessos"])
    configs_hc = (
        "empate aleatório"
        if escolhidas["Hill Climbing com reinicio"]
        else "primeiro empate"
    )
    exemplo = next(
        (r for r in resultados if r.metodo == "Simulated Annealing" and r.sucesso),
        None,
    )
    if exemplo is None:
        execucao_demo = "Nenhuma execução de Simulated Annealing encontrou solução."
    else:
        execucao_demo = (
            f"Execução SA #{exemplo.execucao}, semente {exemplo.semente}: "
            f"solução em {exemplo.avaliacoes_ate_solucao} avaliações. "
            f"Permutação (início): {exemplo.melhor_estado.split()[:12]} …"
        )
    configuracao_hc = (
        "empate_aleatorio"
        if escolhidas["Hill Climbing com reinicio"]
        else "primeiro_empate"
    )
    calibracao_rows = "".join(
        "<tr>"
        f"<td>{_escape(row['metodo'])}</td>"
        f"<td>{_escape(row['configuracao'])}</td>"
        f"<td>{row['sucessos']}/{row['execucoes']}</td>"
        f"<td>{_escape(row['avaliacoes_sucesso_media'])}</td>"
        "</tr>"
        for row in _resumo_calibracao(calibracao)
    )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><style>
body {{ font-family: Arial, sans-serif; color: #243447; margin: 26px; font-size: 10pt; }}
h1 {{ color: #16324f; font-size: 22pt; margin: 0 0 4px; }}
h2 {{ color: #1d70a2; font-size: 14pt; margin: 12px 0 5px; }}
p, li {{ line-height: 1.25; }}
p {{ margin: 5px 0; }}
table {{ width: 100%; table-layout: fixed; border-collapse: collapse; font-size: 7.5pt; page-break-inside: avoid; }}
thead {{ display: table-header-group; }}
tr {{ page-break-inside: avoid; }}
th {{ background: #16324f; color: white; text-align: left; }}
th, td {{ border: 1px solid #cbd5e1; padding: 5px; overflow-wrap: break-word; }}
tr:nth-child(even) {{ background: #f1f5f9; }}
.note {{ background: #f1f5f9; padding: 10px; border-left: 4px solid #2a9d8f; }}
</style></head><body>
<h1>TDE3 — Otimização</h1>
<p>Inteligência Artificial · PUCPR · Trabalho individual (sem grupo)</p>
<h2>Problema e modelagem</h2>
<p>O problema é encontrar uma configuração das N-Rainhas que minimize pares em conflito
diagonal. Para N={N}, o estado é uma permutação s de 0 a 29: s[c] é a linha da rainha na
coluna c. Assim, há exatamente uma rainha por linha e coluna. O espaço contém
30! ("30 fatorial", 30×29×…×2×1) = 265.252.859.812.191.058.636.308.480.000 estados possíveis;
o algoritmo não enumera todo o espaço. Cada estado tem
C(30,2)=435 vizinhos por troca de duas posições.</p>
<p>A função objetivo minimizada é f(s)=Σ(i&lt;j) [|s[i]−s[j]|=|i−j|]. Conta cada par
diagonal uma vez; o alvo conhecido é zero conflitos. A representação elimina conflitos de
linha e coluna por construção.</p>
<h2>Métodos e protocolo</h2>
<p>Foram comparados sorteio aleatório, Hill Climbing por subida mais íngreme com reinício
aleatório e Simulated Annealing com trocas aleatórias, temperatura inicial
{TEMPERATURA_INICIAL}, resfriamento geométrico e temperatura mínima {TEMPERATURA_MINIMA}
(piso; se não encontrar alvo, segue até o orçamento). No AG, cada indivíduo/cromossomo é a
mesma permutação; fitness=APTIDAO_MAXIMA−conflitos=435−conflitos, para maximizar.</p>
<p>O ciclo genético mantém k={AG_POPULACAO}, usa torneio t={AG_TORNEIO}, elitismo E={AG_ELITISMO},
crossover OX (corte copiado do pai 1; posições restantes preenchidas pela ordem do pai 2)
e mutação por swap de dois genes. Crossover simples de um ponto poderia duplicar valores e
invalidar a permutação. O OX mantém cada linha única. HC e SA continuam como buscas locais;
recombinação é usada apenas pelo AG.</p>
<p>Calibração equilibrada: duas configurações para cada método, {EXECUCOES_CALIBRACAO}
execuções por configuração e {ORCAMENTO_CALIBRACAO:,} avaliações por execução
(mesmo total por método). HC variou desempate; SA variou α; AG variou p_mut (0,02 ou
0,05). A seleção priorizou taxa de sucesso e depois distribuição média dos melhores
conflitos (em caso de empate sem sucessos) ou avaliações até solução. Escolhas: HC
{configuracao_hc}; SA α={float(escolhidas['Simulated Annealing']):.3f}; AG
p_mut={float(escolhidas['Algoritmo Genetico']):.2f}. AG: p_cross={AG_CROSSOVER}, G={AG_GERACOES},
E={AG_ELITISMO}, seleção por torneio t={AG_TORNEIO}, crossover {AG_CROSSOVER_OPERADOR}.</p>
<table><thead><tr><th>Calibração</th><th>Configuração</th><th>Sucessos</th>
<th>Avaliações até solução (média)</th></tr></thead><tbody>{calibracao_rows}</tbody></table>
<p>Cada método teve {EXECUCOES} execuções, orçamento idêntico de {ORCAMENTO:,} avaliações
da função objetivo por execução e sementes reproduzíveis. Semente-base {SEMENTE_BASE};
por método, a semente é base + deslocamento do método (0, 10000, 20000 ou 50000) +
índice da execução (0–29). Calibração usa índices (0–4) e deslocamentos 30000 (HC),
40000 (SA) e 60000 (AG). Uma
avaliação é cada chamada à função de conflitos. Custos de solução consideram apenas
execuções bem-sucedidas; falhas são reportadas separadamente pelo melhor valor obtido.
Calibração e avaliação final foram mantidas separadas. A geração inicial do AG custa k
avaliações; cada geração posterior é reavaliada por inteiro. Uma geração só começa quando
há orçamento para os k indivíduos, sem exceder o teto.</p>
<h2>Resultados observados</h2>
{_tabela_resultados(resumo)}
<p>O CSV bruto contém cada execução, semente, consumo, sucesso, melhor valor e estado.
Todos os métodos usaram o mesmo limite por execução; nenhuma execução excedeu
{ORCAMENTO:,} avaliações.</p>
<p class="note">{_escape(execucao_demo)}</p>
<h2>Análise</h2>
<p>O sorteio encontrou solução em {aleatorio['sucessos']}/{aleatorio['execucoes']}; HC
({configs_hc}) em {hc['sucessos']}/{hc['execucoes']} ({hc['taxa_sucesso_pct']}%); SA
(α={float(escolhidas['Simulated Annealing']):.3f}) em {sa['sucessos']}/{sa['execucoes']}
({sa['taxa_sucesso_pct']}%); AG em {ag['sucessos']}/{ag['execucoes']}
({ag['taxa_sucesso_pct']}%). Custos médios/mínimos/máximos até solução, apenas entre
sucessos: HC {hc['avaliacoes_sucesso_media']}/{hc['avaliacoes_sucesso_melhor']}/
{hc['avaliacoes_sucesso_pior']}; SA {sa['avaliacoes_sucesso_media']}/
{sa['avaliacoes_sucesso_melhor']}/{sa['avaliacoes_sucesso_pior']}; AG
{ag['avaliacoes_sucesso_media']}/{ag['avaliacoes_sucesso_melhor']}/
{ag['avaliacoes_sucesso_pior']}. As médias, medianas e desvios estão na tabela; não se
conclui superioridade universal de uma amostra de 30 execuções.</p>
<p>A representação por permutação reduz estados inválidos e a vizinhança de 435 trocas é
enumerável para o HC. O HC pode parar em ótimos locais, como mostram as falhas com um
conflito. O SA pode aceitar movimentos piores com probabilidade dependente da temperatura,
permitindo escapar de alguns ótimos locais, sem garantia de ótimo. O sorteio puro é uma
linha de base simples. O AG diversifica por população, torneio, elitismo, OX e mutação por
swap; o elitismo preserva a melhor aptidão observada na população, mas não garante o ótimo
global. Consulte a taxa de sucesso e a distribuição das falhas na tabela para comparar os
resultados observados.</p>
<h2>Limitações e divergências</h2>
<ul>
<li>30 execuções finais por método e uma calibração piloto pequena não caracterizam todos os cenários;
não foi feita análise estatística inferencial.</li>
<li>Resfriamento geométrico no Simulated Annealing não garante encontrar o ótimo. O Hill
Climbing também não oferece garantia de encontrar solução dentro do orçamento.</li>
<li>Resultados dependem da semente, orçamento e implementação; o estudo mede avaliações,
não tempo de parede.</li>
<li>A ficha cita uma base genética na Aula 9, mas esse notebook/código executável não foi
localizado no workspace. Foi localizado o roteiro `CodigoAlgoritmoGenetico.md` e o notebook
real da Aula 8; o AG foi implementado segundo o roteiro e a modelagem por permutação.</li>
</ul>
</body></html>"""


def _xml(texto: str) -> str:
    return html.escape(texto, quote=False)


def _pptx_shape(
    shape_id: int,
    nome: str,
    x: int,
    y: int,
    largura: int,
    altura: int,
    texto: str = "",
    tamanho: int = 1800,
    cor: str = INK,
    preenchimento: str | None = None,
    negrito: bool = False,
) -> str:
    if preenchimento:
        fill = f'<a:solidFill><a:srgbClr val="{preenchimento}"/></a:solidFill>'
        line = '<a:ln><a:noFill/></a:ln>'
    else:
        fill = "<a:noFill/>"
        line = "<a:ln><a:noFill/></a:ln>"
    paragraphs = []
    for linha in texto.split("\n"):
        bold = ' b="1"' if negrito else ""
        paragraphs.append(
            f'<a:p><a:pPr/><a:r><a:rPr lang="pt-BR" sz="{tamanho}"{bold}>'
            f'<a:solidFill><a:srgbClr val="{cor}"/></a:solidFill>'
            f'<a:latin typeface="Aptos"/></a:rPr><a:t>{_xml(linha)}</a:t></a:r>'
            f'<a:endParaRPr lang="pt-BR" sz="{tamanho}"/></a:p>'
        )
    corpo = "".join(paragraphs) if paragraphs else "<a:p/>"
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{_xml(nome)}"/>
<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm>
<a:off x="{x}" y="{y}"/><a:ext cx="{largura}" cy="{altura}"/></a:xfrm>
<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill}{line}</p:spPr>
<p:txBody><a:bodyPr wrap="square" lIns="120000" tIns="80000" rIns="120000" bIns="80000"/>
<a:lstStyle/>{corpo}</p:txBody></p:sp>"""


def _slide_xml(shapes: list[str]) -> bytes:
    body = "".join(shapes)
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}" showMasterSp="0">
<p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>
<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>
<a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>
<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>{body}</p:spTree></p:cSld>
<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"""
    return xml.encode("utf-8")


def _slides(
    resumo: list[dict[str, Any]],
    resultados: list[Execucao],
    calibracao: list[ExecucaoCalibracao],
    escolhidas: dict[str, bool | float],
) -> list[bytes]:
    linhas_resultado = {str(row["metodo"]): row for row in resumo}
    hc = linhas_resultado["Hill Climbing com reinicio"]
    sa = linhas_resultado["Simulated Annealing"]
    ag = linhas_resultado["Algoritmo Genetico"]
    slide_list: list[list[str]] = []
    titulo_y = 300_000
    content_y = 1_200_000
    calibracao_resumida = _resumo_calibracao(calibracao)
    linhas_calibracao = []
    for row in calibracao_resumida:
        linhas_calibracao.append(
            f"{row['metodo']} {row['configuracao']}: "
            f"{row['sucessos']}/{row['execucoes']} sucessos"
        )
    resumo_calibracao_slides = "\n".join(linhas_calibracao)
    slide_list.append([
        _pptx_shape(2, "Título", 650_000, 1_100_000, 11_000_000, 1_000_000,
                    "N-Rainhas: busca e otimização", 3000, WHITE, NAVY, True),
        _pptx_shape(3, "Subtítulo", 800_000, 2_500_000, 10_500_000, 800_000,
                    "TDE3 · Inteligência Artificial · Trabalho individual", 2000, MUTED),
        _pptx_shape(4, "N", 800_000, 4_000_000, 3_400_000, 1_200_000,
                    "N = 30", 3200, WHITE, BLUE, True),
        _pptx_shape(5, "Alvo", 4_700_000, 4_000_000, 3_400_000, 1_200_000,
                    "Alvo: 0 conflitos", 2600, WHITE, TEAL, True),
        _pptx_shape(6, "Resumo", 8_600_000, 4_000_000, 3_700_000, 1_200_000,
                    "Comparação por avaliações de f", 1800, WHITE, NAVY, True),
    ])
    slide_list.append([
        _pptx_shape(2, "Título", 500_000, titulo_y, 11_500_000, 600_000,
                    "Modelagem", 2800, NAVY, None, True),
        _pptx_shape(3, "Texto", 700_000, content_y, 11_000_000, 4_900_000,
                    "Representação: permutação s de 0..29; s[c] é a linha da rainha na coluna c.\n"
                    "Por construção: uma rainha por linha e por coluna.\n"
                    "Espaço: |S| = 30! (30×29×…×1) = 265.252.859.812.191.058.636.308.480.000 possíveis; não enumeramos todos.\n"
                    "Vizinhança: trocar duas posições; C(30,2) = 435 vizinhos.\n"
                    "Objetivo: minimizar conflitos diagonais. Fitness AG=435−conflitos.\n"
                    "Crossover de 1 ponto pode duplicar genes; OX preserva permutação: segmento do pai 1, ordem restante do pai 2.",
                    2100, INK),
    ])
    slide_list.append([
        _pptx_shape(2, "Título", 500_000, titulo_y, 11_500_000, 600_000,
                    "Métodos e protocolo", 2800, NAVY, None, True),
        _pptx_shape(3, "Métodos", 700_000, content_y, 5_300_000, 4_800_000,
                    "Sorteio aleatório\nPermutações independentes; linha de base.\n\n"
                    "Hill Climbing com reinício\nAvalia trocas; reinicia sem melhoria.\n\n"
                    "Simulated Annealing\nTroca aleatória; pode aceitar pioras.\n\n"
                    "Algoritmo Genético\nPopulação; torneio t=3; OX; mutação swap; elitismo.",
                    1750, INK, LIGHT),
        _pptx_shape(4, "Comparabilidade", 6_400_000, content_y, 5_700_000, 4_800_000,
                    "30 execuções por método\n10.000 avaliações de f por execução\n"
                    "Unidade comum: chamadas à função objetivo\nSemente-base: 20261109; sementes derivadas por método/execução\n"
                    "Calibração: 2 configs/método, 5×2000 avaliações/config\n"
                    f"Escolhidos: HC {'empate aleatório' if escolhidas['Hill Climbing com reinicio'] else 'primeiro empate'}; "
                    f"SA α={float(escolhidas['Simulated Annealing']):.3f}; "
                    f"AG p_mut={float(escolhidas['Algoritmo Genetico']):.2f}\n"
                    f"AG: k={AG_POPULACAO}, p_cross={AG_CROSSOVER}, G={AG_GERACOES}, E={AG_ELITISMO}; OX; torneio t={AG_TORNEIO}.\n"
                    f"Calibração (sucessos/config):\n{resumo_calibracao_slides}",
                    1500, INK, LIGHT),
    ])
    exemplo = next(
        (r for r in resultados if r.metodo == "Simulated Annealing" and r.sucesso),
        None,
    )
    demonstracao = (
        "Sem solução nesta amostra."
        if exemplo is None
        else f"Semente {exemplo.semente} · sucesso em {exemplo.avaliacoes_ate_solucao} avaliações\n"
             f"Conflitos finais: 0\nPermutação (12 primeiras posições): "
             f"{' '.join(exemplo.melhor_estado.split()[:12])} …"
    )
    slide_list.append([
        _pptx_shape(2, "Título", 500_000, titulo_y, 11_500_000, 600_000,
                    "Execução observada", 2800, NAVY, None, True),
        _pptx_shape(3, "Contador", 700_000, content_y, 11_000_000, 1_200_000,
                    demonstracao, 2100, INK, LIGHT),
        _pptx_shape(4, "Nota", 700_000, 3_000_000, 11_000_000, 2_300_000,
                    "Amostra real do CSV bruto. O estado completo e cada chamada estão registrados em resultados.csv.",
                    1900, MUTED),
    ])

    linhas_tabela = [
        "Método | Sucesso | Avaliações até solução (média/mediana/mín/máx; DP) | Conflitos nas falhas (média/mín/máx)"
    ]
    for row in resumo:
        linhas_tabela.append(
            f"{row['metodo']} | {row['sucessos']}/{row['execucoes']} "
            f"({row['taxa_sucesso_pct']}%) | "
            f"{row['avaliacoes_sucesso_media']}/{row['avaliacoes_sucesso_mediana']}/"
            f"{row['avaliacoes_sucesso_melhor']}/{row['avaliacoes_sucesso_pior']};"
            f" DP {row['avaliacoes_sucesso_desvio_padrao']} | "
            f"{row['conflitos_falhas_media']}/{row['conflitos_falhas_melhor']}/"
            f"{row['conflitos_falhas_pior']}"
        )
    slide_list.append([
        _pptx_shape(2, "Título", 500_000, titulo_y, 11_500_000, 600_000,
                    "Resultados — N=30, orçamento 10.000", 2600, NAVY, None, True),
        _pptx_shape(3, "Tabela", 500_000, content_y, 12_000_000, 4_900_000,
                    "\n".join(linhas_tabela), 1150, INK, LIGHT),
        _pptx_shape(4, "Nota", 500_000, 6_250_000, 12_000_000, 500_000,
                    "Custos de solução calculados apenas nos sucessos; falhas permanecem na taxa e no melhor conflito.",
                    1300, MUTED),
    ])
    slide_list.append([
        _pptx_shape(2, "Título", 500_000, titulo_y, 11_500_000, 600_000,
                    "Limitações e conclusões", 2800, NAVY, None, True),
        _pptx_shape(3, "Texto", 700_000, content_y, 11_000_000, 4_900_000,
                    f"Resultados desta amostra: sorteio {linhas_resultado['Sorteio aleatorio']['sucessos']}/30; "
                    f"HC {hc['sucessos']}/30; SA {sa['sucessos']}/30; AG {ag['sucessos']}/30.\n"
                    "HC pode ficar preso em ótimos locais; SA aceita pioras probabilisticamente, mas resfriamento geométrico não garante o ótimo.\n"
                    "AG com elitismo preserva a melhor aptidão observada, não garante o ótimo global.\n"
                    "Nenhum método tem garantia de solução no orçamento. 30 execuções e calibração piloto pequena limitam a generalização.\n"
                    "Não foi localizado código executável da Aula 9; CodigoAlgoritmoGenetico.md forneceu a especificação.",
                    1700, INK, LIGHT),
    ])

    return [_slide_xml(shapes) for shapes in slide_list]


def _write_pptx(
    destino: Path,
    resumo: list[dict[str, Any]],
    resultados: list[Execucao],
    calibracao: list[ExecucaoCalibracao],
    escolhidas: dict[str, bool | float],
) -> None:
    slides = _slides(resumo, resultados, calibracao, escolhidas)
    content_types = [f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' for i in range(1, len(slides) + 1)]
    rels = [f'<Relationship Id="rId{i+1}" Type="{R}/slide" Target="slides/slide{i}.xml"/>' for i in range(1, len(slides) + 1)]
    ids = [f'<p:sldId id="{255+i}" r:id="rId{i+1}"/>' for i in range(1, len(slides) + 1)]
    presentation = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}">
<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
<p:sldIdLst>{''.join(ids)}</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="wide"/>
<p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>"""
    presentation_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/slideMaster" Target="slideMasters/slideMaster1.xml"/>
{''.join(rels)}</Relationships>"""
    master = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}"><p:cSld><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
</p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2"
accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4"
accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
<p:sldLayoutIdLst><p:sldLayoutId id="1" r:id="rId1"/></p:sldLayoutIdLst>
<p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>"""
    master_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>"""
    layout = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}" type="blank" preserve="1">
<p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>
<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/>
<a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm>
</p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"""
    layout_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/slideMaster" Target="../slideMasters/slideMaster1.xml"/></Relationships>"""
    theme = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="{A}" name="TDE3"><a:themeElements><a:clrScheme name="TDE3">
<a:dk1><a:srgbClr val="{NAVY}"/></a:dk1><a:lt1><a:srgbClr val="{WHITE}"/></a:lt1>
<a:dk2><a:srgbClr val="{INK}"/></a:dk2><a:lt2><a:srgbClr val="{LIGHT}"/></a:lt2>
<a:accent1><a:srgbClr val="{BLUE}"/></a:accent1><a:accent2><a:srgbClr val="{TEAL}"/></a:accent2>
<a:accent3><a:srgbClr val="E9C46A"/></a:accent3><a:accent4><a:srgbClr val="E76F51"/></a:accent4>
<a:accent5><a:srgbClr val="64748B"/></a:accent5><a:accent6><a:srgbClr val="94A3B8"/></a:accent6>
<a:hlink><a:srgbClr val="{BLUE}"/></a:hlink><a:folHlink><a:srgbClr val="64748B"/></a:folHlink>
</a:clrScheme><a:fontScheme name="TDE3"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont>
<a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
<a:fmtScheme name="TDE3"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
</a:fmtScheme></a:themeElements></a:theme>"""
    content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="{CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{''.join(content_types)}</Types>"""
    root_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/officeDocument" Target="ppt/presentation.xml"/></Relationships>"""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as pacote:
        pacote.writestr("[Content_Types].xml", content.encode())
        pacote.writestr("_rels/.rels", root_rels.encode())
        pacote.writestr("ppt/presentation.xml", presentation.encode())
        pacote.writestr("ppt/_rels/presentation.xml.rels", presentation_rels.encode())
        pacote.writestr("ppt/slideMasters/slideMaster1.xml", master.encode())
        pacote.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels.encode())
        pacote.writestr("ppt/slideLayouts/slideLayout1.xml", layout.encode())
        pacote.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels.encode())
        pacote.writestr("ppt/theme/theme1.xml", theme.encode())
        for indice, slide in enumerate(slides, 1):
            pacote.writestr(f"ppt/slides/slide{indice}.xml", slide)
            rel = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="{REL}"><Relationship Id="rId1" Type="{R}/slideLayout" Target="../slideLayouts/slideLayout1.xml"/></Relationships>"""
            pacote.writestr(f"ppt/slides/_rels/slide{indice}.xml.rels", rel.encode())


def gerar_entrega(
    raiz: Path,
    resultados: list[Execucao],
    resumo: list[dict[str, Any]],
    calibracao: list[ExecucaoCalibracao],
    escolhidas: dict[str, bool | float],
) -> None:
    pasta = raiz / "entrega"
    pasta.mkdir(parents=True, exist_ok=True)
    backups = raiz / "backups" / "originais"
    backups.mkdir(parents=True, exist_ok=True)
    for nome in ("Aula8_Laboratorio_Estudante.ipynb", "TDE3_Ficha_de_Projeto_6A.docx"):
        origem = raiz / nome
        backup = backups / nome
        if origem.exists() and not backup.exists():
            shutil.copy2(origem, backup)

    _fill_ficha(raiz, pasta / "TDE3_Ficha_Preenchida.docx", escolhidas)
    html_relatorio = _relatorio_html(resumo, resultados, calibracao, escolhidas)
    soffice = shutil.which("libreoffice") or shutil.which("soffice")
    if soffice is None:
        raise RuntimeError("LibreOffice/soffice é necessário para gerar o PDF do relatório.")
    with tempfile.TemporaryDirectory(prefix="tde3-") as temporario:
        html_path = Path(temporario) / "Relatorio_TDE3.html"
        html_path.write_text(html_relatorio, encoding="utf-8")
        subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(pasta),
                str(html_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        _write_pptx(
            Path(temporario) / "Apresentacao_TDE3.pptx",
            resumo,
            resultados,
            calibracao,
            escolhidas,
        )
        subprocess.run(
            [
                soffice,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                temporario,
                str(Path(temporario) / "Apresentacao_TDE3.pptx"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        pdf_apresentacao = Path(temporario) / "Apresentacao_TDE3.pdf"
        if not pdf_apresentacao.exists() or pdf_apresentacao.stat().st_size == 0:
            raise RuntimeError("A apresentação PPTX não abriu no LibreOffice.")
        shutil.copy2(
            Path(temporario) / "Apresentacao_TDE3.pptx",
            pasta / "Apresentacao_TDE3.pptx",
        )


if __name__ == "__main__":
    from src.experimento import calibrar_metodos, executar_experimentos, resumir

    dados_calibracao, parametros = calibrar_metodos()
    dados = executar_experimentos(
        desempate_hc=bool(parametros["Hill Climbing com reinicio"]),
        alfa_sa=float(parametros["Simulated Annealing"]),
        mutacao_ag=float(parametros["Algoritmo Genetico"]),
    )
    gerar_entrega(
        Path(__file__).resolve().parents[1],
        dados,
        resumir(dados),
        dados_calibracao,
        parametros,
    )
