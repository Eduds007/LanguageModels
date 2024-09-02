import json
import pandas as pd

filename = './2. Seleção de modelos e dados/Modelo Opus/nq-traduzido-opus-50k.xlsx'

squad = []
    


traduzido = pd.read_excel(filename)
for passage in json.loads(traduzido.to_json(orient='records')):
    estrutura = {
        "title": passage['title'],
        "context": passage['long_answer'],
        "question": passage['question'],
        "answers":passage['short_answer'],
    }

    squad.append(estrutura)

json_data =squad
file_path = "data-50k-hf.json"
with open(file_path, "w") as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"Variable saved as JSON")