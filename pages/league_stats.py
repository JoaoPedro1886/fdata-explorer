import pandas as pd
import numpy as np
import streamlit as st
from data import load


def app():
    st.cache()

    def load_data():
        df = load.data()
        return df

    df = load_data()
    selected_league = st.sidebar.selectbox('Select League', df.league.sort_values().unique())
    seasons = df[df['league'] == selected_league].season.sort_values(ascending=False).unique()
    options = ['%s-%s' % (str(x), str(x + 1)) for x in seasons]
    keys = dict(zip(options, seasons))
    selected_season = st.sidebar.selectbox('Select Season', options)
    selected_season = keys[selected_season]

    def dataframe(league='Barclays Premier League', season=2021):
        df = load_data()
        br = df[df['league'] == league]
        br = br[br['season'] == season]
        brhome = pd.DataFrame(br.groupby('team1').xg1.mean())
        brhomeag = pd.DataFrame(br.groupby('team1').xg2.mean())
        braway = pd.DataFrame(br.groupby('team2').xg2.mean())
        brawayag = pd.DataFrame(br.groupby('team2').xg1.mean())
        merge1 = pd.merge(brhome, braway, left_index=True, right_index=True)
        merge2 = pd.merge(brhomeag, brawayag, left_index=True, right_index=True)
        merge1['xG For'] = np.round((merge1.xg1 + merge1.xg2) / 2, decimals=2)
        merge2['xG Against'] = np.round((merge2.xg1 + merge2.xg2) / 2, decimals=2)
        merge = pd.merge(merge1[['xG For']], merge2[['xG Against']], left_index=True, right_index=True)
        merge['xGD'] = merge['xG For'] - merge['xG Against']
        return merge.sort_values(by='xGD', ascending=False)

    table = dataframe(league=selected_league, season=selected_season)
    cols = [c for c in table.columns]
    table = table.reset_index(level=0).rename(columns={'team1': 'Team'})
    table.index = np.arange(1, len(table) + 1)
    st.dataframe(table.style.format(precision=2, subset=cols), width=700, height=768)
