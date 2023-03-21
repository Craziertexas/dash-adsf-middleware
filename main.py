import dash
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from flask import Flask, session, redirect, render_template_string, url_for

server = Flask(__name__)

app = dash.Dash(__name__, server=server, url_base_pathname='/dummypath/')
app.layout = dbc.Container([
    dbc.Row(
        [
            html.H1("Welcome to my app!", style = {'textAlign':'center','marginTop':40,'marginBottom':40}),
            html.P("This is an example of a Dash app ", style = {'textAlign':'center'}),
        ]
    ),
    dbc.Row([
            dcc.Dropdown( id = 'dropdown',
            options = [
                {'label':'Google', 'value':'GOOG' },
                {'label': 'Apple', 'value':'AAPL'},
                {'label': 'Amazon', 'value':'AMZN'},
                ],
            value = 'GOOG'),
            dcc.Graph(id = 'bar_plot')
    ])
    ],
    fluid=True
)

from auth import saml_login, auth_required

df = px.data.stocks()
    
@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
def graph_update(dropdown_value):
    print(f'Updating graph for user {session["saml_auth_data"]["data"]["nameid"]}')
    fig = go.Figure([go.Scatter(x = df['date'], y = df['{}'.format(dropdown_value)],\
                     line = dict(color = 'firebrick', width = 4))
                     ])
    
    fig.update_layout(title = 'Stock prices over time',
                      xaxis_title = 'Dates',
                      yaxis_title = 'Prices'
                      )
    return fig  

@server.route("/", methods=['GET'])
@auth_required
def index():
    return app.index()

@server.route("/hello", methods=['GET'])
def hello():
    return "Testing Dash ADSF intergration!"

@server.route("/me", methods=['GET'])
@auth_required
def getMe():
    print(session)
    return f'Your name id is {session["saml_auth_data"]["data"]["nameid"]} !'

@server.route("/login", methods=['GET'])
@saml_login
def login():
    return redirect(url_for("index", external=True))

@server.route('/logout-form', methods=['GET'])
def logout():
    template = '''
    <html>
        <head>
            <title>Logout</title>
        </head>
        <body>
            <form action="{{ url_for('flask_saml2_sp.logout') }}" method="POST">
            <button type="submit">Logout</button>
            </form>
        </body>
    </html>
    '''
    return render_template_string(template)


if __name__ == '__main__': 
    app.run_server(host='0.0.0.0',port=5050, use_reloader=True, use_debugger=True)