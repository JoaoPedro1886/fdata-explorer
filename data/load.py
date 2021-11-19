import pandas as pd
import streamlit as st


@st.cache()
def data():
    dtype_list = {'season': 'int32',
                  'date': 'O',
                  'league': 'O',
                  'team1': 'O',
                  'team2': 'O',
                  'score1': 'float32',
                  'score2': 'float32',
                  'xg1': 'float32',
                  'xg2': 'float32',
                  'nsxg1': 'float32',
                  'nsxg2': 'float32'}

    cols = ['season', 'date', 'league', 'team1', 'team2', 'score1', 'score2', 'xg1', 'xg2', 'nsxg1',
            'nsxg2']

    df = pd.read_csv('https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv', dtype=dtype_list)[cols]
    df['timestamp'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.dropna(subset=['xg1', 'xg2', 'nsxg1', 'nsxg2'])
    return df
