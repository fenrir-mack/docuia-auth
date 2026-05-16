from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    """
    Port de saída — contrato que o domínio exige para persistência.
    O domínio conhece apenas esta interface, nunca o banco real.
    """

    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        """Cria ou atualiza um usuário. Retorna o usuário com id preenchido."""
        pass

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Retorna o usuário com o email informado, ou None se não existir."""
        pass

    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        """Retorna o usuário com o id informado, ou None se não existir."""
        pass

    @abstractmethod
    def atualizar(self, usuario: Usuario) -> Usuario:
        """Atualiza os dados de um usuário existente."""
        pass
