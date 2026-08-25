# Treino do DPR

Pipeline de treino de um DPR (Dense Passage Retriever) em português: dois encoders
BERT-like (query e passage) treinados para aproximar pergunta e passagem correta no
espaço de embeddings, com NLL loss sobre positivo + negativos difíceis + negativos
"in-batch" (mesma formulação do paper original, Karpukhin et al., 2020).

> **Este projeto tem cerca de dois anos.** Ele foi feito numa época em que os
> modelos de linguagem em português (e os encoders disponíveis em geral) eram
> bem mais limitados do que os de hoje. Os números abaixo refletem esse contexto —
> hoje em dia provavelmente dá pra conseguir resultados bem melhores trocando os
> encoders base por opções mais recentes.

## Como rodar

```bash
cd "3. Treino do DPR"
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Converter o dataset SQuAD-like para o formato DPR (minera negativos difíceis
   localmente com TF-IDF, sem precisar de Elasticsearch/Haystack):

   ```bash
   python squad_to_dpr.py --squad_input_filename data-5k.json \
       --dpr_output_filename data-5k-dpr.json --split_dataset
   ```

2. Treinar, escolhendo a config:

   ```bash
   python dpr.py --run baseline    # bert-base-uncased, dataset 5k, 1 época
   python dpr.py --run modified    # BERTimbau, dataset 50k, 3 épocas
   ```

   Cada execução salva config, log e checkpoints em `runs/<config>_<timestamp>/`.

3. Comparar execuções já feitas:

   ```bash
   python compare_runs.py
   ```

4. (Opcional) Subir um serviço de retrieval real com um checkpoint treinado —
   ver `../dpr_service.py` na raiz do projeto, que carrega os encoders salvos e
   indexa as passagens pra responder queries via API.

## Taxa de acerto (baseline)

Config `baseline` (bert-base-uncased, `data-5k.json`, 1 época) — métrica é a
accuracy top-1: dado um lote, o modelo tem que apontar qual das passagens
candidatas do lote é a resposta certa pra cada pergunta (positivo + negativos
difíceis + negativos "in-batch" de outras perguntas do mesmo lote).

| Conjunto | Accuracy | Chance level* |
|----------|----------|----------------|
| dev      | 40.0%    | ~3% |
| test     | 36.9%    | ~3% |

\* Cada pergunta tem ~32 passagens candidatas no lote (batch 16 × 2 passagens/pergunta), então acertar no chute daria ~3%.

## Limitações / trabalho não concluído

A config `modified` (BERTimbau + dataset de 50k + mais épocas) **não foi
concluída** — o hardware disponível durante o desenvolvimento (CPU com
instabilidade sob carga sustentada) causava crashes recorrentes e, em um caso,
travou a máquina por completo, impedindo terminar esse treino maior.

Se alguém quiser contribuir terminando esse treino (ou testando com hardware
mais estável / encoders mais modernos), seria muito bem-vindo — o pipeline e os
dados já estão prontos, só falta rodar até o fim.
