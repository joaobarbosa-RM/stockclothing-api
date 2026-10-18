from pydantic import BaseModel, ConfigDict, Field
from typing import List
from datetime import datetime


class ProdutoSchema(BaseModel):
    nome: str
    preco: float = Field(gt=0)                              # gt=0: tem que ser maior que zero
    tamanho: str
    cor: str
    quantidade_estoque: int = Field(default=0, ge=0)        # ge=0: não aceita estoque negativo

    model_config = ConfigDict(from_attributes=True)


class ReporEstoqueSchema(BaseModel):
    quantidade: int = Field(gt=0)

    model_config = ConfigDict(from_attributes=True)


class ResponseProdutoSchema(BaseModel):
    id: int
    nome: str
    preco: float
    tamanho: str
    cor: str
    quantidade_estoque: int

    model_config = ConfigDict(from_attributes=True)


class ItemVendaSchema(BaseModel):
    produto: int                                            # id do produto
    quantidade: int = Field(gt=0)

    model_config = ConfigDict(from_attributes=True)


class VendaSchema(BaseModel):
    itens: List[ItemVendaSchema] = Field(min_length=1)      # não deixa criar venda vazia

    model_config = ConfigDict(from_attributes=True)


class ResponseItemVendaSchema(BaseModel):
    id: int
    produto: int
    quantidade: int
    preco_unitario: float

    model_config = ConfigDict(from_attributes=True)


class ResponseVendaSchema(BaseModel):
    id: int
    valor_total: float
    criado_em: datetime
    itens: List[ResponseItemVendaSchema]

    model_config = ConfigDict(from_attributes=True)
