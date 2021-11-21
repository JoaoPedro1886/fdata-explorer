import pandas as pd
import numpy as np
import streamlit as st
from data import load
from sklearn.linear_model import LogisticRegression


def app():
    st.cache(allow_output_mutation=True)

    def load_data():
        data = load.data()
        return data

    df = load_data()
    selected_league = st.sidebar.selectbox('Select League', df.league.sort_values().unique())
    seasons = df[df['league'] == selected_league].season.sort_values(ascending=False).unique()
    options = ['%s-%s' % (str(x), str(x + 1)) for x in seasons]
    keys = dict(zip(options, seasons))
    selected_season = st.sidebar.selectbox('Select Season', options)
    selected_season = keys[selected_season]

    df_range = df[(df['league'] == selected_league) & (df['season'] == selected_season)].reset_index()

    start_date = pd.to_datetime(df_range['date'].iloc[0])
    end_date = pd.to_datetime(df_range['date'].iloc[-1])

    # st.write('Select period')

    col1, col2 = st.columns(2)

    with col1:
        d1 = st.date_input("From:", value=start_date, min_value=start_date, max_value=end_date)
        # st.write(d1)

    with col2:
        d2 = st.date_input("To:", value=end_date, min_value=start_date, max_value=end_date)

    def get_proba(X,y):
        model = LogisticRegression()
        model.fit(X,y)
        return model.predict_proba(X)[:,1]

    def create_xptscol():
        df1 = load_data()
        df1['win1'] = np.where(df1.score1 > df1.score2, 1, 0)
        df1['win2'] = np.where(df1.score2 > df1.score1, 1, 0)
        df1['draw'] = np.where(df1.score1 == df1.score2, 1, 0)

        X = df1[['xg1', 'xg2']]
        y1 = df1['win1']
        y2 = df1['win2']
        y3 = df1['draw']
        df1['xP_home'] = 3 * get_proba(X, y1) + get_proba(X, y3)
        df1['xP_away'] = 3 * get_proba(X, y2) + get_proba(X, y3)
        return df1

    def df_filtered(league=selected_league, season=selected_season, date1=d1, date2=d2):
        dftofilter = create_xptscol()
        filt_df = dftofilter[dftofilter['league'] == league]
        filt_df = filt_df[filt_df['season'] == season]
        filt_df = (filt_df[(filt_df['timestamp'] >= pd.to_datetime(date1))
                          & (filt_df['timestamp'] <= pd.to_datetime(date2))])
        return filt_df

    def dataframe(metric='xg'):
        br = df_filtered()
        #br = dftofilter[dftofilter['league'] == league]
        #br = br[br['season'] == season]
        mhome = pd.DataFrame(br.groupby('team1')['team1'].count())
        maway = pd.DataFrame(br.groupby('team2')['team2'].count())
        m_merge = pd.merge(mhome, maway, left_index=True, right_index=True)
        m_merge['M'] = m_merge['team1']+m_merge['team2']
        m_merge = m_merge.drop(['team1', 'team2'], 1)
        brhome = pd.DataFrame(br.groupby('team1')[metric+'1'].mean())
        brhomeag = pd.DataFrame(br.groupby('team1')[metric+'2'].mean())
        braway = pd.DataFrame(br.groupby('team2')[metric+'2'].mean())
        brawayag = pd.DataFrame(br.groupby('team2')[metric+'1'].mean())
        merge1 = pd.merge(brhome, braway, left_index=True, right_index=True)
        merge2 = pd.merge(brhomeag, brawayag, left_index=True, right_index=True)
        if metric == 'xg':
            colname = 'xG'
        else:
            colname = 'G'
        merge1[colname] = np.round((merge1[metric+'1'] + merge1[metric+'2']) / 2, decimals=2)
        merge2[colname+'A'] = np.round((merge2[metric+'1'] + merge2[metric+'2']) / 2, decimals=2)
        merge = pd.merge(merge1[[colname]], merge2[[colname+'A']], left_index=True, right_index=True)
        merge[colname+'D'] = merge[colname] - merge[colname+'A']
        merge = pd.merge(m_merge, merge, left_index=True, right_index=True)
        return merge

    def df_xpts():
        df2 = df_filtered()
        df2home = pd.DataFrame(df2.groupby('team1').xP_home.sum())
        df2away = pd.DataFrame(df2.groupby('team2').xP_away.sum())
        merge = pd.merge(df2home, df2away, left_index=True, right_index=True)
        merge['xPts'] = merge['xP_home'] + merge['xP_away']
        return merge.drop(['xP_home', 'xP_away'], axis=1)

    def merge():
        df_xg = dataframe()
        df_g = dataframe(metric='score')
        df_xp = df_xpts()
        #df_merge = pd.merge(df_xg, df_g, left_index=True, right_index=True)
        df_merge = pd.merge(df_xg, df_xp, left_index=True, right_index=True)
        return df_merge.sort_values(by='xPts', ascending=False)


    table = merge()
    cols = [c for c in table.columns]
    table = table.reset_index(level=0).rename(columns={'team1': 'Team'})
    table.index = np.arange(1, len(table) + 1)
    st.dataframe((table.style
                  .format(precision=2, subset=cols)),
                 width=10000, height=7000)
