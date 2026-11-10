PUCPR  |  Escola Politécnica  |  Bacharelado em Ciência da Computação
Inteligência Artificial (PCO118A)  ·  Prof. Carlos Costa Cedro
TDE3 — Otimização
Ficha de projeto  ·  preencher em sala em 20/10
RA3  ·  peso 4,0  ·  execução de 10/11 a 17/11  ·  apresentação em 17/11
Esta ficha é entregue ao final da aula de 21/10 e vale como registro da atividade. Ela existe para que nenhuma equipe saia da aula sem as decisões de modelagem fechadas, porque são elas que travam o trabalho quando tomadas em casa.
A base de código já é sua:  o notebook do laboratório de Algoritmos Genéticos traz o ciclo genético completo, o contador de avaliações da função objetivo e as linhas de base da Aula 8. Para rodá-lo sobre o seu problema você substitui apenas duas funções, `estado_aleatorio()` e `conflitos(s)`, e ajusta `N` e `APTIDAO_MAXIMA`. Não comece do zero.
Equipe
nomes completos


1. O problema
Problema escolhido
nome e uma frase dizendo o que se quer otimizar

Por que este problema
uma característica dele que faz você esperar que busca local seja adequada


2. Modelagem (ID3.1)
Representação
como um estado é codificado, concretamente

Tamanho do espaço |S|
com a conta à vista, não só o resultado

Vizinhança
qual é a modificação elementar, e quantos vizinhos por estado

Recombinação
o crossover de um ponto produz estados válidos nesta representação? se não, qual é o plano

Função objetivo
a fórmula, e se é de máximo ou de mínimo

Alvo conhecido?
existe valor ótimo conhecido, como os zero conflitos das oito rainhas? se não, como saberá que foi bem


3. Protocolo experimental (ID3.3)
Linhas de base
mínimo obrigatório: sorteio aleatório e Hill Climbing com reinício

Orçamento
quantas avaliações da função objetivo cada método terá. Igual para todos

Execuções e semente
quantas execuções por método, e qual semente


4. Verificação antes de sair da aula
Marque cada item e mostre ao professor. O entregável real do bloco não é a ficha preenchida, é o código rodando.
✓
Item

A função `estado_aleatorio()` foi substituída e devolve um estado do seu espaço

A função `conflitos(s)` foi substituída, incrementa `AVALIACOES` e devolve o valor a minimizar

`N` e `APTIDAO_MAXIMA` foram ajustados ao seu problema

Pelo menos uma linha de base já produziu número sobre o seu problema

O tamanho do espaço |S| foi calculado e conferido com o professor

5. Critérios de avaliação
Critério
Peso
Indicador
Modelagem: representação, vizinhança e função objetivo especificadas e justificadas
1,0
ID3.1
Implementação correta de ao menos dois métodos de busca local sobre o problema
1,0
ID3.2
Protocolo reprodutível, com orçamento e calibração simétricos
1,0
ID3.3
Análise dos resultados, com distribuição reportada e garantias ausentes declaradas
1,0
ID3.3

6. As três formas de perder nota por comparação injusta
São as três falhas da atividade de auditoria de 28/10. Elas valem nota, e estão anunciadas de antemão.
A falha
Como se manifesta
Como evitar
Unidade de custo incomparável
Comparar gerações com iterações, ou qualquer coisa com segundos. Uma geração com população 50 custa 50 avaliações; uma iteração de Simulated Annealing custa 1; um lance de busca custa milhares de nós
Medir tudo na mesma unidade, declarada no relatório
Calibração assimétrica
Varrer dezenas de configurações de um método e comparar contra o outro nos valores padrão. Isso mede a diferença entre calibrar e não calibrar
Mesmo esforço de calibração dos dois lados, declarado no relatório
Melhor caso, sem linha de base
Reportar a melhor de N execuções. Isso mede a sorte, não o método
Reportar média, pior caso e taxa de sucesso. Sempre incluir a linha de base trivial

7. Armadilhas na escolha do problema
Escolha
O que dá errado
Redirecionamento
Caixeiro viajante com poucas cidades
O espaço é pequeno e a enumeração resolve, o que não justifica busca local
Usar 30 ou mais cidades, ou manter e usar o ótimo exato como referência de qualidade
Problema sem função objetivo natural
A equipe gasta o trabalho inteiro discutindo como pontuar uma solução
Exigir que a função objetivo caiba em cinco linhas de código
Restrições duras complexas
A maioria dos estados gerados é inválida, como no crossover sobre permutações
Escolher representação que satisfaça as restrições por construção, ou trocar de problema
Reimplementar as oito rainhas
Não há trabalho de modelagem, que é justamente o ID3.1
Aceito só se generalizarem para n rainhas com n grande e mudarem a representação
Roteiro da apresentação
Em 17/11, cada equipe tem 12 minutos, com 3 minutos de arguição. A apresentação é avaliada pelo mesmo instrumento do relatório, e não separadamente.
Tempo
O que mostrar
1 min
O problema e por que ele é adequado ao método. Sem introdução histórica
3 min
A modelagem: representação, o tamanho do espaço com a conta, e o que a representação torna impossível por construção
3 min
Uma execução ao vivo ou gravada, com o contador de custo visível na tela
3 min
A tabela de comparação contra as linhas de base, na mesma unidade e com a distribuição, não só o melhor caso
2 min
O que não funcionou, e as garantias que o seu sistema não tem

O item que mais pesa e que as equipes costumam pular:  o último. Uma apresentação que só mostra o que deu certo perde pontos no indicador de avaliação de resultados. Declarar explicitamente uma limitação medida vale mais que um resultado bonito sem ressalva.
