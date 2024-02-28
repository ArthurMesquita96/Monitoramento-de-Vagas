import re

import numpy as np
import pandas as pd


def get_senioridade(title_job):
    if isinstance(title_job, str):  # Verifica se é uma string
        mapa_senioridade = {
            'Sênior': ['Sênior', 'Senior', 'Sr'],
            'Pleno': ['Pleno', 'Pl', 'Jr/Pl'],
            'Júnior': ['Júnior', 'Jr']
        }

        for senioridade, termos in mapa_senioridade.items():
            for termo in termos:
                if termo.lower() in title_job.lower():
                    return senioridade

    return ''


def get_benefits_list(description):
    try:
        # Seu código para obter a lista de benefícios...
        pass
    except:
        return None


if __name__ == '__main__':
    df = pd.read_csv(
        'data/data_raw/vagas_glassdoor_raw.csv')

    # Aplica a função get_senioridade à coluna 'senioridade'
    df['senioridade'] = df['titulo_da_vaga'].apply(get_senioridade)

    print(df['senioridade'].value_counts())
    print(df[df['senioridade'] == 'Júnior']['titulo_da_vaga'])
