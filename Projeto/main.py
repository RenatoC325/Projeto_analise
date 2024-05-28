import dash
import dash_bootstrap_components as dbc 
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dependencies import Input, Output
from dash import html, dcc, Input, Output

# configurando cores para os temas
dark_theme ='darkly'
vapor_theme ='vapor'
url_dark_theme=dbc.themes.DARKLY
url_vapor_theme=dbc.themes.VAPOR


# ------------dados--------------#
# importado dados
df=pd.read_csv('src/data/dataset_comp.csv')
df['dt_Venda']=pd.to_datetime(df['dt_Venda'])
df['Mes']=df['dt_Venda'].dt.strftime('%b').str.upper()

# -------------------------------#

# --------------lista------------#
lista_clientes=[]
for cliente in df['Cliente'].unique():
    lista_clientes.append({
        'label': cliente.upper(), 
        'value': cliente
        })
lista_clientes.append({
    'label':'Todos',
    'value':"Todos_Clientes"
    })

meses_br= dict(
    JAB = 'JAN',
    FEB = 'FEV',
    MAR = 'MAR',
    APR = 'ABR',
    MAY = 'MAI',
    JUN = 'JUN',
    JUL = 'JUL',
    AUG = 'AGO',
    SEP = 'SET',
    OCT = 'OUT',
    NOV = 'NOV',
    DEC = 'DEZ'
)

lista_meses=[]
for mes in df['Mes'].unique():
    mes_pt=meses_br.get(mes,mes)
    lista_meses.append({
        'label':mes_pt,
        'value':mes
    })
lista_meses.append({
    'label': "ANO COMPLETO",
    'value':"ano_completo"
})

lista_categoria=[]
for categoria in df['Categorias'].unique():
    lista_categoria.append({
        'label': categoria.upper(), 
        'value': categoria
    })
lista_categoria.append({"label":'TODAS AS CATEGORIAS', 'valeu':"todas_categorias"})
    
   

# -------------------------------

# CRIANDO APP #
app=dash.Dash(__name__)


# ------------LAYOUT-------------#
layout_titulo= html.Div([
    html.Div(
        dcc.Dropdown(
            id='dropdown_clientes',
            options=lista_clientes,
            placeholder=lista_clientes[-1]["label"],
            style={
                "background-color":"transparent",
                'border' : 'name',
                'font-family':'fraktur bold',
                'color' : "black"
            }
        ),style={'width':'25%'}
    ),
    html.Div(
        html.Legend(
            "Ebony Store",
            style={
                'textAlign':"rigth",'font-size' :'150%'
            }
        ), style={'width':'50%'}),
        html.Div(
            ThemeSwitchAIO(
                aio_id='theme',
                themes=[
                    url_vapor_theme,
                    url_dark_theme
                ]
            ),style={'width':"25%"}
        )], style={
        'text-align':'center',
        'display':'flex',
        'justify-content':'space-around',
        'align-items':'center',
        'font-family':"fira code",
        'margin-top':'20px'
    })

layout_linha1= html.Div([
    html.Div([
        html.H4(id='output_cliente'),
        dcc.Graph(id='visual01'),
    ],
    style={'width':'55%'
 }),

    html.Div([
        dbc.Checklist(
            id='Radio_mes',
            options=lista_meses,
            inline=True

        ),
        dbc.RadioItems(
        id="lista_categoria",
        options=lista_categoria,
        inline=True
        )

            
    ],style={
        'width':"30%",
        'display':'flex',
        'flex-direction':"column",
        'justify-content':'space-evenly'
    })
    ], style={
     
    'display':'flex',
    'justify-content':'space-around',
    'margin-top':'25px',
    'height':"300px"
    })



#-----------carregando layout---------------#
app.layout=html.Div([
    layout_titulo,
    layout_linha1
 ])

# ------------funçoes de apoio----------#
def filtro_cliente(cliente_selecionado):
    if cliente_selecionado is None:
        return pd.Series(True, index=df.index)

    return df['Cliente']== cliente_selecionado

def filtro_categoria(categoria_selecionada):
    if categoria_selecionada is None:
        return pd.Series (True, index=df.index)
    elif categoria_selecionada == 'todas_categorias':
        return pd.Series (True, index=df.index)
    return df["Categorias"] == categoria_selecionada

def filtro_mes(mes_selecionado):
    if mes_selecionado is None:
        return pd.Series (True, index=df.index)
    elif mes_selecionado == 'ano_completo':
        return pd.Series (True, index=df.index)
    else:
        if len(mes_selecionado) == 0:
            return pd.Series (True, index=df.index)
        elif len(mes_selecionado)==1:    
            for mes in mes_selecionado:
                 return df["Mes"]==mes
        else:
            re




# --------------CALLBACKS----------------- #

@app.callback(
    Output('output_cliente',"children"),
    [
    Input('dropdown_clientes',"value"),
    Input("lista_categoria",'value')
    ]
 )
def atualizar_texto(cliente_selecionado,categoria_selecionada):
    if cliente_selecionado and categoria_selecionada:
        return f'TOP 5 Produtos da Categoria:{categoria_selecionada} | Cliente:{cliente_selecionado}'
    elif cliente_selecionado:
        return f'TOP5 PRODUTOS | Clientes:{cliente_selecionado}'

    elif categoria_selecionada:
        return f'TOP5 {categoria_selecionada}'

    else :
        return f'TOP5 Categorias'

@app.callback(
    Output('visual01','figure'),
    [ 
        Input('dropdown_clientes',"value"),
        Input('Radio_mes','value'),
        Input('lista_categoria','value'),
        Input(ThemeSwitchAIO.ids.switch("theme"),"value")
    ]
 )

def visual01(cliente, mes, categoria, toggle):
    template= vapor_theme if toggle else dark_theme

    nome_cliente=filtro_cliente(cliente)
    nome_categoria=filtro_categoria(categoria)
    nome_mes=filtro_mes(mes)

    cliente_mes_categoria =nome_cliente & nome_categoria & nome_mes
    df_filtrado=df.loc[cliente_mes_categoria]

    df_grupo= df_filtrado.groupby (['Produto','Categorias'])['Total Vendas'].sum().reset_index()
    df_top5 = df_grupo.sort_values(by='Total Vendas',ascending=False).head(5)
    
# --------------Criando Grafico--------------

    fig=px.bar(
        df_top5,
        x="Produto",
        y="Total Vendas",
        color='Total Vendas',
        text="Total Vendas",
        color_continuous_scale="blues",
        height=280,
        template=template

    )
    fig.update_traces(texttemplate="%{text:.2s}",textposition='outside')
    fig.update_layout(
        margin=dict(t=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False, range=[
            df_top5['Total Vendas'].min() * 0,
            df_top5['Total Vendas'].max() * 1.5
        ]),
        xaxis_title=None,
        yaxis_title=None,
        xaxis_tickangle=-15,
        font=dict(size=15),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig
    
  

























# subindo servido
if __name__ == '__main__':
    app.run_server(debug=True)
