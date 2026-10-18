def test_criar_produto(client):
    dados = {"nome": "Camisa Polo", "preco": 50.0, "tamanho": "M", "cor": "Azul", "quantidade_estoque": 10}
    resposta = client.post("/produtos/", json=dados)
    assert resposta.status_code == 201
    assert resposta.json()["id"] == 1
    assert resposta.json()["nome"] == "Camisa Polo"


def test_criar_produto_com_preco_negativo(client):
    dados = {"nome": "Camisa", "preco": -5, "tamanho": "M", "cor": "Azul"}
    resposta = client.post("/produtos/", json=dados)
    assert resposta.status_code == 422


def test_listar_produtos(client, criar_produto):
    criar_produto(nome="Camisa Polo")
    criar_produto(nome="Calça Jeans")
    resposta = client.get("/produtos/")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_pesquisar_por_nome(client, criar_produto):
    criar_produto(nome="Camisa Polo")
    criar_produto(nome="Calça Jeans")
    resposta = client.get("/produtos/?nome=camisa")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Camisa Polo"


def test_estoque_baixo(client, criar_produto):
    criar_produto(nome="Camisa", quantidade_estoque=2)
    criar_produto(nome="Calça", quantidade_estoque=50)
    resposta = client.get("/produtos/estoque-baixo")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["nome"] == "Camisa"


def test_visualizar_produto(client, criar_produto):
    criar_produto()
    resposta = client.get("/produtos/1")
    assert resposta.status_code == 200
    assert resposta.json()["cor"] == "Azul"


def test_visualizar_produto_que_nao_existe(client):
    resposta = client.get("/produtos/999")
    assert resposta.status_code == 404


def test_atualizar_produto(client, criar_produto):
    criar_produto()
    novos_dados = {"nome": "Camisa Polo", "preco": 65.0, "tamanho": "G", "cor": "Preta", "quantidade_estoque": 8}
    resposta = client.put("/produtos/1", json=novos_dados)
    assert resposta.status_code == 200
    assert resposta.json()["preco"] == 65.0
    assert resposta.json()["cor"] == "Preta"


def test_repor_estoque(client, criar_produto):
    criar_produto(quantidade_estoque=10)
    resposta = client.post("/produtos/1/repor-estoque", json={"quantidade": 5})
    assert resposta.status_code == 200
    assert resposta.json()["quantidade_estoque"] == 15


def test_deletar_produto(client, criar_produto):
    criar_produto()
    resposta = client.delete("/produtos/1")
    assert resposta.status_code == 200
    assert client.get("/produtos/1").status_code == 404
