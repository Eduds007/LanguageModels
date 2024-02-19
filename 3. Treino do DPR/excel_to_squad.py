import json
import pandas as pd

filename = '../../2. Seleção de modelos e dados/Modelo Opus/nq-traduzido-opus-5k.xlsx'

squad = {
    "version": "0.1",
    "data": [
        
    ],
}

traduzido = pd.read_excel(filename)
for passage in json.loads(traduzido.to_json(orient='records')):
    estrutura = {
        "title": passage['title'],
        "paragraphs": [
            {
            "context": passage['long_answer'],
            "qas": [
                {
                    "id":0,
                    "question": passage['question'],
                    "answers": [
                        {
                        "answer_start":0,
                        'text':passage['short_answer'],
                        }
                        
                    ],
                },
            ],
            },
        ],
    }
    squad['data'].append(estrutura)

json_data =squad
file_path = "data.json"
with open(file_path, "w") as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"Variable saved as JSON")