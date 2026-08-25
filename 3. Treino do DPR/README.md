# DPR Training

Training pipeline for a Portuguese DPR (Dense Passage Retriever): two BERT-like
encoders (query and passage) trained to bring the correct question and passage
close together in embedding space, using an NLL loss over the positive + hard
negatives + "in-batch" negatives (same formulation as the original paper,
Karpukhin et al., 2020).

> **This project is about two years old.** It was built at a time when
> Portuguese language models (and available encoders in general) were much
> more limited than today's. The numbers below reflect that context — nowadays
> you'd likely get much better results by swapping in more recent base
> encoders.

## How to run

```bash
cd "3. Treino do DPR"
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. Convert the SQuAD-like dataset to DPR format (mines hard negatives locally
   with TF-IDF, no need for Elasticsearch/Haystack):

   ```bash
   python squad_to_dpr.py --squad_input_filename data-5k.json \
       --dpr_output_filename data-5k-dpr.json --split_dataset
   ```

2. Train, picking a config:

   ```bash
   python dpr.py --run baseline    # bert-base-uncased, 5k dataset, 1 epoch
   python dpr.py --run modified    # BERTimbau, 50k dataset, 3 epochs
   ```

   Each run saves its config, log, and checkpoints to `runs/<config>_<timestamp>/`.

3. Compare runs already done:

   ```bash
   python compare_runs.py
   ```

4. (Optional) Serve real retrieval with a trained checkpoint — see
   `../dpr_service.py` at the project root, which loads the saved encoders and
   indexes the passages to answer queries via an API.

## Accuracy (baseline)

`baseline` config (bert-base-uncased, `data-5k.json`, 1 epoch) — the metric is
top-1 accuracy: given a batch, the model has to point to which of the
candidate passages in the batch is the correct answer for each question
(positive + hard negatives + "in-batch" negatives from other questions in the
same batch).

| Split | Accuracy | Chance level* |
|----------|----------|----------------|
| dev      | 40.0%    | ~3% |
| test     | 36.9%    | ~3% |

\* Each question has ~32 candidate passages in the batch (batch size 16 × 2 passages/question), so guessing randomly would give ~3%.

## Limitations / unfinished work

The `modified` config (BERTimbau + 50k dataset + more epochs) **was not
completed** — the hardware available during development (a CPU that was
unstable under sustained load) caused recurring crashes and, in one case,
froze the machine entirely, preventing this larger training run from
finishing.

If anyone wants to contribute by finishing this training run (or testing with
more stable hardware / more modern encoders), it would be very welcome — the
pipeline and data are already in place, it just needs to be run to completion.
