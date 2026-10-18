import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship      # relationship = para conectar as tabelas

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")                       # a url do banco fica no .env
if not DATABASE_URL:
    raise RuntimeError("Falta a DATABASE_URL no arquivo .env")

# cria a conexão com o banco de dados
db = create_engine(DATABASE_URL)

# "Base" faz a tradução das classes para tabelas
Base = declarative_base()


class Produto(Base):
    __tablename__ = "produtos"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    preco = Column("preco", Float, nullable=False)
    tamanho = Column("tamanho", String)
    cor = Column("cor", String)
    quantidade_estoque = Column("quantidade_estoque", Integer, default=0)

    def __init__(self, nome, preco, tamanho, cor, quantidade_estoque=0):
        self.nome = nome
        self.preco = preco
        self.tamanho = tamanho
        self.cor = cor
        self.quantidade_estoque = quantidade_estoque


class Venda(Base):
    __tablename__ = "vendas"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    valor_total = Column("valor_total", Float, default=0)
    criado_em = Column("criado_em", DateTime, default=datetime.now)
    itens = relationship("ItemVenda", cascade="all, delete")                    # cascade: se deletar a venda, deleta os itens junto

    def __init__(self, valor_total=0):
        self.valor_total = valor_total

    def calcular_valor_total(self):
        # soma (preço x quantidade) de todos os itens da venda
        self.valor_total = sum(item.preco_unitario * item.quantidade for item in self.itens)


class ItemVenda(Base):
    __tablename__ = "itens_venda"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    quantidade = Column("quantidade", Integer)
    preco_unitario = Column("preco_unitario", Float)                            # guarda o preço da hora da venda, se o produto mudar de preço depois não afeta
    venda = Column("venda", Integer, ForeignKey("vendas.id"))
    produto = Column("produto", Integer, ForeignKey("produtos.id"))

    def __init__(self, quantidade, preco_unitario, venda, produto):
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.venda = venda
        self.produto = produto
