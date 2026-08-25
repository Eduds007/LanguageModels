# Language Models in Portuguese

This project aims to develop language models in Portuguese. Specifically, developing a DPR (Dense Passage Retriever) trained on Portuguese datasets.

> **This project is about two years old** (the timeline below runs from 09/23 to 06/24). It was developed at a time when Portuguese language models and the available encoders were much more limited than they are today — read the results with that context in mind.

**Scholarship holder**: Eduardo Milanez Araujo & Eduardo Figueiredo Pacheco \
**Advisor**: Fabio Gagliardi Cozman

[Project description](https://drive.google.com/file/d/1U2_mAwZgv8FBG5XjLi2hJwu-egMeKk9Q/view?usp=sharing)

## Project timeline

| Activities | 09/23 | 10/23 | 11/23 |  12/23 |  01/24 |  02/24 |  03/24 |  04/24 |  05/24 |  06/24 | 
|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| 1. Literature review      | X      | X      |       |       |       |     |    | |  |  |
| 2. Model and data selection      | X        | X         | X           |     |     |   |     |     |    |     |
| 3. DPR training      |      |     | X          | X        | X           |     |     |   |  |     |     |
| 4. LLaMa-based training      |      |      |   |    | X          | X        | X          |          |      |     |     |
| 5. DPR model analysis      |      |     |       |      |     |      |    X  |  X  |     |      |     |
| 6. Generative model evaluation      | | | | | | | |      X | X     |   |  |
| 7. Repository setup      |       |       |       |       |       |      |       |       |      X | X      |       |
| 8. Report writing      |     |     |     |     |  X |    |     |    |     | X |



## Main libraries used

> **Note:** the DPR training originally used the [Haystack](https://github.com/deepset-ai/haystack) library, but it hasn't been updated since ~2024 and is no longer compatible with current versions of `transformers`/`numpy`/`scipy`. Training in `3. Treino do DPR/` was rewritten directly in `torch`/`transformers`, without that dependency — see [`3. Treino do DPR/README.md`](./3.%20Treino%20do%20DPR/README.md).

 [Datasets](https://github.com/huggingface/datasets): Library for reusing language models produced by other researchers. 
  ```
  pip install datasets
  ```

# 

# Running the project

The front/back-end (chat) is dockerized, and can be run with:

If it's the first time:
  ```
  cd LanguageModels
  cd src
  sudo docker-compose up --build
  ```
Otherwise:
  ```
  cd LanguageModels
  cd src
  sudo docker-compose up
  ```

DPR training (`3. Treino do DPR/`) runs outside of docker, in a Python venv —
see instructions, results, and limitations in [`3. Treino do DPR/README.md`](./3.%20Treino%20do%20DPR/README.md).

## DPR results and limitations

The baseline (bert-base-uncased, 5k-example dataset, 1 epoch) reached **36.9%
top-1 accuracy on the test set** (vs. ~3% chance level) — see the training
folder's README for details on how this metric is computed.

A second config, using a Portuguese-pretrained encoder (BERTimbau) and the
larger dataset (50k examples), **was not completed**: the available hardware
showed instability under sustained load (recurring crashes during training,
including one full machine freeze), preventing this heavier training run from
finishing. Contributions to finish this training — or to revisit the project
with more modern encoders — are very welcome.




# NLP and Information Retrieval Project Summary

This project explores advanced Natural Language Processing (NLP) and Information Retrieval techniques, focusing on human-machine interaction through language. Using the Python programming language, the code covers everything from data handling to training Dense Passage Retrieval (DPR) models.

## Haystack library (historical)

Training originally used the [Haystack](https://github.com/deepset-ai/haystack) library for search and information retrieval tasks — it allows building search systems that understand context and semantics, integrating with machine learning models. It is no longer used in the current training code (see note above), but is kept here for the project's historical context.

## Data processing

Data processing is a crucial step in this project, involving the cleaning, preparation, and manipulation of datasets for model training and evaluation. This process is fundamental to ensuring NLP models can learn effectively, by removing noise and properly structuring the data.

## Dense Passage Retrieval (DPR)

DPR is a prominent technique that enables efficient retrieval of text passages relevant to a given query. It works by training models to understand the semantics of questions and documents, creating dense vector representations that facilitate search by semantic similarity.

## Importance of DPR

Implementing and training the DPR is essential to the success of the search system, highlighting the importance of deep learning models in advancing NLP capabilities. This approach surpasses traditional keyword-based search methods, offering more accurate and contextually relevant answers.


## Portuguese dataset

One of this project's main contributions is providing a question-and-answer dataset with over 50,000 passages translated using a translation model specifically trained for converting English text to Portuguese: [NQ-PT-BR](https://huggingface.co/datasets/edu-milanez/NQ-PT-BR)
