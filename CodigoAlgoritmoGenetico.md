Aqui está a documentação técnica completa e estruturada em Markdown sobre **Algoritmos Genéticos (AG)** extraída das fontes, contendo pseudocódigos, operadores, fórmulas de cálculo e especificações de custo.

---

# Especificação Técnica de Algoritmos Genéticos (AG)

## 1. Estrutura Estrutural e Ciclo do Algoritmo (`ALGORITMO-GENETICO`)

O algoritmo genético é uma busca local populacional que mantém \\(k\\) estados simultâneos e permite a produção de um novo estado a partir da recombinação de dois progenitores.

### Parâmetros e Decisões de Configuração (7 Parâmetros Livres)
1. `k`: Tamanho da população (quantidade de indivíduos mantidos simultaneamente).
2. `p_cross`: Probabilidade de aplicação do operador de recombinação (crossover).
3. `p_mut`: Probabilidade de mutação aplicada de forma independente por gene.
4. `G` (`geracoes`): Orçamento máximo de gerações/iterações do algoritmo.
5. `E`: Tamanho do elitismo (\\(E \ge 1\\)), definindo quantos dos melhores indivíduos passam intactos para a geração seguinte.
6. `SELECIONA`: Mecanismo estocástico de seleção de progenitores.
7. `RECOMBINA`: Operador de crossover.

### Pseudocódigo Formal

```pseudocode
função ALGORITMO-GENETICO(problema, k, p_cross, p_mut, G, E):
    populacao ← k estados sorteados aleatoriamente
    
    para g = 1 até G:
        avaliar a aptidão (fitness) de cada indivíduo em populacao
        
        se algum indivíduo atingiu a aptidão alvo:
            devolva esse indivíduo
            
        nova_populacao ← os E melhores indivíduos de populacao  # Elitismo
        
        enquanto tamanho(nova_populacao) < k:
            pai1 ← SELECIONA(populacao)
            pai2 ← SELECIONA(populacao)
            
            se sorteio_uniforme(0, 1) < p_cross:
                filho ← RECOMBINA(pai1, pai2)
            senão:
                filho ← cópia de pai1
                
            para cada gene do filho:
                se sorteio_uniforme(0, 1) < p_mut:
                    substitua o gene por um valor aleatório do domínio
                    
            acrescente filho a nova_populacao
            
        populacao ← nova_populacao
        
    devolva o melhor indivíduo encontrado em populacao
```


---

## 2. Mecanismos de Seleção (`SELECIONA`)

### a) Seleção por Roleta (Roulette Wheel)
- **Fórmula de probabilidade**:
  \\[P(\text{indivíduo } i) = \frac{f_i}{\sum_{j=1}^{N} f_j}\\]
  onde \\(f_i\\) é a aptidão (fitness) do indivíduo \\(i\\).
- **Comportamento**: É sensível à escala dos valores de aptidão. Indivíduos com aptidão muito acima da média podem dominar a seleção em poucas gerações.

### b) Seleção por Torneio de Tamanho \\(t\\)
- **Funcionamento**: Sorteia \\(t\\) indivíduos da população uniformemente (com reposição) e escolhe o de maior aptidão do grupo.
- **Probabilidade do melhor indivíduo ser selecionado**:
  \\[P(\text{melhor}) = 1 - \left(\frac{N - 1}{N}\right)^t\\]
  onde \\(N\\) é o tamanho total da população.
- **Comportamento**: Depende apenas da ordenação dos indivíduos e não da escala numérica da aptidão. O valor de \\(t\\) (ex: \\(t=3\\)) ajusta a pressão seletiva.

### c) Elitismo (\\(E \ge 1\\))
- **Funcionamento**: Copia os \\(E\\) melhores indivíduos diretamente para a próxima geração sem modificação por crossover ou mutação.
- **Propriedade Demostrada**: Garante que a melhor aptidão da população é monotonicamente não decrescente ao longo das gerações (\\(f_{\text{max}}(g+1) \ge f_{\text{max}}(g)\\)).

---

## 3. Operadores de Recombinação (Crossover) e Mutação

### Operadores de Crossover
1. **Um Ponto**: Sorteia uma posição de corte \\(k \in [1, L-1]\\). O filho recebe o prefixo \\([1 \dots k]\\) do Pai 1 e o sufixo \\([k+1 \dots L]\\) do Pai 2.
2. **Dois Pontos**: Sorteia duas posições de corte. O filho herda o segmento central de um progenitor e os dois segmentos extremos do outro.
3. **Uniforme**: Aplica uma máscara binária de comprimento \\(L\\). Onde a máscara é `1`, herda do Pai 1; onde é `0`, herda do Pai 2.

#### Compatibilidade entre Representação e Crossover
- Em **representações livres/vetoriais**, o crossover de um ponto gera descendentes válidos por construção.
- Em **representações por permutação** (ex: problema das N rainhas), o crossover de um ponto produz estados inválidos (elementos duplicados e faltantes) em aproximadamente **\\(94,7\%\\)** dos casos.
- Probabilidade exata de validade em permutações sob corte uniforme \\(k\\):
  \\[P(\text{válido} \mid k) = \frac{1}{\binom{L}{k}}\\]
  \\[P(\text{válido}) = \frac{1}{L - 1} \sum_{k=1}^{L-1} \frac{1}{\binom{L}{k}}\\]

- Para permutações, utilizam-se operadores específicos como **Order Crossover (OX)** ou **PMX**, que mantêm a permutação válida por construção.

### Operador de Mutação
- Aplica-se a cada gene individualmente de forma independente com probabilidade \\(p_{\text{mut}}\\).
- **Mutações esperadas por filho**:
  \\[E[\text{mutações}] = L \times p_{\text{mut}}\\]

- **Probabilidade de um filho não sofrer mutações**:
  \\[P(\text{zero mutação}) = (1 - p_{\text{mut}})^L\\]


---

## 4. Teorema do Esquema (Holland, 1975)

Um **esquema \\(H\\)** é um padrão parcial de cromossomo contendo posições fixas e livres (`*`).
- **Ordem \\(o(H)\\)**: Quantidade de posições fixas no esquema.
- **Comprimento de Definição \\(\delta(H)\\)**: Distância entre a primeira e a última posição fixa (\\(\text{posição}_{\text{última}} - \text{posição}_{\text{primeira}}\\)).

### Desigualdade da Cota Inferior (\\(t \to t+1\\))
\\[E[m(H, t+1)] \ge m(H, t) \cdot \frac{f(H)}{\bar{f}} \cdot \left[ 1 - p_{\text{cross}} \cdot \frac{\delta(H)}{L - 1} - o(H) \cdot p_{\text{mut}} \right]\\]

Onde:
- \\(m(H, t)\\): Número de representantes de \\(H\\) na geração \\(t\\).
- \\(f(H)\\): Aptidão média dos representantes de \\(H\\).
- \\(\bar{f}\\): Aptidão média da população inteira na geração \\(t\\).
- \\(L\\): Comprimento do cromossomo.

---

## 5. Protocolo de Avaliação e Custo Computacional

1. **Unidade de Custo**: O custo computacional deve ser medido exclusivamente em **avaliações da função objetivo (\\(f\\))**, ignorando contagens de gerações, passos ou tempo de CPU.
2. **Custo por Geração**: Uma geração de um algoritmo genético com população \\(k\\) equivale a exatamente \\(k\\) avaliações da função objetivo.
3. **Comparação Experimental**: Testes contra algoritmos de linha de base (como *Hill Climbing com Reinício Aleatório* e *Simulated Annealing*) exigem pareamento estrito pelo mesmo orçamento total de avaliações de \\(f\\).