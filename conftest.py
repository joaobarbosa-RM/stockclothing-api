import os

# força um banco só pros testes, assim nunca mexe no postgres de verdade
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from models import Base
from dependencies import pegar_sessao


@pytest.fixture()
def client():
    # banco temporário, só na memória
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessaoDeTeste = sessionmaker(bind=engine)

    def sessao_de_teste():
        session = SessaoDeTeste()
        try:
            yield session
        finally:
            session.close()

    # troca a sessão real pela de teste
    app.dependency_overrides[pegar_sessao] = sessao_de_teste

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture()
def criar_produto(client):
    # cadastra um produto e devolve o json dele
    def _criar(nome="Camisa Polo", preco=50.0, tamanho="M", cor="Azul", quantidade_estoque=10):
        dados = {"nome": nome, "preco": preco, "tamanho": tamanho,
                 "cor": cor, "quantidade_estoque": quantidade_estoque}
        return client.post("/produtos/", json=dados).json()
    return _criar
