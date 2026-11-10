MD 4 — Finalizar o TDE3 com Algoritmo Genético, auditoria e entrega completa
Objetivo
Finalize o TDE3 de Otimização para N-Rainhas (N=30), incorporando Algoritmo Genético (AG) como método adicional, por precaução e para atender à referência explícita da ficha ao ciclo genético e ao crossover.

O projeto já possui implementação e resultados de:
- Sorteio aleatório;
- Hill Climbing com reinício aleatório;
- Simulated Annealing.
Também já existem testes, ficha preenchida, apresentação e uma interface gráfica em desenvolvimento ou implementada. Não recomece o projeto. Primeiro inspecione o estado real dos arquivos e preserve tudo que funciona. Seu trabalho é integrar o AG, validar os quatro métodos e atualizar toda a entrega de forma consistente.

O estudante trabalha individualmente. Não invente integrantes, tarefas de equipe ou contribuições de terceiros.
1. Fontes obrigatórias: leia antes de programar
Localize e leia os materiais disponíveis no workspace. Dê prioridade a estes arquivos, se estiverem presentes:
1. TDE3_Ficha_de_Projeto_6A.docx e/ou TDE3_Ficha_Preenchida.docx;
2. Notebook/código do laboratório da Aula 9 de Algoritmos Genéticos (AI_Aula9, notebook Colab ou equivalente);
3. Notebook/código da Aula 8, que contém a base das buscas locais, representação e contador de avaliações;
4. AI_Aula9.pdf;
5. Guia_de_Estudos_RA3_IA_Prova_2.pdf e/ou Material para Revisão Prova RA3.pdf;
6. MD1_Preparar_IDE_TDE3.md, MD2_Executar_TDE3_Completo.md e os arquivos gerados nas etapas anteriores;
7. README, código-fonte, testes, CSVs, ficha, relatório, slides e interface atuais.
Regra de fidelidade às fontes
A ficha do TDE3 afirma que a base de código já existe no notebook de Algoritmos Genéticos, contendo o ciclo genético, contador de avaliações da função objetivo e linhas de base da Aula 8. Ela orienta adaptar estado_aleatorio(), conflitos(s), N e APTIDAO_MAXIMA, em vez de começar do zero.

Portanto:
- Localize e inspecione o código real da Aula 9.
- Reaproveite sua estrutura, nomes, fluxo, contagem de avaliações e protocolo sempre que forem compatíveis.
- Não substitua o laboratório por um AG genérico inventado sem antes analisar a implementação fornecida.
- Se o código original usar representação diferente da permutação, explique a incompatibilidade e adapte apenas o necessário.
- Se não conseguir localizar o notebook/código original, registre isso explicitamente. Use os materiais de aula em PDF como especificação e não afirme que reutilizou código que não encontrou.
- Não copie resultados de exemplo do material didático como se fossem resultados deste experimento.
O que os materiais de aula estabelecem sobre AG
O AG mantém uma população de k indivíduos/cromossomos. Cada indivíduo representa uma solução. A aptidão (fitness) é tratada como valor a maximizar. A cada geração, os indivíduos são avaliados, verifica-se o alvo, os E melhores são preservados por elitismo, pais são selecionados, filhos são produzidos por crossover com probabilidade p_cross ou por cópia de um pai, e ocorre mutação por gene com probabilidade p_mut.

As sete decisões de configuração são:
1. k: tamanho da população;
2. p_cross: probabilidade de crossover;
3. p_mut: probabilidade de mutação por gene;
4. G: limite de gerações;
5. E: tamanho do elitismo;
6. mecanismo de seleção;
7. operador de recombinação.
O material apresenta:
- Seleção por roleta: P(i) = f_i / soma(f), sensível à escala da aptidão.
- Seleção por torneio de tamanho t: sorteia t indivíduos com reposição e escolhe o de maior aptidão. A probabilidade de o melhor aparecer ao menos uma vez é 1 - ((k-1)/k)^t.
- Elitismo: os E melhores passam intactos. Com E >= 1, a melhor aptidão da população não diminui entre gerações; isso não garante encontrar o ótimo global.
- Crossover de um ponto, dois pontos e uniforme, como conceitos gerais.
- Mutação independente por gene: número esperado de eventos de mutação L * p_mut; probabilidade de nenhum evento (1-p_mut)^L.
- O laboratório da Aula 9 exemplifica torneio t=3, elitismo E=1, população 50, p_cross=0.9, p_mut=0.15 e até 300 gerações para o exemplo de oito rainhas. Esses valores são referência didática, não resultados nem parâmetros automaticamente adequados para N=30.
- A comparação experimental deve usar avaliações da função objetivo como unidade de custo. Uma geração de população k custa k avaliações de f. A comparação precisa ser pareada por orçamento de avaliações, com calibração simétrica, distribuição de resultados e linha de base trivial.
2. Modelagem correta de N-Rainhas (N=30)
Preserve a modelagem existente, salvo se a auditoria encontrar erro real.
- N = 30.
- Estado/cromossomo: permutação dos inteiros 0..29.
- s[c] é a linha da rainha na coluna c.
- A permutação garante uma rainha por linha e por coluna.
- Conflito diagonal para cada par i < j quando abs(s[i] - s[j]) == abs(i - j).
- Função objetivo conflitos(s): contar pares em conflito diagonal; minimizar.
- Alvo: 0 conflitos.
- Número de pares de rainhas: C(30,2) = 435.
- Vizinhança por troca de duas posições: C(30,2) = 435 vizinhos.
O que significa 30!
Explique nos materiais em linguagem simples: 30! é “30 fatorial”, isto é, 30 × 29 × 28 × ... × 2 × 1. É a quantidade de permutações possíveis de 30 elementos, ou seja, o tamanho do espaço de estados desta representação.

Valor correto:
30! = 265.252.859.812.191.058.636.308.480.000
(aproximadamente 2,65 × 10^32).

Não diga que o programa percorre todo esse espaço. O valor expressa quantas permutações existem.
Fitness e APTIDAO_MAXIMA
A função objetivo é de minimização, mas o material da Aula 9 define fitness como valor a maximizar. Faça a transformação coerente:
- APTIDAO_MAXIMA = C(N,2) = 435, pois esse é o limite superior teórico para a quantidade de pares.
- fitness(s) = APTIDAO_MAXIMA - conflitos(s).
- Fitness varia de 0 a 435.
- Solução perfeita: conflitos(s)=0 e fitness(s)=435.
- Melhor fitness significa menos conflitos.
Verifique o código do notebook original antes de fixar os nomes e a semântica. Se o material usar APTIDAO_MAXIMA de outro modo, compare com esta modelagem e documente a adaptação sem quebrar a intenção do professor.

Não use fitness = conflitos diretamente em uma roleta que seleciona valores maiores, pois isso favoreceria soluções piores.
3. Implementar o Algoritmo Genético para permutações
Restrição central: todo cromossomo precisa continuar sendo uma permutação válida
O crossover de um ponto simples, aplicado diretamente a dois vetores de permutação, pode produzir genes duplicados e valores ausentes. Isso quebra a representação e invalida o estado.

Logo:
- Não use crossover simples de um ponto sem mecanismo de reparo.
- Prefira implementar Order Crossover (OX) ou Partially Mapped Crossover (PMX), desde que consiga testar corretamente.
- OX é uma escolha adequada: selecionar dois cortes, copiar o segmento de um pai para as mesmas posições do filho e preencher as posições restantes, na ordem, com os elementos ainda ausentes do outro pai.
- Documente qual pai fornece o segmento e qual fornece a ordem de preenchimento.
- Faça testes com pais diferentes e com pais iguais.
A mutação também deve preservar a permutação:
- Use troca (swap mutation) entre duas posições, pois ela mantém todos os valores únicos.
- Adapte a ideia de mutação por gene do material: para cada posição/gene, faça o sorteio com probabilidade p_mut; quando ocorrer, escolha outra posição e troque os dois valores.
- Evite substituição aleatória de um valor por outro, pois isso cria duplicatas.
- Documente que, nesta adaptação por permutação, o evento de mutação é implementado como troca. Como trocas podem se sobrepor na mesma passagem, não afirme que o número de genes efetivamente diferentes após a mutação é sempre N * p_mut. Essa fórmula do material representa o número esperado de eventos por gene no mecanismo independente, não necessariamente o número final de posições distintas após swaps sobrepostos.
Ciclo genético esperado
Siga o pseudocódigo e a implementação do laboratório:
1. Criar população inicial de k permutações válidas.
2. Avaliar cada indivíduo com a função objetivo/fitness, contabilizando cada avaliação de f.
3. Se algum indivíduo tiver zero conflitos, registrar sucesso e retornar.
4. Copiar os E melhores para a nova população sem alteração.
5. Enquanto a nova população não atingir k:
   - selecionar dois pais pelo mecanismo definido;
   - com probabilidade p_cross, aplicar OX ou PMX;
   - caso contrário, copiar um dos pais;
   - aplicar mutação por swaps;
   - adicionar o filho.
6. Substituir a população pela nova geração.
7. Repetir até atingir o alvo, o limite de gerações ou o orçamento de avaliações.
8. Ao terminar, retornar o melhor indivíduo encontrado, mesmo se não alcançar zero conflitos.
Seleção e elitismo
Use como configuração principal:
- Seleção por torneio com t=3, conforme o laboratório da Aula 9.
- Elitismo E=1, conforme o laboratório.
- Crossover OX ou PMX, por compatibilidade com permutações.
- Mutação por swap.
A roleta pode ser mantida como opção secundária somente se estiver corretamente implementada com fitness não negativo e soma positiva. Não é necessário implementar várias opções de seleção se isso aumentar muito o escopo. O torneio já atende ao conteúdo de aula e evita problemas de escala.
Parâmetros
Não copie cegamente os parâmetros de N=8 para N=30. Defina um conjunto pequeno e justificado para N=30. Comece com valores razoáveis e calibre de modo simétrico. Registre:
- população k;
- p_cross;
- p_mut;
- limite G;
- elitismo E;
- seleção (torneio, t=3);
- crossover (OX ou PMX);
- semente.
Não faça busca extensa de hiperparâmetros. O trabalho precisa ser concluído com escopo controlado.
4. Contador de avaliações e comparação justa — requisito crítico
A unidade de custo é exclusivamente o número de avaliações da função objetivo conflitos(s). Não compare métodos por gerações, iterações ou tempo de CPU.
- Reaproveite o contador do projeto/notebook, se existente.
- Toda chamada efetiva à função objetivo deve incrementar o contador exatamente uma vez.
- Não conte cálculos auxiliares de fitness como uma segunda avaliação se eles apenas reutilizam o resultado de conflitos(s).
- Não esconda avaliações em seleção, crossover, mutação, interface ou geração de gráficos.
- O AG precisa informar avaliações consumidas, sucesso/falha, melhor número de conflitos e configurações.
- A população inicial custa k avaliações.
- De acordo com a regra do laboratório, uma geração custa k avaliações de f. Se a implementação mantiver fitness em cache dos indivíduos elitistas e avaliar somente filhos, o custo real pode ser k-E; não declare que custou k sem contar. Para aderir literalmente ao protocolo da aula, prefira reavaliar a população inteira a cada geração, inclusive elites, e contar essas k chamadas.
- Pare antes de ultrapassar o orçamento. Faça a lógica de parada respeitar o limite exato, inclusive quando o orçamento não for múltiplo de k.
- Se uma geração inteira não couber no orçamento restante, não a inicie; registre o orçamento efetivamente utilizado.
- Faça teste automatizado do contador para confirmar esses comportamentos.
Comparação final
Mantenha os métodos já implementados:
1. Sorteio aleatório;
2. Hill Climbing com reinício aleatório;
3. Simulated Annealing;
4. Algoritmo Genético.
Use o mesmo orçamento de avaliações por execução para todos os quatro métodos. Preserve os resultados anteriores dos três métodos, mas confira sua consistência com os CSVs e logs reais.

Configuração final já registrada no projeto:
- Orçamento: 10.000 avaliações por execução.
- 30 execuções finais por método.
- Semente-base: 20261109.
- Os métodos existentes usam sementes derivadas da base, conforme implementação atual.
Inclua o AG na mesma quantidade de execuções e orçamento. Não altere silenciosamente os resultados anteriores. Se alguma mudança no contador comum for necessária, reexecute todos os métodos afetados e gere uma nova comparação completa.
Calibração simétrica
O projeto já tem calibração piloto para Hill Climbing e Simulated Annealing: duas configurações por método, cinco execuções por configuração e 2.000 avaliações por execução.

Adicione uma calibração pequena para o AG (por exemplo, duas configurações, cinco execuções por configuração e o mesmo orçamento de 2.000 avaliações por execução). Se o protocolo exigir que todos os métodos sejam recalibrados, faça isso de forma simétrica e registre a decisão. Não compare um método muito calibrado com outro sem calibração.

Não escolha a configuração final do AG olhando apenas para a melhor execução. Considere taxa de sucesso e distribuição dos resultados.
5. Testes obrigatórios do AG
Crie testes automatizados, preferencialmente no conjunto de testes existente, cobrindo:
1. Cromossomo inicial sempre é permutação de 0..29.
2. OX/PMX sempre gera filho com todos os valores exatamente uma vez.
3. Crossover com pais iguais retorna uma permutação igual/compatível.
4. Mutação por swap preserva a permutação.
5. Mutação com taxa zero não altera o cromossomo.
6. Elitismo preserva o melhor indivíduo da geração anterior.
7. Melhor fitness da população não diminui entre gerações com E>=1.
8. Seleção por torneio sempre retorna um indivíduo da população.
9. Fitness está coerente: menos conflitos implica fitness maior.
10. Solução com zero conflitos tem fitness 435.
11. Contador incrementa uma vez por avaliação real de conflitos.
12. AG respeita exatamente o orçamento e não ultrapassa o limite.
13. AG respeita o limite de gerações.
14. Com a mesma semente, a execução é reprodutível.
15. AG retorna o melhor indivíduo encontrado mesmo quando não encontra solução.
16. Teste de integração com N menor (por exemplo N=8) para verificar que o AG consegue encontrar soluções conhecidas; esse teste não substitui os experimentos finais em N=30.
Não enfraqueça nem apague testes existentes para fazer a suíte passar.
6. Interface gráfica
Se a interface criada na etapa anterior existir, integre o AG nela. Não crie uma segunda interface paralela.

A interface deve:
- listar os quatro métodos;
- permitir selecionar AG;
- mostrar os parâmetros do AG;
- demonstrar a população ou, no mínimo, o melhor indivíduo da geração atual;
- exibir o tabuleiro 30x30 com as rainhas e conflitos;
- mostrar geração atual, avaliações consumidas, orçamento, conflitos e fitness;
- indicar claramente sucesso (0 conflitos) ou encerramento sem solução;
- permitir interromper execução com segurança;
- não congelar a janela durante o processamento;
- não fazer avaliações extras para atualizar a tela;
- usar os resultados reais dos CSVs na aba de comparação.
Se a interface não existir, verifique o estado real do projeto antes de criá-la. Não sacrifique a correção dos algoritmos para adicionar elementos visuais.
7. Atualizar ficha, relatório, README e apresentação
Depois de implementar, testar e executar os experimentos, atualize todos os documentos afetados para refletir os quatro métodos.
Ficha
- Corrija a seção de recombinação: agora existe AG e o crossover é usado nele.
- Explique que crossover de um ponto simples não preserva permutações; foi adotado OX/PMX para manter cromossomos válidos.
- Diferencie métodos: HC e SA usam movimentos locais; AG usa população, seleção, recombinação e mutação.
- Atualize linhas de base e métodos avaliados.
- Mantenha N=30, 30!, 435 vizinhos, função objetivo, orçamento, execuções e sementes consistentes.
- Não deixe afirmações antigas dizendo simplesmente que crossover não se aplica ao projeto inteiro.
- Aponte que crossover não se aplica a HC/SA, mas se aplica ao AG.
Relatório
Inclua:
- problema e modelagem;
- explicação simples de 30!;
- descrição curta de cada método;
- representação do cromossomo;
- fitness 435 - conflitos;
- seleção por torneio t=3;
- elitismo E=1;
- operador de crossover OX/PMX e justificativa;
- mutação por swap;
- parâmetros e calibração;
- protocolo de custo por avaliações de f;
- resultados dos quatro métodos;
- taxa de sucesso, média, mediana (se disponível), melhor e pior caso;
- distribuição de conflitos nas falhas;
- limitações e ameaças à validade.
Apresentação
Atualize os slides para apresentar os quatro métodos. Mantenha a duração prevista e a clareza. Inclua:
- por que 30! é um espaço enorme;
- como a permutação representa o tabuleiro;
- por que crossover de um ponto não serve diretamente;
- como OX/PMX preserva a permutação;
- como funciona a seleção, elitismo e mutação;
- comparação justa por avaliações de f;
- resultados reais e limitações.
Não invente resultados. Não apresente parâmetros de exemplo da Aula 9 como se fossem resultados obtidos no N=30.
README e arquivos de resultados
Atualize comandos de execução, estrutura e dependências. Gere/atualize CSVs e tabelas com dados reais. Preserve arquivos brutos para permitir conferência.
8. Auditoria final e integridade
Antes de concluir:
1. Execute a suíte completa de testes.
2. Execute o fluxo oficial do projeto (python3 run.py ou o comando que o README realmente indicar).
3. Execute o AG isoladamente com semente fixa e orçamento pequeno para smoke test.
4. Execute os experimentos finais completos com o mesmo orçamento dos demais métodos.
5. Confira os CSVs e recalcule as estatísticas independentemente a partir dos dados brutos.
6. Confira se os quatro métodos aparecem em todos os documentos e gráficos.
7. Confira se as taxas de sucesso e estatísticas dos slides batem com relatório e CSVs.
8. Confira que a interface não altera os resultados e não conta avaliações extras.
9. Confira que nenhuma permutação inválida chega à função objetivo.
10. Confira que nenhuma execução ultrapassa 10.000 avaliações.
11. Preserve os resultados anteriores e mantenha backup antes de substituir documentos.
12. Não deixe texto provisório, TODO, campos vazios ou números de exemplo na entrega final.
Se algum experimento não terminar por limite de tempo ou falha técnica, não invente o resultado nem marque como concluído. Registre exatamente o que foi executado e o que ficou pendente.
9. Entregáveis esperados
Mantenha a organização atual do projeto e gere, no mínimo:
- Código-fonte do AG integrado;
- Operador OX ou PMX testado;
- Mutação por swap testada;
- Testes automatizados;
- CSVs brutos dos experimentos;
- resumo/tabela comparativa dos quatro métodos;
- ficha atualizada;
- relatório final;
- apresentação atualizada;
- README atualizado;
- interface atualizada, se já existir.
Não crie documentos redundantes se os equivalentes já existirem. Atualize os arquivos existentes.
10. Resposta final da IA da IDE
Ao terminar, apresente um resumo objetivo com:
1. Quais arquivos foram alterados/criados.
2. Qual código/material da Aula 9 foi localizado e reaproveitado.
3. Qual crossover foi implementado (OX ou PMX) e por que.
4. Como o fitness foi calculado.
5. Parâmetros finais do AG.
6. Número de testes executados e resultado.
7. Número de execuções finais por método e orçamento.
8. Resultados reais dos quatro métodos: sucessos, taxa de sucesso, média/melhor/pior avaliações até solução e distribuição de conflitos nas falhas.
9. Comando para executar o projeto e abrir a interface.
10. Pendências ou limitações que ainda existirem.
Regra final: priorize correção, aderência à ficha e aos materiais de aula, comparação experimental justa e consistência entre código, CSVs, ficha, relatório, apresentação e interface. Não invente dados e não recomece o projeto do zero.