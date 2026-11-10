MD 1 — Preparar a IDE para executar o TDE3
Você é um assistente de programação trabalhando dentro da IDE. Sua tarefa nesta etapa é preparar o ambiente e entender o trabalho, sem começar a implementar a solução final.
Contexto do trabalho
- Disciplina: Inteligência Artificial — PUCPR.
- Atividade: TDE3 — Otimização.
- O estudante fará o trabalho individualmente (sem grupo).
- Objetivo prático: cumprir os requisitos da ficha e produzir o resultado final necessário com o menor escopo e a menor quantidade de etapas possível.
- O estudante prefere uma solução simples, executável, explicada com clareza e sem funcionalidades extras.
- O estudante usará você para implementar o trabalho por meio de instruções em Markdown. Não faça perguntas desnecessárias: inspecione os arquivos disponíveis e tome decisões técnicas simples, registrando as decisões.
Arquivos de referência obrigatórios
Localize e leia integralmente, quando disponíveis no workspace:
1. Aula8_Laboratorio_Estudante.ipynb
2. TDE3_Ficha_de_Projeto_6A.docx
Não presuma que o conteúdo do notebook corresponde exatamente à descrição da ficha. Confira o conteúdo real dos arquivos. Há uma possível diferença: a ficha menciona uma base de Algoritmos Genéticos, enquanto o notebook fornecido pode conter exercícios de busca local (Hill Climbing e Simulated Annealing). Identifique isso objetivamente e não invente código ou conteúdo que não exista.
Direção de solução proposta
A proposta inicial é generalizar o problema das N-Rainhas, usando N = 30:
- Estado representado por uma permutação de 0 a N-1.
- Cada índice representa uma coluna e o valor naquela posição representa a linha da rainha.
- A permutação garante exatamente uma rainha por linha e por coluna.
- A função objetivo conta pares de rainhas em conflito diagonal; queremos minimizar até zero.
- Espaço de estados: N! (para N=30, 30!).
- Vizinhança: trocar os valores de duas posições; quantidade de vizinhos: N*(N-1)/2.
- Alvo conhecido: zero conflitos, pois existem soluções para N-Rainhas para N >= 4.
Essa escolha é uma proposta de escopo mínimo, não uma autorização para ignorar os requisitos da ficha. Verifique se ela se encaixa no material e nos critérios. Se houver impedimento técnico real, proponha a menor alteração possível e explique o motivo.
O que fazer nesta etapa
1. Inspecione os arquivos e o workspace atual.
2. Identifique a linguagem, bibliotecas, estrutura e forma correta de executar o notebook/projeto.
3. Verifique se o notebook abre e quais células/funções já existem.
4. Identifique exatamente quais métodos estão disponíveis no material e quais precisam ser implementados/adaptados.
5. Confira todos os campos da ficha, os critérios de avaliação e os requisitos de apresentação.
6. Verifique se existe algum arquivo de projeto anterior. Não apague nem sobrescreva arquivos do estudante.
7. Se necessário, crie uma pasta de trabalho organizada, por exemplo:
   - src/ para o código;
   - resultados/ para CSV/tabelas;
   - entrega/ para ficha preenchida e apresentação.
8. Prepare ou confirme o ambiente Python. Prefira a biblioteca padrão. Não instale dependências sem necessidade.
9. Faça uma cópia de segurança dos arquivos originais antes de qualquer alteração.
10. Não execute experimentos longos nesta etapa.
Requisitos que você deve manter visíveis
A ficha exige, entre outros pontos:
- problema e justificativa;
- representação concreta;
- tamanho do espaço com a conta;
- vizinhança e número de vizinhos;
- tratamento da recombinação/crossover;
- fórmula da função objetivo e se é maximização ou minimização;
- existência de alvo conhecido;
- linhas de base: sorteio aleatório e Hill Climbing com reinício;
- orçamento em número de avaliações da função objetivo, igual para todos os métodos;
- número de execuções e semente;
- resultados com distribuição, incluindo média, melhor e pior caso;
- pelo menos dois métodos de busca local implementados;
- comparação justa e limitações/garantias ausentes declaradas.
A apresentação prevista na ficha tem 12 minutos: problema, modelagem, execução com contador visível, comparação com distribuição e limitações.
Restrições importantes
- O estudante está trabalhando sozinho. Não invente nomes de colegas, divisão de tarefas ou equipe.
- Não invente resultados, métricas, capturas de tela, testes executados ou conclusões.
- Não use tempo de execução em segundos como unidade principal de comparação. O custo comparável deve ser o número de avaliações da função objetivo.
- Não compare métodos com orçamentos diferentes.
- Não reporte apenas a melhor execução.
- Não faça uma interface gráfica, site, banco de dados ou funcionalidades que não foram solicitadas.
- Não reescreva o notebook inteiro sem necessidade.
- Não altere os arquivos originais sem backup.
- Não afirme que um algoritmo tem garantia de encontrar o ótimo se isso não for demonstrado.
Entrega desta etapa
Ao terminar, responda de forma curta e objetiva com:
1. O que encontrou nos dois arquivos.
2. Se a proposta N-Rainhas com N=30 é compatível ou qual ajuste mínimo recomenda.
3. Quais métodos serão usados e quais já existem no notebook.
4. Como executar o projeto.
5. Quais arquivos/pastas foram preparados.
6. Quais divergências ou riscos precisam ser resolvidos antes da implementação.
Pare após a preparação. Não implemente ainda. Aguarde o MD 2.