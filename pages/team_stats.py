#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 00:48:50 2021

@author: joaopdrosr
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
import streamlit as st
from datetime import date
from data import load


def app():
    st.cache()

    def load_data():
        data = load.data()
        return data

    df = load_data()

    col1, col2 = st.columns(2)

    selected_team = st.sidebar.selectbox('Enter team', df.team1.sort_values().unique())

    selected_season = st.sidebar.selectbox('Select season', df[df['team1'] == selected_team]
                                           .season.sort_values(ascending=False).unique())

    selected_league = st.sidebar.selectbox('Enter league', df[(df['team1'] == selected_team) &
                                                              (df['season'] == selected_season)]
                                           .league.unique())

    df_range = df[(df['league'] == selected_league) & (df['season'] == selected_season)].reset_index()

    df_range['datetime'] = pd.to_datetime(df_range['date'], format='%Y-%m-%d')

    number = st.sidebar.number_input('Insert a number', min_value=1, step=1)

    metrics = ['shot-xg', 'non-shot-xg']
    metric = st.sidebar.radio('Choose Metric', ('Shot-based xG', 'Non-shot-based xG', 'Goal'))

    today = date.today()

    start_date = pd.to_datetime(df_range['date'].iloc[0])
    end_date = pd.to_datetime(df_range['date'].iloc[-1])

    # st.write('Select period')

    with col1:
        d1 = st.date_input("From:", value=start_date, min_value=start_date, max_value=end_date)
        # st.write(d1)

    with col2:
        d2 = st.date_input("To:", value=end_date, min_value=start_date, max_value=end_date)

    # st.write(d2)

    if metric == 'Shot-based xG':
        # st.write('You selected shot-based xG.')
        selected_metric = 'shot-xg'
    elif metric == 'Non-shot-based xG':
        # st.write('You selected non-shot-based xG.')
        selected_metric = 'non-shot-xg'
    else:
        # st.write('You selected Goal.')
        selected_metric = 'goal'

    def trend(team='Arsenal', competition='Barclays Premier League', season=2021,
              n=10, metric='shot-xg', x_axis='matchweek',
              date1=start_date, date2=end_date):
        df = load_data()

        df = df[(df['league'] == competition) & ((df['team1'] == team) | (df['team2'] == team))]

        if season == 'all':
            options = [x for x in df.season]
            df = df.loc[df['season'].isin(options)]
            title = "%s-game rolling average in %s (2016-2022)" % (n, competition)
        elif type(season) == int:
            df = df[df['season'] == season]
            title = "%s-game rolling average in %s (%d-%d)" % (n, competition, season, season + 1)
        else:
            options = [season]
            df = df.loc[df['season'].isin(options)]
            title = "%s-game rolling average in %s (%d-%d)" % (n, competition, season, season + 1)

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

        if metric == 'non-shot-xg':
            df['xG'] = np.where(df.team1 == team, df.nsxg1, df.nsxg2)
            df['xGA'] = np.where(df.team2 == team, df.nsxg1, df.nsxg2)
            y_label = 'Non-shot xG per Game'
        elif metric == 'shot-xg':
            df['xG'] = np.where(df.team1 == team, df.xg1, df.xg2)
            df['xGA'] = np.where(df.team2 == team, df.xg1, df.xg2)
            y_label = 'Shot based xG per Game'
        elif metric == 'goal':
            df['xG'] = np.where(df.team1 == team, df.score1, df.score2)
            df['xGA'] = np.where(df.team2 == team, df.score1, df.score2)
            y_label = 'Goals Scored per Game'

        df = df.dropna(subset=['xG', 'xGA'], axis=0)

        df['Matchweek'] = df.groupby('season').cumcount() + 1
        df['Matchweek'] = df['Matchweek'].astype(int)

        df = df[(df['date'] >= pd.to_datetime(date1)) & (df['date'] <= pd.to_datetime(date2))]

        if x_axis == 'time':
            index = 'date'
        elif x_axis == 'matchweek':
            index = 'Matchweek'
        else:
            index = 'date'

        df = df[['season', 'date', 'Matchweek', 'xG', 'xGA']].set_index(index)

        mark_on = np.where(np.arange(1, len(df) + 1) >= n, True, False)

        df['xG'] = df.xG.rolling(n, min_periods=1).mean()
        df['xGA'] = df.xGA.rolling(n, min_periods=1).mean()

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.set(title=title,
               ylabel=y_label)
        plt.suptitle("%s's xG for and against trend over time" % team)
        # plt.ylabel('Expected Goals (xG)')
        plt.style.use('fivethirtyeight')
        df.xG.plot(ax=ax, color='darkblue', marker='o', markevery=list(mark_on))
        df.xGA.plot(ax=ax, color='darkred', marker='o', markevery=list(mark_on))
        plt.fill_between(df.index, df['xG'], df['xGA'],
                         where=df['xG'] >= df['xGA'],
                         facecolor='skyblue', alpha=0.2, interpolate=True)
        plt.fill_between(df.index, df['xG'], df['xGA'],
                         where=df['xG'] < df['xGA'],
                         facecolor='lightcoral', alpha=0.2, interpolate=True)
        plt.ylim([0, 4])

        locator = matplotlib.ticker.MultipleLocator(2)
        plt.gca().xaxis.set_major_locator(locator)
        formatter = matplotlib.ticker.StrMethodFormatter("{x:.0f}")
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.legend(loc='best')
        ax.annotate('data: FiveThirtyEight',
                    xy=(0.5, 0), xytext=(340, 10),
                    xycoords=('axes fraction', 'figure fraction'),
                    textcoords='offset points',
                    size=12, ha='right', va='bottom')
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(0.5)
            plt.grid(linestyle='--', linewidth=0.5)
        return fig

    plot_data = trend(team=selected_team, competition=selected_league, season=selected_season, n=number,
                      metric=selected_metric, date1=d1, date2=d2)
    if st.checkbox('Show/Hide'):
        st.pyplot(plot_data)
