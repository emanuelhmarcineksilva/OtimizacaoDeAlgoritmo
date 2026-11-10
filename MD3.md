MD 3 — Criar uma interface visual didática para demonstrar o TDE3
Você está trabalhando no projeto TDE3 — N-Rainhas (N=30), já implementado e com experimentos executados.

Sua tarefa é criar uma interface visual local, simples, intuitiva e autoexplicativa para que o estudante consiga apresentar o funcionamento dos algoritmos ao professor, executar uma demonstração ao vivo e consultar os resultados já obtidos.

O estudante trabalha sozinho. Não invente integrantes, funções de equipe ou resultados.
1. Antes de programar: audite o projeto existente
Inspecione a estrutura real do projeto e leia os arquivos-fonte, testes, CSVs e documentos existentes. Não presuma nomes de classes, funções ou caminhos: descubra-os no projeto.

O comando atual para executar tudo é:
python3 run.py
Os resultados registrados atualmente são:
- N = 30;
- sorteio aleatório: 0/30 sucessos;
- Hill Climbing com reinício: 14/30 sucessos (46,7%);
- Simulated Annealing: 30/30 sucessos (100%);
- orçamento final: até 10.000 avaliações da função objetivo por execução;
- calibração: 2 configurações por método local, 5 execuções por configuração e 2.000 avaliações por execução;
- semente-base: 20261109;
- oito testes automatizados passaram na execução relatada.
Não trate esses números como constantes no código da interface. Leia os CSVs reais e carregue os valores de lá. Se os CSVs ou o código não estiverem disponíveis, informe isso e não invente dados.

Antes de criar a interface, verifique se os documentos e os dados estão atualizados e consistentes. A interface não deve modificar os resultados experimentais, a ficha, o relatório ou os slides.
2. Objetivo principal da interface
A interface deve permitir que alguém que nunca viu o projeto entenda:
- qual problema está sendo resolvido;
- como uma solução é representada;
- o que significa um conflito;
- como funciona cada algoritmo;
- o que é uma avaliação da função objetivo;
- por que os métodos são comparados pelo número de avaliações;
- o que os resultados experimentais mostram;
- quais são as limitações dos algoritmos.
Ela será usada principalmente para uma demonstração ao vivo, com o contador de avaliações claramente visível, conforme o roteiro da ficha.
3. Tecnologia e restrições
1. Primeiro verifique se tkinter está disponível no Python 3 do ambiente.
2. Se estiver disponível, use Tkinter, pois é biblioteca padrão e evita dependências externas.
3. Se não estiver disponível, não instale pacotes nem mude o ambiente sem necessidade. Informe o impedimento e proponha a alternativa mais simples compatível com o projeto.
4. Não use frameworks web, bancos de dados ou dependências pesadas.
5. Não reimplemente os algoritmos na interface. Reutilize as funções reais do projeto (src/, ou onde estiverem), preservando os testes e a lógica já validada.
6. Não altere o comportamento dos algoritmos para produzir uma demonstração mais bonita.
7. Não execute os 90 experimentos automaticamente ao abrir a interface.
8. Preserve todos os arquivos existentes e crie a interface em um arquivo separado, por exemplo interface.py.
9. A interface deve ser iniciada por:
python3 interface.py
10. A execução atual do projeto por python3 run.py deve continuar funcionando exatamente como antes.
4. Organização visual: abas
Crie uma janela de tamanho confortável, com visual limpo, consistente e sem excesso de decoração. Use textos em português do Brasil, boa hierarquia visual, espaçamento, botões com nomes claros e explicações curtas.

Crie as seguintes abas:
Aba 1 — Visão geral
Mostrar:
- título: N-Rainhas — Otimização com Busca Local;
- N = 30;
- objetivo: encontrar uma disposição com zero conflitos diagonais;
- representação: permutação de 0 a 29;
- espaço de estados: 30!;
- vizinhos por estado: C(30,2) = 435;
- métodos utilizados;
- uma explicação curta sobre o que será demonstrado.
Inclua uma pequena seção Como usar esta interface, com passos numerados:
1. Escolher um algoritmo.
2. Iniciar uma demonstração.
3. Observar o tabuleiro e o contador.
4. Consultar a comparação dos experimentos.
Aba 2 — Modelagem do problema
Explique de forma didática e direta:

Representação
- s[c] representa a linha da rainha na coluna c.
- Cada estado é uma permutação.
- Por construção, não existem conflitos de linha ou coluna.
Conflito diagonal
- Duas rainhas nas posições i e j entram em conflito quando abs(s[i] - s[j]) == abs(i - j).
- A função objetivo conta quantos pares estão em conflito.
- O objetivo é minimizar esse número até chegar a zero.
Espaço de estados
- Mostrar 30! e explicar que cada permutação é um estado possível.
- Mostrar 435 vizinhos, correspondentes à troca de dois valores.
Inclua uma legenda visual simples para o tabuleiro:
- rainha;
- rainha envolvida em conflito;
- posição sem conflito.
Aba 3 — Algoritmos
Crie três cartões ou seções explicativas, um para cada método:

1. Sorteio aleatório
- Gera uma permutação aleatória.
- Avalia a quantidade de conflitos.
- Repete até encontrar zero ou atingir o orçamento.
- Explique que é a linha de base aleatória.
2. Hill Climbing com reinício
- Avalia vizinhos obtidos pela troca de duas posições.
- Escolhe uma melhoria quando encontra uma.
- Quando fica preso em ótimo local ou platô, reinicia a partir de um novo estado.
- Explique que pode ficar preso em soluções com conflitos restantes.
3. Simulated Annealing
- Escolhe um vizinho por troca.
- Aceita melhorias.
- Pode aceitar movimentos piores conforme a temperatura e a probabilidade de aceitação.
- A temperatura diminui ao longo da execução.
- Explique que isso pode ajudar a escapar de ótimos locais, mas não garante encontrar a solução.
Inclua um pequeno glossário para:
- estado;
- vizinhança;
- função objetivo;
- avaliação;
- ótimo local;
- reinício;
- temperatura;
- semente aleatória;
- orçamento.
Não exagere no texto. Cada conceito deve ter uma explicação simples e correta.
Aba 4 — Demonstração ao vivo
Esta é a aba mais importante.

Permita escolher o método:
- Sorteio aleatório;
- Hill Climbing com reinício;
- Simulated Annealing.
Controles:
- botão Iniciar demonstração;
- botão Pausar/continuar, se a arquitetura permitir sem instabilidade;
- botão Cancelar execução;
- botão Nova execução.
Parâmetros:
- N deve permanecer fixo em 30 para corresponder aos experimentos e documentos;
- orçamento padrão de 10.000 avaliações;
- semente editável, com valor padrão reproduzível;
- não exponha dezenas de parâmetros técnicos na tela principal.
Durante a execução, mostrar em destaque:
- método selecionado;
- número atual de avaliações;
- orçamento máximo;
- conflitos atuais;
- melhor número de conflitos encontrado;
- estado atual (permutação ou uma versão resumida);
- status: executando, pausado, sucesso ou orçamento esgotado;
- tempo decorrido apenas como informação secundária, nunca como métrica principal de comparação.
Tabuleiro
- Desenhe um tabuleiro 30×30.
- Mostre as 30 rainhas nas posições do estado atual.
- Destaque visualmente as rainhas envolvidas em conflitos.
- Use uma legenda visível.
- Se o tabuleiro ficar pequeno, permita ampliar ou usar uma visualização simplificada; não omita o tabuleiro.
Explicação durante a execução
Mostre mensagens curtas que mudem conforme o algoritmo:
- sorteio: Gerando e avaliando uma nova permutação;
- HC: Explorando trocas e procurando uma melhoria;
- HC reinício: Sem melhoria local; iniciando novo estado;
- SA: Avaliando vizinho;
- SA aceitando piora: Movimento pior aceito pela temperatura atual;
- sucesso: Solução encontrada: 0 conflitos;
- orçamento esgotado: Orçamento de avaliações atingido.
Essas mensagens precisam corresponder ao que realmente acontece no código. Não invente eventos. Se o algoritmo atual não expõe esses eventos, faça a menor adaptação possível por callbacks opcionais, sem alterar o resultado ou a lógica de busca. Os callbacks não podem gerar avaliações extras.

Responsividade e segurança
- A janela não pode congelar durante uma execução.
- Execute o algoritmo em uma thread de trabalho ou mecanismo equivalente.
- Atualize widgets apenas pela thread principal do Tkinter.
- Não use time.sleep para simular progresso.
- Não faça a interface chamar conflitos() para atualizar a tela sem contabilizar: isso criaria avaliações escondidas.
- Use o valor de conflitos já calculado pelo algoritmo e os callbacks.
- Cancelar deve interromper a execução de forma segura e sem corromper os resultados.
- A interface deve deixar claro se a execução de demonstração não faz parte dos 30 experimentos oficiais.
Se a arquitetura atual não permitir atualização passo a passo sem modificar substancialmente o algoritmo, implemente uma demonstração em atualizações por lote, com contador correto e sem avaliações adicionais. Prefira fidelidade à aparência.
Aba 5 — Resultados experimentais
Leia os CSVs já produzidos pelo projeto e monte uma comparação visual e tabular.

Mostrar para cada método:
- execuções;
- sucessos e taxa de sucesso;
- média, melhor e pior avaliações até solução, calculados apenas sobre execuções bem-sucedidas;
- conflitos médios nas execuções sem solução;
- melhor e pior quantidade de conflitos nas falhas, se esses dados existirem no CSV;
- orçamento por execução.
Mostrar também:
- os resultados da calibração;
- configuração escolhida para cada método local;
- quantidade de execuções de calibração;
- orçamento da calibração.
Use gráficos simples e legíveis, sem poluição visual. Se não houver biblioteca gráfica instalada, faça gráficos simples com Canvas do Tkinter ou use tabelas bem formatadas. Não instale dependências só para desenhar gráficos.

Atenção à distribuição: a ficha pede análise da distribuição, não somente o melhor caso. Se os dados brutos permitirem, inclua também mediana e desvio-padrão ou um histograma/faixas de frequência. Não invente campos que não existam. Se o CSV não permitir calcular alguma métrica, indique que o dado não está disponível.
Aba 6 — Análise e limitações
Mostrar conclusões com linguagem cuidadosa:
- qual método teve melhor taxa de sucesso nesta amostra;
- comparação de custo em avaliações;
- por que o Hill Climbing pode ficar preso em ótimos locais;
- como o Simulated Annealing aceita algumas pioras;
- por que o sorteio aleatório funciona como linha de base;
- por que 30 execuções não provam superioridade universal;
- nenhum método tem garantia de encontrar solução dentro do orçamento utilizado;
- o resfriamento geométrico do SA não garante o ótimo;
- a calibração piloto foi pequena;
- a menção a ciclo genético na introdução da ficha não corresponde ao notebook fornecido; o trabalho implementa métodos de busca local e não utiliza crossover.
Não esconda limitações nem transforme resultados desta amostra em garantias gerais.
5. Demonstração preparada para apresentação
Inclua um botão ou roteiro Preparar demonstração que:
- selecione uma semente reproduzível;
- selecione um método;
- carregue o orçamento de 10.000;
- deixe o contador em destaque;
- abra a aba de demonstração.
Não execute automaticamente ao abrir. O estudante inicia quando estiver apresentando.

A demonstração deve ser curta o suficiente para uma apresentação ao vivo. Se uma execução completa levar muito tempo, permita acompanhar o contador e o melhor estado encontrado, com opção de encerrar. Não altere o orçamento dos experimentos oficiais.
6. Integração e testes
- Reutilize o motor de busca já implementado.
- Mantenha python3 run.py funcional.
- Mantenha todos os testes atuais passando.
- Acrescente testes pequenos para funções auxiliares da interface quando necessário.
- Verifique que abrir a interface não inicia experimentos automaticamente.
- Verifique que a interface não faz avaliações extras escondidas.
- Verifique que o cancelamento não deixa threads ou processos presos.
- Verifique que os CSVs são lidos sem alteração.
- Verifique que a interface funciona em resolução comum de notebook.
7. Entrega
Crie:
- interface.py (ou estrutura equivalente simples);
- eventuais módulos auxiliares apenas se forem realmente necessários;
- atualização curta no README.md explicando como abrir a interface.
Comando para abrir:
python3 interface.py
Comando para executar os experimentos e gerar documentos continua sendo:
python3 run.py
Não altere os documentos existentes sem necessidade. Se a interface revelar inconsistência nos dados, informe antes de modificar a ficha, o relatório ou os slides.
8. Resposta final obrigatória
Ao terminar, informe objetivamente:
1. Arquivos criados ou alterados.
2. Comando para abrir a interface.
3. Abas implementadas.
4. Como executar uma demonstração ao vivo.
5. Testes executados e resultado.
6. Limitações técnicas que permaneceram.
7. Confirmação de que python3 run.py continua funcionando.
Prioridade máxima: interface simples, estável, didática e fiel aos algoritmos e resultados existentes. Não transforme isso em um projeto de software maior do que o próprio TDE3.