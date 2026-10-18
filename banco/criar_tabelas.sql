-- Cria as 3 tabelas do projeto.
-- Se as tabelas já existirem, apague antes (a ordem importa por causa das chaves estrangeiras):
-- DROP TABLE IF EXISTS itens_venda, vendas, produtos;

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR NOT NULL,
    preco DOUBLE PRECISION NOT NULL,
    tamanho VARCHAR,
    cor VARCHAR,
    quantidade_estoque INTEGER DEFAULT 0
);

CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    valor_total DOUBLE PRECISION DEFAULT 0,
    criado_em TIMESTAMP DEFAULT NOW()
);

-- precisa vir por último porque aponta para vendas e produtos
CREATE TABLE itens_venda (
    id SERIAL PRIMARY KEY,
    quantidade INTEGER,
    preco_unitario DOUBLE PRECISION,
    venda INTEGER REFERENCES vendas(id),
    produto INTEGER REFERENCES produtos(id)
);
