def test_criar_venda(client, criar_produto):
    criar_produto(nome="Camisa", preco=50.0, quantidade_estoque=10)
    criar_produto(nome="Calça", preco=120.0, quantidade_estoque=5)

    venda = {"itens": [{"produto": 1, "quantidade": 2}, {"produto": 2, "quantidade": 1}]}
    resposta = client.post("/vendas/", json=venda)

    assert resposta.status_code == 201
    assert resposta.json()["valor_total"] == 220.0           # (2 x 50) + (1 x 120)

    # o estoque tem que ter diminuído
    assert client.get("/produtos/1").json()["quantidade_estoque"] == 8
    assert client.get("/produtos/2").json()["quantidade_estoque"] == 4


def test_venda_sem_estoque_suficiente(client, criar_produto):
    criar_produto(quantidade_estoque=3)
    resposta = client.post("/vendas/", json={"itens": [{"produto": 1, "quantidade": 5}]})
    assert resposta.status_code == 400
    # nada foi vendido, o estoque continua igual
    assert client.get("/produtos/1").json()["quantidade_estoque"] == 3
    assert client.get("/vendas/").json() == []


def test_se_um_item_falhar_a_venda_toda_cancela(client, criar_produto):
    criar_produto(nome="Camisa", quantidade_estoque=10)
    criar_produto(nome="Calça", quantidade_estoque=1)
    venda = {"itens": [{"produto": 1, "quantidade": 2}, {"produto": 2, "quantidade": 5}]}
    resposta = client.post("/vendas/", json=venda)
    assert resposta.status_code == 400
    # o primeiro item não pode ter tirado do estoque
    assert client.get("/produtos/1").json()["quantidade_estoque"] == 10


def test_venda_com_produto_que_nao_existe(client):
    resposta = client.post("/vendas/", json={"itens": [{"produto": 999, "quantidade": 1}]})
    assert resposta.status_code == 404


def test_venda_sem_itens(client):
    resposta = client.post("/vendas/", json={"itens": []})
    assert resposta.status_code == 422


def test_mesmo_produto_duas_vezes_na_venda(client, criar_produto):
    criar_produto(quantidade_estoque=5)
    venda = {"itens": [{"produto": 1, "quantidade": 3}, {"produto": 1, "quantidade": 3}]}
    resposta = client.post("/vendas/", json=venda)
    assert resposta.status_code == 400
    assert client.get("/produtos/1").json()["quantidade_estoque"] == 5


def test_listar_e_visualizar_vendas(client, criar_produto):
    criar_produto(preco=40.0, quantidade_estoque=10)
    client.post("/vendas/", json={"itens": [{"produto": 1, "quantidade": 2}]})
    client.post("/vendas/", json={"itens": [{"produto": 1, "quantidade": 1}]})

    lista = client.get("/vendas/")
    assert lista.status_code == 200
    assert len(lista.json()) == 2
    assert lista.json()[0]["id"] == 2                         # a mais nova vem primeiro

    detalhe = client.get("/vendas/1")
    assert detalhe.status_code == 200
    assert detalhe.json()["valor_total"] == 80.0
    assert len(detalhe.json()["itens"]) == 1
    assert detalhe.json()["itens"][0]["preco_unitario"] == 40.0


def test_visualizar_venda_que_nao_existe(client):
    assert client.get("/vendas/999").status_code == 404


def test_preco_da_venda_nao_muda_se_o_produto_mudar(client, criar_produto):
    criar_produto(preco=50.0, quantidade_estoque=10)
    client.post("/vendas/", json={"itens": [{"produto": 1, "quantidade": 1}]})
    novos_dados = {"nome": "Camisa Polo", "preco": 99.0, "tamanho": "M", "cor": "Azul", "quantidade_estoque": 9}
    client.put("/produtos/1", json=novos_dados)
    assert client.get("/vendas/1").json()["valor_total"] == 50.0


def test_nao_deleta_produto_que_ja_foi_vendido(client, criar_produto):
    criar_produto(quantidade_estoque=10)
    client.post("/vendas/", json={"itens": [{"produto": 1, "quantidade": 1}]})
    resposta = client.delete("/produtos/1")
    assert resposta.status_code == 400
