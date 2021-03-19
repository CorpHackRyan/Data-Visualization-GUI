import plotly.graph_objects as go
import pandas as pd



def display_map(total_jobs, total_grads):
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')

    fig = go.Figure(data=go.Choropleth(
        locations=df['code'],  # Spatial coordinates
        # z = df['total exports'].astype(float), # Data to be color-coded
        z=total_grads.astype(float),  # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Millions USD",
    ))

    fig.update_layout(title_text="2018 - Ratio of jobs available per graduating student", geo_scope="usa",)

    fig.show()
    # fig = px.choropleth(locations=["NV", "TX", "NY"], locationmode="USA-states", color=[1, 2, 8], scope="usa")
    # fig = px.choropleth(locations=total_jobs, locationmode="USA-states", color_continuous_scale=30, scope="usa")
    # fig.show()


