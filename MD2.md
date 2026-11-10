MD 2 — Implementar o TDE3, executar, preencher a ficha e criar a apresentação
Agora execute o trabalho completo do TDE3 com base na inspeção feita na etapa anterior. O objetivo é entregar somente o necessário para cumprir os requisitos, com implementação simples, resultados reais e documentação curta.
Regra principal
Trabalhe como se o estudante fosse um único integrante, sem grupo. Não invente nomes, tarefas de equipe ou contribuições de terceiros.

Leia novamente a ficha TDE3_Ficha_de_Projeto_6A.docx e o notebook Aula8_Laboratorio_Estudante.ipynb antes de alterar qualquer coisa. Siga o conteúdo real dos arquivos. Se houver divergência entre o texto da ficha e o notebook, não esconda: registre a diferença e adote a solução mínima que atende aos critérios explícitos de avaliação.
Problema a implementar
Use o problema das N-Rainhas generalizado, preferencialmente com N = 30, desde que a inspeção confirme que é viável no ambiente.
Modelagem
- Estado: permutação de 0 até N-1.
- Interpretação: s[c] é a linha da rainha na coluna c.
- A permutação garante uma rainha por coluna e por linha.
- Função objetivo: número de pares de rainhas que se atacam na diagonal.
- Para cada par i < j, há conflito diagonal quando abs(s[i] - s[j]) == abs(i - j).
- Minimizar a função objetivo.
- Alvo conhecido: 0 conflitos.
- Espaço de estados: N!; mostrar a conta para o N escolhido.
- Vizinhança: trocar os valores de duas posições; número de vizinhos N*(N-1)/2.
Se N=30 tornar os experimentos inviáveis no tempo disponível, reduza somente o necessário (por exemplo, N=20), justifique e mantenha um N suficientemente maior que 8 para caracterizar a generalização. Registre o N final em todos os arquivos.
Recombinação/crossover
A ficha pergunta sobre crossover. Como os métodos de busca local não precisam de recombinação, explique isso corretamente: crossover não é usado pelos métodos escolhidos. Se o material/ficha exigir de fato Algoritmo Genético como método obrigatório, não finja que Hill Climbing e Simulated Annealing o substituem. Nesse caso, implemente o mínimo necessário ou sinalize a incompatibilidade claramente antes de ampliar o escopo. Não implemente GA apenas por iniciativa própria se os critérios explícitos e o notebook confirmarem que dois métodos de busca local são suficientes.
Métodos e linhas de base
Implemente e compare, no mínimo:
1. Sorteio aleatório (baseline): gerar estados aleatórios válidos e avaliar a função objetivo.
2. Hill Climbing com reinício aleatório: subida mais íngreme, aceitando somente melhora estrita; quando ficar preso em ótimo local/platô, iniciar novo estado aleatório.
3. Simulated Annealing: escolher vizinho aleatório por troca de duas posições; aceitar melhorias e aceitar pioras conforme a probabilidade de Boltzmann, com resfriamento geométrico.
Use o notebook como referência para a lógica e para o contador de avaliações. Adapte a implementação à representação por permutação e ao N escolhido. Evite duplicar código.
Comparação experimental justa — obrigatório
Todos os métodos devem usar a mesma unidade de custo: avaliações da função objetivo. Não use segundos, número de passos ou número de iterações como unidade principal de comparação.

Defina um protocolo simples e simétrico:
- Use o mesmo orçamento máximo de avaliações por execução para os três métodos.
- Use o mesmo número de execuções por método, preferencialmente 30 ou 50, conforme o tempo de execução.
- Use uma semente-base fixa e sementes derivadas de forma reprodutível para cada execução.
- Faça calibração pequena e equilibrada: mesmo número de configurações testadas e mesmo orçamento de calibração para Hill Climbing e Simulated Annealing. Se não houver tempo para calibração, use parâmetros padrão justificados e declare isso.
- O sorteio aleatório deve receber o mesmo orçamento e tentar encontrar uma solução dentro dele.
- Hill Climbing com reinício deve parar ao encontrar solução ou esgotar o orçamento.
- Simulated Annealing deve parar ao encontrar solução ou esgotar o orçamento.
- Conte cada chamada à função objetivo exatamente uma vez. Centralize o contador para evitar contagens inconsistentes.
- Não ultrapasse o orçamento por execução. Se um algoritmo precisar avaliar vários vizinhos, interrompa a avaliação quando atingir o limite.
- Garanta que o contador seja zerado no início de cada execução.
Reporte para cada método:
- taxa de sucesso (% de execuções que encontraram zero conflitos);
- média, melhor e pior número de avaliações até a solução, considerando apenas execuções bem-sucedidas;
- média, melhor e pior melhor-valor encontrado quando não houver solução, ou outra estatística equivalente claramente definida;
- distribuição dos resultados, não apenas o melhor caso;
- orçamento, quantidade de execuções e sementes utilizadas.
Se um método não encontrar soluções em algumas execuções, não descarte essas falhas. Reporte a taxa de sucesso e deixe claro como as estatísticas foram calculadas. Não invente resultados para completar tabelas.
Implementação e validação
1. Faça backup dos arquivos originais.
2. Implemente em Python, preferencialmente em um arquivo .py simples e executável.
3. Preserve o notebook original; se for útil, crie uma cópia adaptada.
4. Garanta que a função objetivo incremente o contador em toda avaliação.
5. Faça testes básicos:
   - estado é uma permutação válida;
   - função objetivo retorna inteiro não negativo;
   - solução conhecida/gerada com zero conflitos é reconhecida;
   - vizinho continua sendo uma permutação;
   - orçamento de avaliações nunca é ultrapassado;
   - mesma semente reproduz a mesma execução;
   - todos os métodos retornam métricas no mesmo formato.
6. Execute os testes e os experimentos completos.
7. Salve os resultados brutos em CSV e gere uma tabela-resumo legível.
8. Não reporte números estimados, simulados manualmente ou copiados do exemplo de oito rainhas como se fossem resultados do experimento final.
Análise obrigatória
Escreva uma análise objetiva que responda:
- Por que a representação por permutação é adequada?
- Que conflitos ela elimina por construção?
- Por que o espaço de busca é grande, mas a vizinhança é tratável?
- Por que Hill Climbing pode ficar preso em ótimos locais?
- Como o Simulated Annealing pode aceitar movimentos piores e escapar de ótimos locais?
- Qual método teve melhor desempenho nos experimentos, usando a mesma unidade de custo?
- O resultado é consistente entre execuções ou varia bastante?
- Quais são as limitações e garantias ausentes? Declare explicitamente que o resfriamento geométrico do Simulated Annealing não garante encontrar o ótimo; não prometa garantia para Hill Climbing.
- O sorteio aleatório foi competitivo ou claramente inferior?
Não afirme que um método é superior se os dados não sustentarem isso. Se os resultados forem próximos, diga que houve empate técnico ou diferença inconclusiva.
Preencher a ficha DOCX
Preencha TDE3_Ficha_de_Projeto_6A.docx preservando o formato original, quando possível. Salve uma cópia final em entrega/TDE3_Ficha_Preenchida.docx.

Preencha todos os campos aplicáveis:
- Equipe: Trabalho individual — sem grupo (não inventar nomes).
- Problema escolhido e justificativa.
- Representação, tamanho do espaço com a conta e vizinhança.
- Recombinação/crossover, explicando sua não aplicação aos métodos locais ou a decisão efetivamente tomada.
- Função objetivo, fórmula e minimização.
- Alvo conhecido.
- Linhas de base.
- Orçamento, número de execuções e sementes.
- Verificação: marque somente itens realmente executados e comprovados. Se um item da ficha depender de demonstração ao professor, não marque como concluído sem evidência.
Se algum campo não comportar a resposta, use texto conciso e tecnicamente correto. Não invente aprovação do professor.
Relatório curto
Crie entrega/Relatorio_TDE3.pdf ou .docx com:
1. Identificação da atividade e indicação de trabalho individual.
2. Problema e modelagem.
3. Métodos e protocolo experimental.
4. Tabela comparativa com média, melhor, pior, taxa de sucesso e orçamento.
5. Discussão dos resultados.
6. Limitações e garantias ausentes.
Se a ficha for suficiente como documento escrito e a atividade não exigir relatório separado, ainda assim gere um relatório enxuto com os resultados experimentais, sem repetir páginas desnecessariamente.
Apresentação simples
Crie entrega/Apresentacao_TDE3.pptx, com visual limpo e poucos elementos, sem animações. Use aproximadamente 6 slides:
1. Problema: N-Rainhas e objetivo de minimizar conflitos.
2. Modelagem: representação por permutação, espaço N!, vizinhança e fórmula.
3. Métodos: sorteio aleatório, Hill Climbing com reinício e Simulated Annealing.
4. Execução: mostrar uma solução/execução e o contador de avaliações.
5. Resultados: tabela/gráfico com taxa de sucesso e distribuição na mesma unidade de custo.
6. Limitações: o que não funcionou, variação entre execuções e garantias que os algoritmos não oferecem.
A apresentação deve ser simples e compreensível para uma exposição de 12 minutos. Não invente imagens nem resultados. Inclua notas curtas do apresentador apenas se forem úteis.
Organização final esperada
Organize os arquivos em entrega/:
- TDE3_Ficha_Preenchida.docx
- Relatorio_TDE3.pdf ou Relatorio_TDE3.docx
- Apresentacao_TDE3.pptx
- resultados.csv
- tabela_resumo.csv ou .md
Mantenha também o código-fonte e os testes em uma pasta do projeto.
Conferência final antes de encerrar
Execute uma verificação final e só declare concluído se:
- o código executa do início ao fim;
- os testes passam;
- os resultados vieram da execução real;
- o orçamento foi respeitado em todas as execuções;
- os métodos foram comparados com o mesmo orçamento e unidade;
- a ficha está preenchida sem dados inventados;
- a apresentação usa os resultados reais;
- os arquivos finais existem e abrem.
Ao final, mostre apenas:
1. lista dos arquivos entregues;
2. comando exato para executar o projeto;
3. resumo dos resultados reais;
4. qualquer requisito que não tenha sido possível cumprir e o motivo.
Se encontrar um bloqueio que altere a interpretação do trabalho (especialmente a possível exigência de Algoritmo Genético), pare e explique objetivamente antes de produzir uma entrega que possa estar fora do enunciado. Para problemas técnicos menores, resolva por conta própria sem interromper o fluxo.