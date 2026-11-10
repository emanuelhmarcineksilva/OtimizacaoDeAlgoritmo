# TDE3 — N-Rainhas

Projeto individual de otimização para N=30. O estado é uma permutação de `0..29` e a
função objetivo minimiza o número de pares em conflito diagonal.

## Executar

```bash
python3 run.py
```

O comando roda os testes, faz uma calibração equilibrada (duas configurações por método
local, cinco execuções por configuração e 2.000 avaliações por execução), depois executa
30 repetições por método com orçamento final de 10.000 avaliações da função objetivo.
Salva os dados e gera a ficha preenchida, relatório PDF e apresentação. Requer Python 3 e
LibreOffice/soffice; não usa bibliotecas Python externas.

Os métodos são sorteio aleatório, Hill Climbing com reinício e Simulated Annealing.
O protocolo usa semente-base `20261109`; sementes e resultados por execução estão nos
CSVs brutos. A calibração escolhe maior taxa de sucesso e, em empate, menor média de
avaliações até solução. O crossover não se aplica aos métodos de busca local; a menção a um
ciclo genético na introdução da ficha não corresponde ao notebook fornecido.
