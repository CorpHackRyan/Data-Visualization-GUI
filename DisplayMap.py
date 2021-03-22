import plotly.graph_objects as go
import pandas as pd
import random


def display_map(analysis_type):
    color = ["Greens", "Reds", "Blues"]

    if analysis_type == "1":
        color_bar_title = "Jobs avail per graduate"
        title_txt = "2018 - Ratio of jobs available per graduating student"
        display_map_csv_data = "display_map_data.csv"
    else:
        color_bar_title = "3 year grad declining balance"
        title_txt = "3 year grad cohort declining balance % to 25% salary"
        display_map_csv_data = "display_map_data2.csv"

    df = pd.read_csv(display_map_csv_data)

    fig = go.Figure(data=go.Choropleth(
        locations=df['state'],  # Spatial coordinates
        z=df['data'].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale=random.choice(color),
        colorbar_title=color_bar_title,
    ))

    fig.update_layout(title_text=title_txt, geo_scope="usa",)
    fig.show()
