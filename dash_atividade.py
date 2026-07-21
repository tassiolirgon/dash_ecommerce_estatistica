# ==================================================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ==================================================
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd


# ==================================================
# CARREGAMENTO E PREPARO DOS DADOS
# ==================================================
CAMINHO_CSV = 'ecommerce_estatistica.csv'


def carrega_dados(caminho=CAMINHO_CSV):
    df = pd.read_csv(caminho)

    # Remove a coluna de índice residual, se existir
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    # Ordem lógica das faixas de vendidos (usa o código numérico como chave)
    ordem_faixas = (
        df[['Qtd_Vendidos', 'Qtd_Vendidos_Cod']]
        .drop_duplicates()
        .sort_values('Qtd_Vendidos_Cod')['Qtd_Vendidos']
        .tolist()
    )
    df['Qtd_Vendidos'] = pd.Categorical(
        df['Qtd_Vendidos'], categories=ordem_faixas, ordered=True
    )

    return df


df = carrega_dados()

# Opções fixas para os filtros
lista_generos = sorted(df['Gênero'].dropna().unique())
faixa_preco = (float(df['Preço'].min()), float(df['Preço'].max()))

# Materiais mais frequentes (o gráfico de barras fica ilegível com os 51)
TOP_MATERIAIS = df['Material'].value_counts().head(6).index.tolist()

# Colunas numéricas usadas no mapa de calor
COLS_NUM = ['Nota', 'N_Avaliações', 'Desconto', 'Preço']


# ==================================================
# FUNÇÃO QUE CRIA OS GRÁFICOS A PARTIR DO RECORTE
# ==================================================
def cria_graficos(generos_selecionados, preco_min, preco_max):

    # Recorte aplicado a todos os gráficos
    dff = df[
        df['Gênero'].isin(generos_selecionados)
        & df['Preço'].between(preco_min, preco_max)
    ]

    # Proteção contra seleção vazia (evita gráficos quebrados)
    if dff.empty:
        vazio = px.scatter(title='Nenhum dado para os filtros selecionados')
        return (vazio,) * 7

    # ---- 1. HISTOGRAMA: distribuição de preços ----
    fig1 = px.histogram(
        dff, x='Preço', nbins=30, color='Gênero',
        title='Distribuição de Preços',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig1.update_layout(xaxis_title='Preço (R$)', yaxis_title='Frequência')

    # ---- 2. PIZZA: participação por gênero ----
    fig2 = px.pie(
        dff, names='Gênero', hole=0.35,
        title='Participação de Produtos por Gênero',
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    # ---- 3. BOLHA: preço x nota, tamanho por nº de avaliações ----
    fig3 = px.scatter(
        dff, x='Preço', y='Nota',
        size='N_Avaliações', color='Gênero',
        hover_name='Marca', size_max=55, opacity=0.7,
        title='Preço x Nota (tamanho = nº de avaliações)'
    )
    fig3.update_layout(xaxis_title='Preço (R$)', yaxis_title='Nota')

    # ---- 4. LINHA: nota média por faixa de vendidos ----
    linha_df = (
        dff.groupby(['Qtd_Vendidos', 'Gênero'], observed=True)['Nota']
        .mean().reset_index()
    )
    fig4 = px.line(
        linha_df, x='Qtd_Vendidos', y='Nota', color='Gênero', markers=True,
        title='Nota Média por Faixa de Unidades Vendidas'
    )
    fig4.update_layout(xaxis_title='Faixa de vendidos', yaxis_title='Nota média')

    # ---- 5. DISPERSÃO 3D: preço, nota e avaliações ----
    fig5 = px.scatter_3d(
        dff, x='Preço', y='Nota', z='N_Avaliações', color='Gênero',
        title='Preço x Nota x Nº de Avaliações'
    )
    fig5.update_layout(scene=dict(
        xaxis_title='Preço', yaxis_title='Nota', zaxis_title='Avaliações'
    ))

    # ---- 6. BARRA: preço médio por material x gênero ----
    barra_df = (
        dff[dff['Material'].isin(TOP_MATERIAIS)]
        .groupby(['Material', 'Gênero'], observed=True)['Preço']
        .mean().reset_index()
    )
    fig6 = px.bar(
        barra_df, x='Material', y='Preço', color='Gênero',
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Bold,
        title='Preço Médio por Material e Gênero'
    )
    fig6.update_layout(
        xaxis_title='Material', yaxis_title='Preço médio (R$)',
        plot_bgcolor='rgba(222, 255, 253, 1)',
        paper_bgcolor='rgba(186, 245, 241, 1)'
    )

    # ---- 7. MAPA DE CALOR: correlação entre variáveis numéricas ----
    corr = dff[COLS_NUM].corr().round(2)
    fig7 = px.imshow(
        corr, text_auto=True, color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1, aspect='auto',
        title='Correlação entre Variáveis Numéricas'
    )

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7


# ==================================================
# CRIAÇÃO DA APLICAÇÃO
# ==================================================
def cria_app():
    app = Dash(__name__)

    app.layout = html.Div(
        style={'fontFamily': 'Arial, sans-serif', 'maxWidth': '1100px',
               'margin': '0 auto', 'padding': '20px'},
        children=[
            html.H1('Dashboard de E-commerce'),
            html.Div('Análise interativa de preços, notas e avaliações.'),
            html.Hr(),

            # ---- Filtros ----
            html.H3('Filtros'),
            html.Label('Gênero:'),
            dcc.Checklist(
                id='filtro_genero',
                options=[{'label': g, 'value': g} for g in lista_generos],
                value=lista_generos,               # todos marcados no início
                inline=True,
                inputStyle={'marginRight': '5px', 'marginLeft': '15px'}
            ),
            html.Br(),
            html.Label('Faixa de preço (R$):'),
            dcc.RangeSlider(
                id='filtro_preco',
                min=faixa_preco[0], max=faixa_preco[1],
                value=[faixa_preco[0], faixa_preco[1]],
                tooltip={'placement': 'bottom', 'always_visible': True}
            ),
            html.Hr(),

            # ---- Gráficos ----
            dcc.Graph(id='g_histograma'),
            dcc.Graph(id='g_pizza'),
            dcc.Graph(id='g_bolha'),
            dcc.Graph(id='g_linha'),
            dcc.Graph(id='g_3d'),
            dcc.Graph(id='g_barra'),
            dcc.Graph(id='g_heatmap'),
        ]
    )

    # ---- Callback: atualiza tudo quando um filtro muda ----
    @app.callback(
        [Output('g_histograma', 'figure'),
         Output('g_pizza', 'figure'),
         Output('g_bolha', 'figure'),
         Output('g_linha', 'figure'),
         Output('g_3d', 'figure'),
         Output('g_barra', 'figure'),
         Output('g_heatmap', 'figure')],
        [Input('filtro_genero', 'value'),
         Input('filtro_preco', 'value')]
    )
    def atualiza(generos, faixa):
        # Se o usuário desmarcar tudo, mostra a base inteira
        if not generos:
            generos = lista_generos
        return cria_graficos(generos, faixa[0], faixa[1])

    return app


# ==================================================
# EXECUÇÃO
# ==================================================
if __name__ == '__main__':
    app = cria_app()
    app.run(debug=True, port=8050)
    