# Análise de Materiais por Espectroscopia de Raios X 🔬

Um programa em Python desenvolvido para assistir na caracterização química e identificação de materiais desconhecidos com base nos seus espetros de emissão de raios X. O projeto foi construído no âmbito da disciplina de Informática para Ciências e Engenharias.

## 🎯 Objetivos do Projeto

O objetivo principal é processar ficheiros de texto contendo os resultados experimentais de equipamentos de espectroscopia, detetar **picos de energia** de forma avançada (filtrando o ruído de fundo) e compará-los com uma base de dados científica de emissões de raios X. Através de um sistema de avaliação de plausibilidade (*score*), o programa é capaz de cruzar a amostra e identificar os elementos químicos predominantes.

## 🚀 Funcionalidades

- **Base de Dados e Scraping (`initdb`)**: Criação de tabelas relacionais em **SQLite** e importação e parsing de referências atómicas e linhas de emissão originais a partir da internet via *urllib*.
- **Algoritmo de Deteção de Picos (`analyze`)**: Um algoritmo avançado de análise de sinal que procura máximos locais em cada varrimento energético, removendo anomalias se a intensidade for menor a 5% do cume principal e as energias inferiores a 0.5 KeV.
- **Identificação de Elementos**: Determinação de pontuações de elementos pela proximidade em $\pm 0.025 \text{ keV}$, compensando perdas de resolução nas máquinas experimentais através de análise da janela estrita superior. 
- **Estatísticas e Histórico (`stats`, `report`)**: Consulta do armazenamento relacional das últimas amostras, devolvendo rapidamente históricos, o número de deteções, contagens máximas e mínimas para um qualquer químico.
- **Visualização Gráfica (`chart`)**: Renderização num gráfico contínuo dos espetros usando a biblioteca gráfica **Matplotlib**. Deteção automática das etiquetas dos elementos vencedores no pico das suas emissões para facilidade visual.

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3.x
- **Bases de Dados**: `sqlite3` (embutido)
- **Pacotes Externos**: `matplotlib` (para plot dos gráficos)
- **Bibliotecas Standard**: `urllib`, `os`

## ⚙️ Como Instalar e Executar

1. **Clona este repositório**:
   ```bash
   git clone https://github.com/ic3K1ng/Analise-de-Materiais-por-Espectroscopia-de-Raios-X.git
   cd Analise-de-Materiais-por-Espectroscopia-de-Raios-X
   ```

2. **Instala os Requisitos**:
   O único requisito externo necessário é a ferramenta de manipulação de gráficos:
   ```bash
   pip install matplotlib
   ```

3. **Inicia a Aplicação**:
   Navega até à diretoria do código e corre o script.
   ```bash
   cd "Análise de Materiais por Espectroscopia de Raios X"
   python prog.py
   ```

## ⌨️ Comandos Disponíveis (CLI)

Após iniciar o programa, será apresentada uma linha de comandos local `>> `. 

| Comando | Função | Exemplo |
| :--- | :--- | :--- |
| `initdb` | Descarrega a biblioteca atómica da internet e inicializa o SQLite. | `>> initdb` |
| `analyze <file>` | Extrai os dados do txt da amostra, deteta os picos, correlaciona com as assinaturas radiológicas e grava tudo. | `>> analyze SrF3.txt` |
| `report <file>` | Verifica os últimos dados de identificação na tabela e imprime no terminal o relatório. | `>> report SrF3.txt` |
| `stats <element>`| Regressa ao registo histórico e resume as visualizações daquele elemento ao longo das experiências. | `>> stats Al` |
| `chart <file>` | Desenha e lança a janela em *matplotlib* mostrando a topografia do sinal em função da energia com a legenda do Elemento Químico exato associado a cada pico. | `>> chart SrF3.txt` |
| `quit` | Fecha o programa em segurança. | `>> quit` |

---
*Desenvolvido como projeto prático universitário de avaliação de conhecimentos.*
