#translate nq using pipelines


from datasets import load_dataset
from transformers import pipeline
import pandas as pd
import re
import sys
import argparse

'''
Esse código é responsável por traduzir a base de dados natural questions 
para a lingua portuguesa, utilizando o modelo de linguagem produzido pelo
grupo Helsinki NLP
'''


def translate(dataset, pipe, size=10):
    df = pd.DataFrame(columns = ['title', 'question', 'long_answer', 'short_answer'])
    small_set = dataset['train']
    for i in range(size):

        doc = re.sub(r'''<(?:"[^"]*"['"]*|'[^']*'['"]*|[^'">])+>''','',small_set[i]['document_text'])
        init_long = small_set[i]['annotations'][0]['long_answer']['start_token']
        end_long = small_set[i]['annotations'][0]['long_answer']['end_token']
        if len(small_set[i]['annotations'][0]['short_answers']) != 0:
            init_short = small_set[i]['annotations'][0]['short_answers'][0]['start_token']
            end_short = small_set[i]['annotations'][0]['short_answers'][0]['end_token']
        else:
            init_short = 0
            end_short  = 0
        question = small_set[i]['question_text']
        long_answer = " ".join(doc.split(" ")[init_long:end_long])
        short_answer = " ".join(doc.split(" ")[init_short:end_short])
        title = re.findall(r'(?<=<h1>)(.+?)(?=</h1>)', small_set[i]['document_text'], re.IGNORECASE)[0]
        if len(long_answer) > 0:  
            title = pipe('>>por<< ' + title)[0]['translation_text']
            long_answer= pipe('>>por<< ' + long_answer)[0]['translation_text']
            if len(short_answer) != 0:
                short_answer= pipe('>>por<< ' + short_answer)[0]['translation_text']
            question= pipe('>>por<< ' + question)[0]['translation_text']

            
            
        else:
            pass
            
        new_row = {'title': [title], 'question': [question], 'long_answer': [long_answer], 'short_answer': [short_answer]}
        df_aux = pd.DataFrame(new_row)
        df = pd.concat([df, df_aux])

        #configuração do terminal
        sys.stdout.write(f'\rProgress : {((i+1)/size)*100}%')
        sys.stdout.flush()
        
    df = df.loc[df['long_answer'] != '']
    df.reset_index(drop=True, inplace=True)
    return df


def main():

    #parser = argparse.ArgumentParser(description="Code to translate NQ")
    #parser.add_argument('--size', type=int, default=10, help="Quantas passagens vc deseja traduzir")
    #args = parser.parse_args()
    #size= args.size
    size = 1000
    #load natural questions db
    dataset = load_dataset('json', data_files="simplified-nq-train.jsonl")

    #load model
    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-pt")
    df = translate(dataset, pipe, size=size)

    df.to_excel("test.xlsx")

    return True


if __name__ == '__main__':
    main()