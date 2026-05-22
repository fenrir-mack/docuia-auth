from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class UsuarioModel(Base):
    """
    Modelo de banco de dados — representa a tabela 'usuarios'.
    Fica na camada de infraestrutura, separado da entidade de domínio.
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    cargo = Column(String(255), default="")
    criado_em = Column(DateTime, default=datetime.utcnow)
