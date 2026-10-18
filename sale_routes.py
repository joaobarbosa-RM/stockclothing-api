from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import pegar_sessao
from schemas import VendaSchema, ResponseVendaSchema
from models import Venda, ItemVenda, Produto
from typing import List

sale_router = APIRouter(prefix="/vendas", tags=["vendas"])


@sale_router.post("/", status_code=201)
async def criar_venda(venda_schema: VendaSchema, session: Session = Depends(pegar_sessao)):
    """
    Registra uma venda e tira as peças vendidas do estoque.
    Se faltar estoque em algum item, a venda inteira é cancelada.
    """
    venda = Venda()
    session.add(venda)
    session.flush()                     # flush: gera o id da venda sem salvar de vez

    for item in venda_schema.itens:
        # with_for_update: trava o produto enquanto a venda acontece, pra duas vendas não pegarem a mesma peça
        produto = session.query(Produto).filter(Produto.id == item.produto).with_for_update().first()
        if not produto:
            session.rollback()          # rollback: desfaz tudo que foi feito nessa venda
            raise HTTPException(status_code=404, detail=f"Produto {item.produto} não encontrado")
        if produto.quantidade_estoque < item.quantidade:
            session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para {produto.nome}, só tem {produto.quantidade_estoque}"
            )
        produto.quantidade_estoque -= item.quantidade                   # tira do estoque
        item_venda = ItemVenda(
            quantidade=item.quantidade,
            preco_unitario=produto.preco,
            venda=venda.id,
            produto=produto.id
        )
        session.add(item_venda)

    session.flush()
    venda.calcular_valor_total()
    session.commit()
    return {
        "mensagem": "Venda registrada com sucesso",
        "venda_id": venda.id,
        "valor_total": venda.valor_total
    }


@sale_router.get("/", response_model=List[ResponseVendaSchema])
async def listar_vendas(session: Session = Depends(pegar_sessao)):
    """
    Lista as vendas, da mais nova para a mais antiga.
    """
    return session.query(Venda).order_by(Venda.id.desc()).all()


@sale_router.get("/{id_venda}", response_model=ResponseVendaSchema)
async def visualizar_venda(id_venda: int, session: Session = Depends(pegar_sessao)):
    """
    Mostra uma venda com os itens dela.
    """
    venda = session.query(Venda).filter(Venda.id == id_venda).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return venda
