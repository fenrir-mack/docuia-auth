from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from infrastructure.database.conexao import get_db
from infrastructure.database.usuario_repository_impl import UsuarioRepositoryImpl
from application.use_cases.auth_use_cases import (
    LoginUseCase,
    CadastroUseCase,
    RecuperarSenhaUseCase,
    RedefinirSenhaUseCase
)

router = APIRouter(prefix="/auth", tags=["Autenticaﾃｧﾃ｣o"])


# --- Schemas de entrada (o que o frontend envia) ---

class LoginInput(BaseModel):
    email: str
    senha: str

class CadastroInput(BaseModel):
    nome: str
    cargo: str
    email: str
    senha: str

class RecuperarSenhaInput(BaseModel):
    email: str

class RedefinirSenhaInput(BaseModel):
    token: str
    nova_senha: str


# --- Endpoints ---

@router.post("/login")
def login(dados: LoginInput, db: Session = Depends(get_db)):
    """Autentica o usuﾃ｡rio e retorna um JWT token."""
    repo = UsuarioRepositoryImpl(db)
    use_case = LoginUseCase(repo)
    try:
        token = use_case.executar(dados.email, dados.senha)
        return {"token": token, "tipo": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/cadastro", status_code=201)
def cadastro(dados: CadastroInput, db: Session = Depends(get_db)):
    """Registra um novo usuﾃ｡rio."""
    try:
        repo = UsuarioRepositoryImpl(db)
        use_case = CadastroUseCase(repo)
        usuario = use_case.executar(dados.nome, dados.cargo, dados.email, dados.senha)
        return {"mensagem": "Conta criada com sucesso", "id": usuario.id}
    except Exception as e:
        # Captura QUALQUER erro (banco, cﾃｳdigo, etc) e retorna como 400 para vermos no frontend
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/esqueceu-senha")
def esqueceu_senha(dados: RecuperarSenhaInput, db: Session = Depends(get_db)):
    """Inicia o fluxo de recuperaﾃｧﾃ｣o de senha."""
    repo = UsuarioRepositoryImpl(db)
    use_case = RecuperarSenhaUseCase(repo)
    token = use_case.executar(dados.email)
    return {"mensagem": "Instruﾃｧﾃｵes enviadas", "token_recuperacao": token}


@router.post("/redefinir-senha")
def redefinir_senha(dados: RedefinirSenhaInput, db: Session = Depends(get_db)):
    """Redefine a senha usando o token de recuperaﾃｧﾃ｣o."""
    repo = UsuarioRepositoryImpl(db)
    use_case = RedefinirSenhaUseCase(repo)
    try:
        use_case.executar(dados.token, dados.nova_senha)
        return {"mensagem": "Senha redefinida com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

