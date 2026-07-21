# Dashboard de E-commerce

Aplicação web interativa construída com **Dash** e **Plotly** para análise exploratória de um dataset de produtos de e-commerce. O painel transforma dados brutos de preço, avaliações e categorias em sete visualizações que respondem em tempo real a filtros escolhidos pelo usuário.

## Sobre o projeto

O dataset (`ecommerce_estatistica.csv`) reúne informações de produtos de vestuário: preço, nota média, número de avaliações, marca, material, gênero, temporada e faixa de unidades vendidas. A aplicação permite filtrar por gênero e por faixa de preço, e todos os gráficos se atualizam automaticamente via callback.

## Visualizações

| # | Gráfico | O que mostra |
|---|---------|--------------|
| 1 | Histograma | Distribuição de preços |
| 2 | Pizza | Participação de produtos por gênero |
| 3 | Dispersão (bolhas) | Preço x nota, com tamanho por número de avaliações |
| 4 | Linha | Nota média por faixa de unidades vendidas |
| 5 | Dispersão 3D | Preço x nota x número de avaliações |
| 6 | Barras agrupadas | Preço médio por material e gênero |
| 7 | Mapa de calor | Correlação entre as variáveis numéricas |

## Tecnologias

- Python
- Dash
- Plotly Express
- pandas

## Como executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/tassiolirgon/dash_ecommerce_estatistica.git
   cd dash_ecommerce_estatistica
   ```

2. Instale as dependências:
   ```bash
   pip install dash plotly pandas
   ```

3. Rode a aplicação:
   ```bash
   python app_ecommerce.py
   ```

4. Abra o navegador em `http://localhost:8050`.

> O arquivo `app_ecommerce.py` espera o `ecommerce_estatistica.csv` na mesma pasta. Ajuste a variável `CAMINHO_CSV` se o arquivo estiver em outro local.

## Estrutura

```
.
├── app_ecommerce.py            # Aplicação Dash e definição dos gráficos
├── ecommerce_estatistica.csv   # Base de dados
└── README.md
```

## Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
