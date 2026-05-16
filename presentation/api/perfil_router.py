from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from infrastructure.database.conexao import get_db
from infrastructure.database.usuario_repository_impl import UsuarioRepositoryImpl
from application.use_cases.auth_use_cases import EditarPerfilUseCase, AlterarSenhaUseCase

router = APIRouter(prefix="/perfil", tags=["Perfil"])
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "docuia-secret-dev")


def get_usuario_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extrai e valida o JWT do header Authorization, retorna o id do usuário."""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


# --- Schemas ---

class EditarPerfilInput(BaseModel):
    nome: str
    cargo: str
    bio: str

class AlterarSenhaInput(BaseModel):
    senha_atual: str
    nova_senha: str


# --- Endpoints ---

@router.get("/me")
def meu_perfil(
    usuario_id: int = Depends(get_usuario_id),
    db: Session = Depends(get_db)
):
    """Retorna os dados do usuário autenticado."""
    repo = UsuarioRepositoryImpl(db)
    usuario = repo.buscar_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "cargo": usuario.cargo,
        "bio": usuario.bio
    }


@router.post("/usuarios/batch")
def obter_usuarios_batch(
    ids: list[int],
    db: Session = Depends(get_db)
):
    """Retorna dados básicos de múltiplos usuários."""
    repo = UsuarioRepositoryImpl(db)
    resultado = []
    # Remoção de duplicatas para otimizar
    ids = list(set(ids))
    for uid in ids:
        u = repo.buscar_por_id(uid)
        if u:
            resultado.append({
                "id": u.id,
                "nome": u.nome,
                "cargo": u.cargo
            })
    return resultado


@router.put("/me")
def editar_perfil(
    dados: EditarPerfilInput,
    usuario_id: int = Depends(get_usuario_id),
    db: Session = Depends(get_db)
):
    """Atualiza nome, cargo e bio do usuário autenticado."""
    repo = UsuarioRepositoryImpl(db)
    use_case = EditarPerfilUseCase(repo)
    try:
        usuario = use_case.executar(usuario_id, dados.nome, dados.cargo, dados.bio)
        return {"mensagem": "Perfil atualizado", "nome": usuario.nome}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/me/senha")
def alterar_senha(
    dados: AlterarSenhaInput,
    usuario_id: int = Depends(get_usuario_id),
    db: Session = Depends(get_db)
):
    """Altera a senha do usuário autenticado."""
    repo = UsuarioRepositoryImpl(db)
    use_case = AlterarSenhaUseCase(repo)
    try:
        use_case.executar(usuario_id, dados.senha_atual, dados.nova_senha)
        return {"mensagem": "Senha alterada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
