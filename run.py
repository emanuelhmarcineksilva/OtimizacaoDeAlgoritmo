from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from src import experimento
from src.gerar_entrega import gerar_entrega


def main() -> None:
    raiz = Path(__file__).resolve().parent
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=raiz,
        check=True,
    )
    calibracao, escolhidas = experimento.calibrar_metodos()
    if any(r.avaliacoes > r.orcamento for r in calibracao):
        raise RuntimeError("Uma execucao de calibracao excedeu o orcamento definido.")
    resultados = experimento.executar_experimentos(
        desempate_hc=bool(escolhidas["Hill Climbing com reinicio"]),
        alfa_sa=float(escolhidas["Simulated Annealing"]),
        mutacao_ag=float(escolhidas["Algoritmo Genetico"]),
    )
    if any(r.avaliacoes > r.orcamento for r in resultados):
        raise RuntimeError("Uma execucao excedeu o orcamento definido.")
    pasta_entrega = raiz / "entrega"
    experimento.salvar_resultados(resultados, pasta_entrega / "resultados.csv")
    experimento.salvar_calibracao(calibracao, pasta_entrega / "calibracao.csv")
    resumo = experimento.resumir(resultados)
    experimento.salvar_resumo(resumo, pasta_entrega / "tabela_resumo.csv")
    gerar_entrega(raiz, resultados, resumo, calibracao, escolhidas)

    for linha in resumo:
        print(
            f"{linha['metodo']}: {linha['sucessos']}/{linha['execucoes']} sucessos "
            f"({linha['taxa_sucesso_pct']}%); avaliacoes ate solucao "
            f"media/mediana/DP/melhor/pior={linha['avaliacoes_sucesso_media']}/"
            f"{linha['avaliacoes_sucesso_mediana']}/"
            f"{linha['avaliacoes_sucesso_desvio_padrao']}/"
            f"{linha['avaliacoes_sucesso_melhor']}/"
            f"{linha['avaliacoes_sucesso_pior']}; conflitos nas falhas "
            f"media/melhor/pior={linha['conflitos_falhas_media']}/"
            f"{linha['conflitos_falhas_melhor']}/"
            f"{linha['conflitos_falhas_pior']}"
        )
    print(f"Entrega pronta em: {pasta_entrega}")


if __name__ == "__main__":
    main()
