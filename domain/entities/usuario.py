from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """
    Entidade de domínio — representa um usuário do sistema.
    Não depende de nenhum framework (FastAPI, SQLAlchemy, etc).
    """
    id: Optional[int]
    nome: str
    email: str
    senha_hash: str
    cargo: str = ""
    criado_em: datetime = field(default_factory=datetime.utcnow)

    def tem_dados_completos(self) -> bool:
        return bool(self.nome and self.email and self.senha_hash)
