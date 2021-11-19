# reference: towardsdatascience.com/
#            creating-multipage-applications-using-streamlit-efficiently-b58a58134030

import streamlit as st
# Custom imports
from main import MultiPage
from pages import league_stats, team_stats

# Create an instance of the app
app = MultiPage()

# Add all your applications (pages) here
app.add_page("League Stats", league_stats.app)
app.add_page("Team Stats", team_stats.app)

# The main app
app.run()
