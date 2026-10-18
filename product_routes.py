from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import ProdutoSchema, ReporEstoqueSchema, ResponseProdutoSchema
from models import Produto, ItemVenda
from typing import List, Optional

product_router = APIRouter(prefix="/produtos", tags=["produtos"])


@product_router.get("/", response_model=List[ResponseProdutoSchema])
async def listar_produtos(nome: Optional[str] = None, session: Session = Depends(pegar_sessao)):
    """
    Lista os produtos. Se mandar o nome, pesquisa por ele.
    """
    query = session.query(Produto)
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))           # ilike: ignora maiúscula e minúscula
    return query.order_by(Produto.id).all()


# precisa ficar antes da rota "/{id_produto}", senão o fastapi acha que "estoque-baixo" é um id
@product_router.get("/estoque-baixo", response_model=List[ResponseProdutoSchema])
async def listar_estoque_baixo(limite: int = 5, session: Session = Depends(pegar_sessao)):
    """
    Lista os produtos com estoque baixo (até 5 peças, a não ser que mande outro limite).
    """
    produtos = session.query(Produto).filter(Produto.quantidade_estoque <= limite) \
        .order_by(Produto.quantidade_estoque).all()
    return produtos


@product_router.get("/{id_produto}", response_model=ResponseProdutoSchema)
async def visualizar_produto(id_produto: int, session: Session = Depends(pegar_sessao)):
    """
    Mostra um produto pelo id.
    """
    produto = session.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@product_router.post("/", response_model=ResponseProdutoSchema, status_code=201)
async def criar_produto(produto_schema: ProdutoSchema, session: Session = Depends(pegar_sessao)):
    """
    Cadastra um produto novo.
    """
    novo_produto = Produto(
        nome=produto_schema.nome,
        preco=produto_schema.preco,
        tamanho=produto_schema.tamanho,
        cor=produto_schema.cor,
        quantidade_estoque=produto_schema.quantidade_estoque
    )
    session.add(novo_produto)
    session.commit()                            # commit: salva no banco
    session.refresh(novo_produto)               # refresh: pega o id que o banco criou
    return novo_produto


@product_router.put("/{id_produto}", response_model=ResponseProdutoSchema)
async def atualizar_produto(id_produto: int, produto_schema: ProdutoSchema, session: Session = Depends(pegar_sessao)):
    """
    Atualiza os dados de um produto.
    """
    produto = session.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.nome = produto_schema.nome
    produto.preco = produto_schema.preco
    produto.tamanho = produto_schema.tamanho
    produto.cor = produto_schema.cor
    produto.quantidade_estoque = produto_schema.quantidade_estoque
    session.commit()
    session.refresh(produto)
    return produto


@product_router.post("/{id_produto}/repor-estoque", response_model=ResponseProdutoSchema)
async def repor_estoque(id_produto: int, estoque_schema: ReporEstoqueSchema, session: Session = Depends(pegar_sessao)):
    """
    Soma peças no estoque, para quando chegar mercadoria nova.
    """
    produto = session.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    produto.quantidade_estoque += estoque_schema.quantidade
    session.commit()
    session.refresh(produto)
    return produto


@product_router.delete("/{id_produto}")
async def deletar_produto(id_produto: int, session: Session = Depends(pegar_sessao)):
    """
    Deleta um produto. Se ele já foi vendido não deixa deletar.
    """
    produto = session.query(Produto).filter(Produto.id == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    ja_vendido = session.query(ItemVenda).filter(ItemVenda.produto == id_produto).first()
    if ja_vendido:
        raise HTTPException(status_code=400, detail="Esse produto já foi vendido, não dá pra deletar")
    session.delete(produto)
    session.commit()
    return {"mensagem": f"Produto número: {id_produto} deletado com sucesso"}
