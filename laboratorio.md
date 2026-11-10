{
 "nbformat": 4,
 "nbformat_minor": 0,
 "metadata": {
  "colab": {
   "provenance": [],
   "toc_visible": true
  },
  "kernelspec": {
   "name": "python3",
   "display_name": "Python 3"
  },
  "language_info": {
   "name": "python"
  }
 },
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "# Inteligência Artificial (PCO118A) — Aula 8: Busca Local\n**Prof. Carlos Costa Cedro** · Bacharelado em Ciência da Computação · PUCPR\n\nComplete as **seis lacunas** marcadas com `TODO`. Execute as células na ordem."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "O problema é o das **oito rainhas**: posicionar oito rainhas em um tabuleiro 8×8 sem que\nnenhuma ataque outra.\n\nA espinha dorsal deste laboratório é o **contador de avaliações da função objetivo**.\nEle é instrumentado na lacuna 1 e usado até o fim. É ele que torna possível a comparação\njusta da lacuna 6, e é o hábito que o TDE3 vai cobrar.\n\n> **Sobre reprodutibilidade.** Os métodos desta aula são estocásticos: duas execuções dão\n> resultados diferentes. As verificações automáticas usam **faixas**, e não valores exatos.\n> Um laboratório que exigisse igualdade exata de um valor estocástico estaria ensinando a\n> coisa errada. Anote sempre a semente que você usou."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "# ============================================================\n# CÓDIGO FORNECIDO — não altere\n# ============================================================\nimport random, math, time\n\nN = 8\n\n# Contador global de avaliações da função objetivo.\n# TODA chamada a conflitos() deve incrementá-lo.\nAVALIACOES = 0\n\ndef zerar():\n    global AVALIACOES\n    AVALIACOES = 0\n\ndef mostrar(s):\n    \"\"\"s[c] = linha da rainha na coluna c.\"\"\"\n    for r in range(N):\n        print(' '.join('Q' if s[c] == r else '.' for c in range(N)))\n\nprint('Setup carregado.')\nmostrar([0, 4, 7, 5, 2, 6, 1, 3])"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lacuna 1 — representação e função objetivo\n\n**Representação A, vetor livre.** O estado é uma lista de 8 posições; `s[c]` é a linha da\nrainha da coluna c. Como há exatamente uma rainha por coluna, conflitos de coluna são\nimpossíveis por construção.\n\nImplemente `conflitos(s)`: o número de **pares** de rainhas que se atacam. Duas rainhas nas\ncolunas i e j se atacam se estão na mesma linha (`s[i] == s[j]`) ou na mesma diagonal\n(`abs(s[i] - s[j]) == j - i`).\n\nNão esqueça de incrementar `AVALIACOES`."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "def conflitos(s):\n    global AVALIACOES\n    # TODO: incrementar AVALIACOES e contar os pares que se atacam\n    raise NotImplementedError('lacuna 1')"
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "# Testes de sanidade (fornecidos)\nassert conflitos([0, 4, 7, 5, 2, 6, 1, 3]) == 0, 'esta é uma solução conhecida'\nassert conflitos([0, 1, 2, 3, 4, 5, 6, 7]) == 28, 'diagonal principal: todos os pares se atacam'\nassert conflitos([0, 0, 0, 0, 0, 0, 0, 0]) == 28, 'todas na mesma linha'\nassert conflitos([0, 2, 4, 6, 1, 3, 5, 7]) == 1, 'quase uma solução: resta um par em diagonal'\nassert conflitos([0, 5, 7, 2, 6, 3, 1, 4]) == 0, 'outra das 92 soluções'\n\nprint(f'espaço de estados da representação A: {N**N} = {N}^{N}')\nprint('Lacuna 1: OK')"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lacuna 2 — Hill Climbing por subida mais íngreme\n\nO problema é de **minimização**: queremos zero conflitos. O algoritmo é o da seção 3.3.1\ndo material teórico, com o sinal invertido.\n\nVizinhança: mover **uma** rainha para outra casa da **mesma coluna**. São 8 × 7 = 56 vizinhos.\n\n`hill_climbing(s)` devolve `(conflitos_finais, passos)`. Em caso de empate entre vizinhos\nigualmente bons, sorteie um deles.\n\n> **Atenção.** Só aceite melhora **estrita**. Aceitar empate faz o algoritmo passear\n> indefinidamente em platôs."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "def hill_climbing(s):\n    s = list(s)\n    passos = 0\n    while True:\n        # TODO: avaliar os 56 vizinhos, achar o melhor valor;\n        #       se nenhum for estritamente melhor que o atual, devolver (conflitos(s), passos);\n        #       senão sortear entre os melhores, mover e contar o passo\n        raise NotImplementedError('lacuna 2')"
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "def estado_vetor():\n    return [random.randrange(N) for _ in range(N)]\n\ndef experimento(hc, gerador, n=1000, semente=42):\n    random.seed(semente)\n    sucessos, p_ok, p_fail = 0, [], []\n    for _ in range(n):\n        h, p = hc(gerador())\n        if h == 0: sucessos += 1; p_ok.append(p)\n        else:                     p_fail.append(p)\n    return (sucessos / n,\n            sum(p_ok) / max(len(p_ok), 1),\n            sum(p_fail) / max(len(p_fail), 1))\n\nt = time.time()\ntaxa_A, pok_A, pfa_A = experimento(hill_climbing, estado_vetor)\nprint(f'representação A (vetor), 1000 instâncias, semente 42')\nprint(f'  taxa de sucesso       = {100*taxa_A:.1f}%')\nprint(f'  passos médios sucesso = {pok_A:.1f}')\nprint(f'  passos médios falha   = {pfa_A:.1f}')\nprint(f'  tempo = {time.time()-t:.1f} s')\n\nassert 0.10 <= taxa_A <= 0.18, 'esperado algo em torno de 13% a 14%'\nprint('\\nLacuna 2: OK')"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Para o relatório\n\nO algoritmo **falha em cerca de 86% dos casos**, e falha em pouco mais de 3 passos.\nUm espaço de quase 17 milhões de estados é atravessado em três ou quatro movimentos.\n\n**Isso é defeito ou é a assinatura do método?** Justifique em uma frase."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lacuna 3 — trocar a representação\n\n**Representação B, permutação.** O estado é uma permutação de 0 a 7: `s[c]` continua sendo\na linha da rainha da coluna c, mas nenhuma linha se repete. Conflitos de linha passam a ser\nimpossíveis **por construção**, e só sobram os diagonais.\n\nVizinhança: **trocar** as linhas de duas colunas. São C(8,2) = 28 vizinhos.\n\nA função objetivo é a **mesma**: `conflitos(s)` não muda. O algoritmo é o **mesmo**: subida\nmais íngreme. Só a vizinhança muda."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "def hill_climbing_perm(s):\n    s = list(s)\n    passos = 0\n    while True:\n        # TODO: mesma estrutura da lacuna 2, mas a vizinhança é trocar s[i] com s[j]\n        raise NotImplementedError('lacuna 3')\n\ndef estado_perm():\n    return random.sample(range(N), N)"
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "taxa_B, pok_B, pfa_B = experimento(hill_climbing_perm, estado_perm)\n\nprint(f\"{'':<26}{'A (vetor)':>12}{'B (permutação)':>17}\")\nprint(f\"{'tamanho do espaço':<26}{N**N:>12}{math.factorial(N):>17}\")\nprint(f\"{'vizinhos por estado':<26}{N*(N-1):>12}{math.comb(N,2):>17}\")\nprint(f\"{'taxa de sucesso':<26}{100*taxa_A:>11.1f}%{100*taxa_B:>16.1f}%\")\nprint(f\"{'passos médios (sucesso)':<26}{pok_A:>12.1f}{pok_B:>17.1f}\")\nprint(f\"{'passos médios (falha)':<26}{pfa_A:>12.1f}{pfa_B:>17.1f}\")\n\nassert taxa_B > 2 * taxa_A, 'a representação B deve ser muito melhor'\nprint('\\nLacuna 3: OK')"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Para o relatório\n\nA taxa de sucesso salta sem que **uma linha do algoritmo** mude. **Explique o mecanismo**,\ne não apenas o fato: que tipo de conflito a representação B torna impossível por\nconstrução, e o que isso faz com a paisagem que o algoritmo percorre?"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lacuna 4 — reinício aleatório e o Teorema 2\n\nO Teorema 2 diz que, se cada execução independente tem probabilidade p de sucesso, o número\nesperado de execuções até o primeiro sucesso é **1/p**.\n\nImplemente `reinicio_aleatorio()`, que executa Hill Climbing repetidamente a partir de\nestados sorteados até obter zero conflitos, devolvendo quantas execuções foram necessárias.\nDepois compare a média observada com a previsão do teorema."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "def reinicio_aleatorio(hc, gerador):\n    # TODO: repetir hc(gerador()) até obter 0 conflitos; devolver o número de execuções\n    raise NotImplementedError('lacuna 4')"
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "random.seed(7)\nM = 2000\ntentativas = [reinicio_aleatorio(hill_climbing, estado_vetor) for _ in range(M)]\nmedia = sum(tentativas) / M\n\nprint(f'reinícios médios até o sucesso (medido, {M} execuções) = {media:.2f}')\nprint(f'p implicado por 1/média                                = {1/media:.4f}')\nprint(f'p medido na lacuna 2                                   = {taxa_A:.4f}')\nprint(f'previsão do Teorema 2 com o p da lacuna 2 (1/p)        = {1/taxa_A:.2f}')\nprint(f'maior número de reinícios observado                    = {max(tentativas)}')\n\nassert abs(1/media - taxa_A) < 0.04, 'previsão e medição devem concordar'\nprint('\\nLacuna 4: OK')"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Para o relatório\n\n1. O p implicado pela média de reinícios e o p medido na lacuna 2 não são idênticos.\n   **Isso invalida o Teorema 2?** Justifique em termos de variação amostral.\n2. Olhe o maior número de reinícios observado. A média é baixa, mas a **cauda** é longa.\n   O que isso significa para quem precisa de um tempo de resposta garantido?"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lacuna 5 — Simulated Annealing\n\nImplemente o algoritmo da seção 3.4.2, com **resfriamento geométrico**: a cada iteração,\n`T = T * alfa`.\n\nComo o problema é de minimização, o movimento **melhora** quando reduz os conflitos.\nDefinindo `d = conflitos_atual - conflitos_novo`, temos `d > 0` para melhora, e a\nprobabilidade de aceitar uma piora é `exp(d / T)`.\n\nVizinho: sorteie uma coluna e uma linha. **Sorteie**, não escolha o melhor: é isso que\ntorna o Simulated Annealing aplicável a vizinhanças grandes demais para enumerar."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "def simulated_annealing(s, T0=2.0, alfa=0.99, Tmin=1e-3):\n    s = list(s)\n    e = conflitos(s)\n    T = T0\n    it = 0\n    while T > Tmin and e > 0:\n        it += 1\n        # TODO: sortear coluna c e linha r; se r == s[c], apenas resfriar e continuar;\n        #       calcular e2 = conflitos do vizinho e d = e - e2;\n        #       aceitar se d > 0 ou se random.random() < exp(d/T); senão desfazer;\n        #       resfriar: T *= alfa\n        raise NotImplementedError('lacuna 5')\n    return e, it"
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "random.seed(11)\nprint(f\"{'alfa':>7}{'iter. até Tmin':>17}{'sucesso':>10}{'iterações médias':>19}\")\ntabela = {}\nfor alfa in (0.95, 0.99, 0.999):\n    suc, its = 0, []\n    for _ in range(1000):\n        e, it = simulated_annealing(estado_vetor(), alfa=alfa)\n        if e == 0: suc += 1\n        its.append(it)\n    teorico = math.log(1e-3 / 2.0) / math.log(alfa)\n    tabela[alfa] = (suc / 1000, sum(its) / 1000)\n    print(f'{alfa:>7}{teorico:>17.0f}{100*suc/1000:>9.1f}%{sum(its)/1000:>19.0f}')\n\nassert tabela[0.999][0] > tabela[0.99][0] > tabela[0.95][0], 'resfriar mais devagar deve ajudar'\nassert tabela[0.999][0] > 0.90\nprint('\\nLacuna 5: OK')"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Para o relatório\n\n1. A coluna `iter. até Tmin` é o **pior caso**: quantas iterações o resfriamento levaria se\n   nunca encontrasse solução. A coluna `iterações médias` é bem menor. **Por quê?**\n2. Passar de α = 0,95 para α = 0,999 multiplica as iterações por cerca de 12 e o sucesso por\n   cerca de 6. **O ganho compensa?** A resposta depende de uma informação que não está na\n   tabela. Qual?\n3. O resfriamento geométrico **não** satisfaz a condição do Teorema 3, e portanto este\n   algoritmo **não tem garantia alguma** de encontrar o ótimo. Ainda assim resolve quase\n   tudo. Como você justificaria seu uso em um relatório profissional?"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lacuna 6 — comparação justa\n\nAgora a pergunta que o TDE3 vai fazer: **entre reinício aleatório e Simulated Annealing,\nqual é melhor?**\n\nA comparação só é honesta se fixar a mesma unidade de custo, e essa unidade é o\n**número de avaliações da função objetivo**. Não é segundos, que dependem da máquina, e\nnão é passos, que custam coisas diferentes em cada algoritmo.\n\nMeça, para cada método, quantas avaliações de `conflitos` são gastas."
  },
  {
   "cell_type": "code",
   "metadata": {},
   "execution_count": null,
   "outputs": [],
   "source": "# TODO: para cada um dos dois métodos, rodar 500 execuções zerando AVALIACOES antes de cada\n#       uma, e registrar a média de AVALIACOES e a taxa de sucesso.\n#       Para o reinício aleatório, medir até o sucesso (a taxa é 100% por construção).\n#       Para o SA, usar alfa=0.999 e medir uma execução de cada vez.\nraise NotImplementedError('lacuna 6')"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Para o relatório\n\n1. Os dois métodos ficam próximos em avaliações de f. **Se você tivesse contado passos**,\n   qual dos dois pareceria dezenas de vezes melhor, e por que a conclusão seria falsa?\n2. Compare o custo dos dois com o tamanho do espaço de estados. Vale a pena usar busca\n   local aqui? E em 100 rainhas, cujo espaço tem 100¹⁰⁰ estados?\n3. Os dois métodos empatam neste problema. **Que outros critérios** você usaria para\n   escolher entre eles em um projeto real?"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n## Entrega\n\nO relatório deve conter:\n\n- as respostas às perguntas das lacunas 2 a 6;\n- **número de execuções, semente e distribuição** em toda medição de método estocástico,\n  com no mínimo média, melhor e pior resultado. Relatórios que apresentem **apenas a melhor\n  execução serão devolvidos**;\n- custo sempre em **avaliações da função objetivo**, nunca em segundos;\n- a tabela da lacuna 6, que é o embrião do protocolo experimental do **TDE3 (Otimização)**,\n  com execução entre 28/10 e 04/11."
  }
 ]
}