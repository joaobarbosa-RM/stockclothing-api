from models import db
from sqlalchemy.orm import sessionmaker


def pegar_sessao():                              # dependencia: cria uma sessão com o banco pra cada rota usar
    Session = sessionmaker(bind=db)
    session = Session()
    try:
        yield session                            # yield: entrega a sessão mas não encerra a função
    finally:
        session.close()                          # fecha a sessão no final, dando certo ou não
