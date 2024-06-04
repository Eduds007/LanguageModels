# Modelos de linguagem em Português

Esse projeto visa desenvolver modelos de linguagem em Português. Em específico, desenvolver um DPR (Dense Passage Retriever) treinado com bases de dados em português.

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

 [Haystack](https://github.com/deepset-ai/haystack): Biblioteca para treinamento do DPR. 
  ```
  pip install haystack
  ```
 [Datasets](https://github.com/huggingface/datasets): Biblioteca para reutilizar modelos de linguagem produzidos por outros pesquisadores. 
  ```
  pip install datasets
  ```

# 

# Executando o projeto

Para poder executar o projeto, que está em um docker, basta executar os comandos: 

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





# Resumo do Projeto de NLP e Recuperação de Informações

Este projeto explora técnicas avançadas de Processamento de Linguagem Natural (NLP) e Recuperação de Informações, focando na interação entre humanos e máquinas através da linguagem. Utilizando a linguagem de programação Python, o código abrange desde o tratamento de dados até o treinamento de modelos de Dense Passage Retrieval (DPR), incluindo o uso da biblioteca Haystack para aprimorar a busca e recuperação de informações em textos.

## Biblioteca Haystack

A biblioteca [Haystack](https://github.com/deepset-ai/haystack) é uma ferramenta poderosa para tarefas de busca e recuperação de informações. Ela permite a construção de sistemas de busca que compreendem o contexto e a semântica do conteúdo pesquisado, integrando-se com modelos de machine learning para oferecer respostas precisas a consultas complexas.

## Tratamento de Dados

O tratamento de dados é uma etapa crucial neste projeto, envolvendo a limpeza, preparação e manipulação de conjuntos de dados para treinamento e avaliação dos modelos. Este processo é fundamental para garantir que os modelos de NLP possam aprender de maneira eficaz, removendo ruídos e estruturando os dados adequadamente.

## Dense Passage Retrieval (DPR)

O DPR é uma técnica de destaque que permite a recuperação eficiente de passagens de texto relevantes para uma dada consulta. Funciona através do treinamento de modelos para entender a semântica das perguntas e dos documentos, criando representações vetoriais densas que facilitam a busca por similaridade semântica.

## Importância do DPR

A implementação e o treinamento do DPR são essenciais para o sucesso do sistema de busca, destacando a importância de modelos de aprendizado profundo no avanço das capacidades de NLP. Esta abordagem supera os métodos tradicionais de busca por palavras-chave, oferecendo respostas mais precisas e contextualmente relevantes.


