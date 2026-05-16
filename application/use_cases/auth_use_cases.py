from domain.entities.usuario import Usuario
from domain.ports.usuario_repository import IUsuarioRepository
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "docuia-secret-dev")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY", "24"))


class LoginUseCase:
    """
    Caso de uso: Autenticar um usuário com email e senha.
    Retorna um JWT token em caso de sucesso.
    """

    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def executar(self, email: str, senha: str) -> str:
        usuario = self.repository.buscar_por_email(email)

        if not usuario:
            raise ValueError("Email ou senha inválidos")

        if not pwd_context.verify(senha[:72], usuario.senha_hash):
            raise ValueError("Email ou senha inválidos")

        payload = {
            "sub": str(usuario.id),
            "email": usuario.email,
            "nome": usuario.nome,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token


class CadastroUseCase:
    """
    Caso de uso: Registrar um novo usuário no sistema.
    Retorna o usuário criado.
    """

    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def executar(self, nome: str, email: str, senha: str) -> Usuario:
        existente = self.repository.buscar_por_email(email)
        if existente:
            raise ValueError("Já existe uma conta com este e-mail")

        print(f"DEBUG - Tamanho real da senha recebida: {len(senha)} caracteres")
        senha_hash = pwd_context.hash(senha[:72])

        novo_usuario = Usuario(
            id=None,
            nome=nome,
            email=email,
            senha_hash=senha_hash
        )

        return self.repository.salvar(novo_usuario)


class RecuperarSenhaUseCase:
    """
    Caso de uso: Gerar token de recuperação de senha.
    (Por simplicidade, retorna o token direto — em produção enviaria por email)
    """

    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def executar(self, email: str) -> str:
        usuario = self.repository.buscar_por_email(email)
        if not usuario:
            # Por segurança, não revelamos se o email existe ou não
            return "Se o email estiver cadastrado, você receberá as instruções"

        payload = {
            "sub": str(usuario.id),
            "tipo": "recuperar_senha",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token


class RedefinirSenhaUseCase:
    """
    Caso de uso: Redefinir senha a partir de um token de recuperação.
    """

    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def executar(self, token: str, nova_senha: str) -> None:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception:
            raise ValueError("Token inválido ou expirado")

        if payload.get("tipo") != "recuperar_senha":
            raise ValueError("Token inválido")

        usuario_id = int(payload["sub"])
        usuario = self.repository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado")

        usuario.senha_hash = pwd_context.hash(nova_senha[:72])
        self.repository.atualizar(usuario)


class EditarPerfilUseCase:
    """
    Caso de uso: Atualizar dados do perfil do usuário logado.
    """

    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def executar(self, usuario_id: int, nome: str, cargo: str, bio: str) -> Usuario:
        usuario = self.repository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado")

        usuario.nome = nome
        usuario.cargo = cargo
        usuario.bio = bio

        return self.repository.atualizar(usuario)


class AlterarSenhaUseCase:
    """
    Caso de uso: Alterar senha do usuário logado (exige senha atual).
    """

    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def executar(self, usuario_id: int, senha_atual: str, nova_senha: str) -> None:
        usuario = self.repository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado")

        if not pwd_context.verify(senha_atual[:72], usuario.senha_hash):
            raise ValueError("Senha atual incorreta")

        usuario.senha_hash = pwd_context.hash(nova_senha[:72])
        self.repository.atualizar(usuario)
