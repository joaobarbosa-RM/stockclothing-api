# StockClothing API

API que fiz pra controlar estoque e vendas de uma loja de roupas. Cadastro os produtos, registro as vendas e o estoque diminui sozinho a cada venda.

## O que tem

- Cadastrar, editar, pesquisar e deletar produtos
- Repor estoque e ver quais produtos estão acabando
- Registrar vendas com vários itens, com o total calculado automaticamente
- Se faltar estoque em algum item, a venda inteira é cancelada

## Feito com

Python, FastAPI, SQLAlchemy e PostgreSQL

## Como rodar

1. Crie um banco vazio no PostgreSQL
2. Rode o arquivo `banco/criar_tabelas.sql` nesse banco (pelo pgAdmin ou psql) pra criar as tabelas
3. Crie o ambiente virtual e instale as dependências:
```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
```
4. Copie o `.env.example` para `.env` e troque pelos dados do seu banco:
```
   DATABASE_URL=postgresql+psycopg2://postgres:SUA_SENHA@localhost:5432/NOME_DO_BANCO
```
5. Rode com `uvicorn main:app --reload`

As rotas ficam em http://127.0.0.1:8000/docs

## Testes

```
pytest -v
```

Os testes usam um banco na memória, então não mexem no seu PostgreSQL.