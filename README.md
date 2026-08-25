# Modelos de linguagem em Português

Esse projeto visa desenvolver modelos de linguagem em Português. Em específico, desenvolver um DPR (Dense Passage Retriever) treinado com bases de dados em português.

> **Projeto com cerca de dois anos** (cronograma abaixo é de 09/23 a 06/24). Foi
> desenvolvido numa época em que os modelos de linguagem em português e os
> encoders disponíveis eram bem mais limitados do que os de hoje — leia os
> resultados com esse contexto em mente.

**Bolsista**: Eduardo Milanez Araujo & Eduardo Figueiredo Pacheco \
**Orientador**: Fabio Gagliardi Cozman

[Descrição do projeto](https://drive.google.com/file/d/1U2_mAwZgv8FBG5XjLi2hJwu-egMeKk9Q/view?usp=sharing)

## Cronograma do projeto

| Atividades | 09/23 | 10/23 | 11/23 |  12/23 |  01/24 |  02/24 |  03/24 |  04/24 |  05/24 |  06/24 | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1. Revisão bibliográfica      | X      | X      |       |       |       |     |    | |  |  |
| 2. Seleção de modelos e dados      | X        | X         | X           |     |     |   |     |     |    |     |
| 3. Treino do DPR      |      |     | X          | X        | X           |     |     |   |  |     |     |
| 4. Treino baseado em LLaMa      |      |      |   |    | X          | X        | X          |          |      |     |     |
| 5. Análise de modelos DPR      |      |     |       |      |     |      |    X  |  X  |     |      |     |
| 6. Avaliação de modelo generativo      | | | | | | | |      X | X     |   |  |
| 7. Elaboração de repositório      |       |       |       |       |       |      |       |       |      X | X      |       |
| 8. Elaboração de relatórios      |     |     |     |     |  X |    |     |    |     | X |



## Principais bibliotecas utilizadas

> **Nota:** o treino do DPR originalmente usava a lib [Haystack](https://github.com/deepset-ai/haystack), mas ela está sem atualização desde ~2024 e não é mais compatível com as versões atuais de `transformers`/`numpy`/`scipy`. O treino em `3. Treino do DPR/` foi reescrito direto em `torch`/`transformers`, sem essa dependência — ver [`3. Treino do DPR/README.md`](./3.%20Treino%20do%20DPR/README.md).

 [Datasets](https://github.com/huggingface/datasets): Biblioteca para reutilizar modelos de linguagem produzidos por outros pesquisadores. 
  ```
  pip install datasets
  ```

# 

# Executando o projeto

O front/back-end (chat) está em docker, e pode ser executado com:

Se for a primeira vez:
  ```
  cd LanguageModels
  cd src
  sudo docker-compose up --build
  ```
Caso contrário:
  ```
  cd LanguageModels
  cd src
  sudo docker-compose up
  ```

Já o treino do DPR (`3. Treino do DPR/`) roda fora do docker, num venv Python —
ver instruções, resultados e limitações em [`3. Treino do DPR/README.md`](./3.%20Treino%20do%20DPR/README.md).

## Resultados do DPR e limitações

O baseline (bert-base-uncased, dataset de 5k exemplos, 1 época) atingiu **36.9%
de accuracy top-1 no conjunto de teste** (contra ~3% de chance) — ver detalhes de
como essa métrica é calculada no README da pasta de treino.

Uma segunda config, com um encoder pré-treinado em português (BERTimbau) e o
dataset maior (50k exemplos), **não foi concluída**: o hardware disponível
apresentou instabilidade sob carga sustentada (crashes recorrentes durante o
treino, incluindo um travamento completo da máquina), impedindo terminar esse
treino mais pesado. Contribuições terminando esse treino — ou revisitando o
projeto com encoders mais modernos — são muito bem-vindas.





# Resumo do Projeto de NLP e Recuperação de Informações

Este projeto explora técnicas avançadas de Processamento de Linguagem Natural (NLP) e Recuperação de Informações, focando na interação entre humanos e máquinas através da linguagem. Utilizando a linguagem de programação Python, o código abrange desde o tratamento de dados até o treinamento de modelos de Dense Passage Retrieval (DPR).

## Biblioteca Haystack (histórico)

O treino originalmente usava a biblioteca [Haystack](https://github.com/deepset-ai/haystack) pra tarefas de busca e recuperação de informações — ela permite construir sistemas de busca que compreendem contexto e semântica, integrando-se com modelos de machine learning. Ela não é mais usada no treino atual (ver nota acima), mas fica registrada aqui pelo contexto histórico do projeto.

## Tratamento de Dados

O tratamento de dados é uma etapa crucial neste projeto, envolvendo a limpeza, preparação e manipulação de conjuntos de dados para treinamento e avaliação dos modelos. Este processo é fundamental para garantir que os modelos de NLP possam aprender de maneira eficaz, removendo ruídos e estruturando os dados adequadamente.

## Dense Passage Retrieval (DPR)

O DPR é uma técnica de destaque que permite a recuperação eficiente de passagens de texto relevantes para uma dada consulta. Funciona através do treinamento de modelos para entender a semântica das perguntas e dos documentos, criando representações vetoriais densas que facilitam a busca por similaridade semântica.

## Importância do DPR

A implementação e o treinamento do DPR são essenciais para o sucesso do sistema de busca, destacando a importância de modelos de aprendizado profundo no avanço das capacidades de NLP. Esta abordagem supera os métodos tradicionais de busca por palavras-chave, oferecendo respostas mais precisas e contextualmente relevantes.


## Base de dados em português

Uma das principais contribuições desse projeto consiste em fornecer uma base perguntas e respostas com mais de 50000 passagens traduzidas com a utilização de um modelo de tradução treinado especificamente para a conversão de textos em inglês para português [NQ-PT-BR](https://huggingface.co/datasets/edu-milanez/NQ-PT-BR)