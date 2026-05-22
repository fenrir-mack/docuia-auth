from typing import Optional
from sqlalchemy.orm import Session

from domain.entities.usuario import Usuario
from domain.ports.usuario_repository import IUsuarioRepository
from infrastructure.database.models import UsuarioModel


class UsuarioRepositoryImpl(IUsuarioRepository):
    """
    Adaptador de saída — implementação concreta do repositório usando SQLAlchemy.
    Converte entre entidade de domínio (Usuario) e modelo de banco (UsuarioModel).
    """

    def __init__(self, db: Session):
        self.db = db

    def _para_entidade(self, model: UsuarioModel) -> Usuario:
        """Converte UsuarioModel → Usuario (entidade de domínio)."""
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            cargo=model.cargo,
            criado_em=model.criado_em
        )

    def salvar(self, usuario: Usuario) -> Usuario:
        model = UsuarioModel(
            nome=usuario.nome,
            email=usuario.email,
            senha_hash=usuario.senha_hash,
            cargo=usuario.cargo,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._para_entidade(model)

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        model = self.db.query(UsuarioModel).filter(
            UsuarioModel.email == email
        ).first()
        return self._para_entidade(model) if model else None

    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        model = self.db.query(UsuarioModel).filter(
            UsuarioModel.id == id
        ).first()
        return self._para_entidade(model) if model else None

    def atualizar(self, usuario: Usuario) -> Usuario:
        model = self.db.query(UsuarioModel).filter(
            UsuarioModel.id == usuario.id
        ).first()

        if not model:
            raise ValueError("Usuário não encontrado no banco")

        model.nome = usuario.nome
        model.cargo = usuario.cargo
        model.senha_hash = usuario.senha_hash

        self.db.commit()
        self.db.refresh(model)
        return self._para_entidade(model)
