# Fases de Desenvolvimento - Análise de Materiais por Espectroscopia de Raios X

Este documento descreve as fases de desenvolvimento do projeto implementado em `prog.py` para a disciplina de Informática para Ciências e Engenharias, com base no enunciado do trabalho prático.

---

## 📅 Cronograma e Fases de Desenvolvimento

### Fase 1: Análise de Requisitos e Modelagem da Base de Dados
*   **Objetivo**: Desenhar a estrutura relacional para suportar o armazenamento de elementos, linhas de emissão e históricos de análise.
*   **Tarefas Realizadas**:
    *   Definição e criação do esquema SQLite contendo quatro tabelas: `Elementos`, `Linhas`, `Analisados` e `Resultados`.
    *   Estabelecimento de chaves primárias e chaves estrangeiras para garantir a integridade dos dados (ex: associar `Resultados` a `Elementos` e `Analisados`).

### Fase 2: Aquisição e Ingestão Automática de Dados
*   **Objetivo**: Popular o sistema com os dados científicos de referência obtidos da internet.
*   **Tarefas Realizadas**:
    *   Implementação do comando `initdb` para redefinir a base de dados.
    *   Download automatizado usando `urllib.request` para obter a lista de elementos (`elements.txt`) e as linhas de emissão de raios X correspondentes (`xray-lines.txt`).
    *   Parsing robusto das strings e inserção em massa nas tabelas `Elementos` e `Linhas`.

### Fase 3: Processamento de Sinal e Deteção de Picos (Algoritmo Avançado)
*   **Objetivo**: Filtrar o ruído dos espectrogramas experimentais e encontrar os picos reais de energia.
*   **Tarefas Realizadas**:
    *   Leitura e interpretação dos ficheiros de espectro de amostras (ignoring a linha de cabeçalho).
    *   Implementação de um algoritmo de picos locais: um ponto representa um pico se a contagem for estritamente superior à do ponto anterior e à do ponto seguinte ($contagem_{i-1} < contagem_i > contagem_{i+1}$).
    *   Aplicação de filtro de ruído: eliminação de medições com contagem inferior a 5% do pico máximo do espectrograma.
    *   Filtragem por energia: eliminação de picos com valor de energia inferior a 0.5 keV.

### Fase 4: Identificação de Elementos Químicos e Cálculo de Score
*   **Objetivo**: Associar cada pico detetado aos elementos químicos que mais plausivelmente os explicam.
*   **Tarefas Realizadas**:
    *   Seleção de candidatos com linhas de emissão na vizinhança do pico ($\pm 0.025 \text{ keV}$).
    *   Criação de um algoritmo de classificação de candidatos baseado no somatório das razões entre a intensidade do espectro e o peso de cada linha de emissão ($\sum \frac{\text{contagem}_i}{\text{peso}_i}$).
    *   Resolução de limitações de resolução: busca do valor energético imediatamente superior no espectrograma quando a energia exata da linha de emissão não consta no ficheiro da amostra.
    *   Atribuição e registo do elemento vencedor na base de dados.

### Fase 5: Relatórios e Estatísticas (Interface Textual)
*   **Objetivo**: Permitir a consulta rápida e estatística das análises guardadas na base de dados.
*   **Tarefas Realizadas**:
    *   Implementação do comando `report` para listar ordenadamente os picos, os nomes completos dos elementos identificados e as suas respetivas contagens.
    *   Implementação do comando `stats` para consolidar o histórico de análises de um determinado elemento químico, fornecendo número de ocorrências, contagem máxima e mínima observadas.

### Fase 6: Visualização Gráfica
*   **Objetivo**: Proporcionar uma interface visual intuitiva para a validação dos espectros e dos picos detetados.
*   **Tarefas Realizadas**:
    *   Uso do pacote `matplotlib.pyplot` no comando `chart` para desenhar o gráfico contínuo de energia (keV) versus contagem.
    *   Plotagem de marcadores circulares pretos nos picos detetados e anotação lateral dos elementos identificados.

### Fase 7: Revisão de Qualidade e Afinação de Requisitos
*   **Objetivo**: Garantir conformidade absoluta com o enunciado do trabalho prático.
*   **Tarefas Realizadas**:
    *   Ajuste na formatação do gráfico para exibir o **Nome Completo** do elemento no gráfico em vez do símbolo (ex: "Strontium" no lugar de "Sr"), conforme os exemplos fornecidos.
    *   Preenchimento da identificação dos alunos no cabeçalho do código principal.
    *   Testes globais de robustez com as amostras de teste (`unknown1`, `unknown2`, `unknown3`).
