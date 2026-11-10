# TDE3 — N-Rainhas

Projeto individual de otimização para N=30. O estado/cromossomo é uma permutação de
`0..29`; a função objetivo conta pares em conflito diagonal e é minimizada até zero.
No Algoritmo Genético, fitness é `435 - conflitos`.

## Executar

Interface didática, com seis abas e demonstrações avulsas:

```bash
python3 interface.py
```

Testes, calibração e execução dos quatro métodos, geração dos CSVs, ficha, relatório e
apresentação:

```bash
python3 run.py
```

Requer Python 3 (inclui Tkinter) e LibreOffice/soffice para gerar/validar os documentos.
Não há dependências Python externas. Abrir a interface somente carrega os CSVs existentes;
não dispara os experimentos.

## Métodos e protocolo

Os métodos são sorteio aleatório, Hill Climbing com reinício, Simulated Annealing e
Algoritmo Genético. A comparação final usa 30 execuções por método e até 10.000 avaliações
da função objetivo por execução. A semente-base é `20261109`; as sementes derivadas e
resultados por execução estão nos CSVs.

A calibração local e genética usa duas configurações por método, cinco execuções por
configuração e 2.000 avaliações por execução. O AG usa seleção por torneio `t=3`, elitismo
`E=1`, OX e mutação por troca (swap); a calibração seleciona a probabilidade de mutação
entre `0.02` e `0.05`. As populações são reavaliadas integralmente a cada geração e uma
geração só começa se couber no orçamento restante.

Não foi localizado notebook/código executável da Aula 9 no workspace. O arquivo
`CodigoAlgoritmoGenetico.md` fornece a especificação/pseudocódigo; `Aula8_Laboratorio_Estudante.ipynb`
é a base real de busca local.

## Arquivos

- `interface.py`: interface Tkinter e demonstração ao vivo.
- `src/experimento.py`: objetivo, contador, métodos, crossover OX, mutação, calibração.
- `src/gerar_entrega.py`: ficha, relatório PDF e apresentação.
- `tests/test_experimento.py`: testes do objetivo, métodos, AG, CSVs e auxiliares da interface.
- `entrega/resultados.csv`: dados brutos finais dos quatro métodos.
- `entrega/calibracao.csv`: dados brutos de calibração.
- `entrega/tabela_resumo.csv`: estatísticas reprodutíveis.

O documento introdutório da ficha menciona um ciclo genético ausente do notebook fornecido;
o AG foi incorporado como método adicional, sem substituir as linhas de base e buscas locais.
