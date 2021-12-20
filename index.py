from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import accuweather


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.H6('NavBar ->  ', style={'display':'inline-block'}),
        dcc.Link('Accuweather', href='/apps/accuweather', style={'display':'inline-block'}),
    ], className="row"),
    html.Div(id='page-content', children=[])
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/accuweather':
        return accuweather.layout
    # if pathname == '/apps/global_sales':
    #     return global_sales.layout
    else:
        return 'Choose a page above :) ||| Credits: Domenico Castronovo' #accuweather.layout


if __name__ == '__main__':
    app.run_server(debug=False)
