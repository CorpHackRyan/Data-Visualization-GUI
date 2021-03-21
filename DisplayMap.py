import plotly.graph_objects as go
import pandas as pd
import random

# Make sure to allow whatever map we are displaying to be passed in, so we can update the headlines properly;

# color_bar_title = (variable passed in gui)
# title = (variable passed in gui)


def display_map(compare_total_jobs_total_data):

    df = pd.read_csv("display_map_data.csv")
    color = ["Greens", "Reds", "Blues"]

    fig = go.Figure(data=go.Choropleth(
        locations=df['state'],  # Spatial coordinates
        z=df['data'].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale=random.choice(color),
        colorbar_title="Jobs avail per graduate",
    ))

    fig.update_layout(title_text="2018 - Ratio of jobs available per graduating student", geo_scope="usa",)

    fig.show()
