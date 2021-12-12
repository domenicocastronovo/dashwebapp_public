from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import accuweather#, global_sales


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Accuweather', href='/apps/accuweather'),
        # dcc.Link('Other Products', href='/apps/global_sales'),
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
        return 'Choose a page above :)' #accuweather.layout


if __name__ == '__main__':
    app.run_server(debug=False)
