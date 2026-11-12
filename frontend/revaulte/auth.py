# Contas de acesso (Change contas-acesso): cadastro, login, sessão e área administrativa.
# O navegador não acessa o Xano: as requisições saem do servidor do Reflex, como no catálogo.
# A senha só existe dentro do evento de envio do formulário; nunca fica no estado nem em log.
import dataclasses
import re
from datetime import date, datetime, timezone
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

import httpx
import reflex as rx

from .config import admin_api_url, auth_api_url

TEMPO_LIMITE_SEGUNDOS = 10

# Rotas das páginas de conta.
ROTA_ENTRAR = "/entrar"
ROTA_CADASTRO = "/cadastro"
ROTA_CONTA = "/conta"
ROTA_ADMIN = "/admin"

# Cookie da sessão: só o token, com a mesma validade do token do Xano (24 h).
NOME_COOKIE = "revaulte_sessao"
VALIDADE_SESSAO_SEGUNDOS = 86400

ROTULOS_PERFIL = {"member": "Cliente", "admin": "Administrador"}

FUSO = ZoneInfo("America/Sao_Paulo")


# ---------------------------------------------------------------------------
# Validação dos formulários (repete no frontend as regras do backend).
# ---------------------------------------------------------------------------

_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def somente_digitos(texto: object) -> str:
    if not isinstance(texto, str):
        return ""
    return "".join(c for c in texto if c.isascii() and c.isdigit())


def _texto(valor: object) -> str:
    return " ".join(valor.split()) if isinstance(valor, str) else ""


def cpf_valido(cpf: str) -> bool:
    """CPF com 11 dígitos, não repetidos, e dígitos verificadores corretos."""
    if len(cpf) != 11 or not cpf.isdigit() or len(set(cpf)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11 % 10
        if digito != int(cpf[tamanho]):
            return False
    return True


def problema_senha(senha: object) -> str:
    """Mensagem do problema da senha, ou vazio quando ela atende à política do backend."""
    if not isinstance(senha, str) or len(senha) < 8:
        return "A senha deve ter pelo menos 8 caracteres."
    if not any(c.isalpha() for c in senha) or not any(c.isdigit() for c in senha):
        return "A senha deve ter pelo menos uma letra e um número."
    return ""


def ler_data_nascimento(texto: object, hoje: date | None = None) -> date | None:
    """Data AAAA-MM-DD real, no passado e a partir de 1900; senão None."""
    if not isinstance(texto, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", texto.strip()):
        return None
    try:
        data = date.fromisoformat(texto.strip())
    except ValueError:
        return None
    hoje = hoje or datetime.now(FUSO).date()
    if data.year < 1900 or data >= hoje:
        return None
    return data


def validar_cadastro(dados: dict, hoje: date | None = None) -> tuple[dict | None, str]:
    """(dados para o backend, "") ou (None, mensagem do primeiro problema encontrado)."""
    nome = _texto(dados.get("nome"))
    email = _texto(dados.get("email")).lower()
    cpf = somente_digitos(dados.get("cpf"))
    telefone = somente_digitos(dados.get("telefone"))
    nascimento = dados.get("nascimento")
    endereco = _texto(dados.get("endereco"))
    senha = dados.get("senha")
    confirmacao = dados.get("confirmacao")

    if not 2 <= len(nome) <= 100:
        return None, "Informe seu nome completo."
    if not _EMAIL.fullmatch(email):
        return None, "Informe um e-mail válido."
    if not cpf_valido(cpf):
        return None, "Informe um CPF válido."
    if not 10 <= len(telefone) <= 11:
        return None, "Informe o telefone com DDD."
    data = ler_data_nascimento(nascimento, hoje)
    if data is None:
        return None, "Informe uma data de nascimento válida."
    if not 5 <= len(endereco) <= 200:
        return None, "Informe seu endereço."
    problema = problema_senha(senha)
    if problema:
        return None, problema
    if senha != confirmacao:
        return None, "As senhas não coincidem."
    return {
        "name": nome,
        "email": email,
        "cpf": cpf,
        "phone": telefone,
        "birth_date": data.isoformat(),
        "address": endereco,
        "password": senha,
    }, ""


def validar_login(dados: dict) -> tuple[dict | None, str]:
    email = _texto(dados.get("email")).lower()
    senha = dados.get("senha")
    if not _EMAIL.fullmatch(email) or not isinstance(senha, str) or not senha:
        return None, "Informe e-mail e senha."
    return {"email": email, "password": senha}, ""


# Erros do cadastro devolvidos pelo backend (campo "message") e o texto exibido.
ERROS_CADASTRO = {
    "email_taken": "Este e-mail já está cadastrado. Entre com ele ou use outro.",
    "cpf_taken": "Este CPF já está cadastrado.",
    "invalid_name": "Informe seu nome completo.",
    "invalid_email": "Informe um e-mail válido.",
    "invalid_password": "A senha deve ter pelo menos 8 caracteres, com letra e número.",
    "invalid_cpf": "Informe um CPF válido.",
    "invalid_phone": "Informe o telefone com DDD.",
    "invalid_birth_date": "Informe uma data de nascimento válida.",
    "invalid_address": "Informe seu endereço.",
}
ERRO_GENERICO = "Não foi possível concluir agora. Verifique sua conexão e tente novamente."
ERRO_LOGIN = "E-mail ou senha incorretos."


def mensagem_erro_cadastro(status: int, corpo: object) -> str:
    mensagem = corpo.get("message") if isinstance(corpo, dict) else None
    if isinstance(mensagem, str) and mensagem in ERROS_CADASTRO:
        return ERROS_CADASTRO[mensagem]
    if isinstance(mensagem, str) and "already exists" in mensagem:
        return ERROS_CADASTRO["email_taken"]
    if status == 400:
        return "Confira os dados informados e tente novamente."
    return ERRO_GENERICO


def destino_seguro(proximo: object) -> str:
    """Só caminhos internos do site; qualquer outro valor leva a Minha conta."""
    if (
        isinstance(proximo, str)
        and proximo.startswith("/")
        and not proximo.startswith("//")
        and "\\" not in proximo
        and proximo not in (ROTA_ENTRAR, ROTA_CADASTRO)
    ):
        return proximo
    return ROTA_CONTA


def ler_proximo(params: object, caminho: object) -> str:
    """Parâmetro ?proximo= da página de login (pelos parâmetros da rota ou pelo caminho)."""
    if isinstance(params, dict) and isinstance(params.get("proximo"), str):
        return params["proximo"]
    if isinstance(caminho, str):
        valores = parse_qs(urlparse(caminho).query).get("proximo")
        if valores:
            return valores[0]
    return ""


def formatar_data(valor: object) -> str:
    """created_at do Xano (milissegundos) -> "dd/mm/aaaa" no horário de Brasília."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return ""
    try:
        return datetime.fromtimestamp(valor / 1000, tz=timezone.utc).astimezone(FUSO).strftime("%d/%m/%Y")
    except (OverflowError, OSError, ValueError):
        return ""


# ---------------------------------------------------------------------------
# Requisições ao Xano.
# ---------------------------------------------------------------------------


async def chamar_xano(metodo: str, url: str, token: str = "", dados: dict | None = None) -> tuple[int, object]:
    """(status HTTP, corpo JSON ou None). Falha de rede resulta em status 0."""
    cabecalhos = {"Accept": "application/json"}
    if token:
        cabecalhos["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=TEMPO_LIMITE_SEGUNDOS) as cliente:
            resposta = await cliente.request(metodo, url, headers=cabecalhos, json=dados)
    except httpx.HTTPError as erro:
        # Só o tipo do erro: a URL e o corpo podem conter dados pessoais.
        print(f"Falha de rede ao chamar o Xano: {type(erro).__name__}")
        return 0, None
    try:
        return resposta.status_code, resposta.json()
    except ValueError:
        return resposta.status_code, None


@dataclasses.dataclass
class Usuario:
    """Dados do usuário autenticado exibidos na interface (sem dados sensíveis)."""

    id: int = 0
    nome: str = ""
    email: str = ""
    perfil: str = ""  # "member" ou "admin"
    rotulo_perfil: str = ""
    desde: str = ""


def preparar_usuario(dados: object) -> Usuario | None:
    if not isinstance(dados, dict):
        return None
    id_usuario = dados.get("id")
    perfil = dados.get("role")
    if isinstance(id_usuario, bool) or not isinstance(id_usuario, int) or id_usuario <= 0:
        return None
    perfil = perfil if perfil in ROTULOS_PERFIL else "member"
    return Usuario(
        id=id_usuario,
        nome=_texto(dados.get("name")),
        email=_texto(dados.get("email")),
        perfil=perfil,
        rotulo_perfil=ROTULOS_PERFIL[perfil],
        desde=formatar_data(dados.get("created_at")),
    )


async def buscar_me(token: str) -> tuple[str, Usuario | None]:
    """("ok", usuário), ("invalido", None) para token recusado ou ("erro", None)."""
    if not token:
        return "invalido", None
    status, corpo = await chamar_xano("GET", f"{auth_api_url()}/auth/me", token)
    if status in (401, 403):
        return "invalido", None
    usuario = preparar_usuario(corpo) if status == 200 else None
    return ("ok", usuario) if usuario else ("erro", None)


def _token_da_resposta(corpo: object) -> str:
    token = corpo.get("authToken") if isinstance(corpo, dict) else None
    return token if isinstance(token, str) and token else ""


# ---------------------------------------------------------------------------
# Estado da sessão.
# ---------------------------------------------------------------------------


class AuthState(rx.State):
    """Sessão do usuário. O perfil vem sempre do backend (auth/me), nunca do navegador."""

    token: str = rx.Cookie(
        "", name=NOME_COOKIE, max_age=VALIDADE_SESSAO_SEGUNDOS, same_site="strict"
    )
    usuario: Usuario = Usuario()
    # Token já conferido no backend nesta sessão do Reflex.
    verificado: bool = False
    # Página protegida: "carregando", "ok", "restrito" ou "erro".
    situacao_protegida: str = "carregando"
    # Formulários: mensagem de erro e envio em andamento.
    erro_formulario: str = ""
    enviando: bool = False
    proximo: str = ""

    @rx.var
    def autenticado(self) -> bool:
        return self.usuario.id > 0

    @rx.var
    def administrador(self) -> bool:
        return self.usuario.id > 0 and self.usuario.perfil == "admin"

    def _encerrar(self):
        self.token = ""
        self.usuario = Usuario()
        self.verificado = False

    @rx.event
    async def verificar_sessao(self):
        """on_load das páginas públicas: confere o token uma vez para o menu da conta."""
        if not self.token:
            self.usuario = Usuario()
            self.verificado = False
            return
        if self.verificado:
            return
        situacao, usuario = await buscar_me(self.token)
        if situacao == "invalido":
            self._encerrar()
            return rx.remove_cookie(NOME_COOKIE)
        if usuario is not None:
            self.usuario = usuario
            self.verificado = True

    async def _exigir(self, rota: str, perfil: str | None):
        self.situacao_protegida = "carregando"
        if not self.token:
            self._encerrar()
            return rx.redirect(f"{ROTA_ENTRAR}?proximo={rota}")
        situacao, usuario = await buscar_me(self.token)
        if situacao == "invalido":
            self._encerrar()
            return [rx.remove_cookie(NOME_COOKIE), rx.redirect(f"{ROTA_ENTRAR}?proximo={rota}")]
        if usuario is None:
            self.situacao_protegida = "erro"
            return
        self.usuario = usuario
        self.verificado = True
        if perfil is not None and usuario.perfil != perfil:
            self.situacao_protegida = "restrito"
            return
        self.situacao_protegida = "ok"

    @rx.event
    async def exigir_login(self):
        """on_load de /conta."""
        return await self._exigir(ROTA_CONTA, None)

    @rx.event
    async def exigir_admin(self):
        """on_load de /admin: perfil conferido no backend; Cliente vê “Acesso restrito”."""
        resultado = await self._exigir(ROTA_ADMIN, "admin")
        if resultado is not None:
            return resultado
        if self.situacao_protegida == "ok":
            return AdminState.carregar_usuarios

    @rx.event
    def abrir_formulario(self):
        """on_load de /entrar e /cadastro: limpa mensagens e guarda o destino pedido."""
        self.erro_formulario = ""
        self.enviando = False
        self.proximo = destino_seguro(ler_proximo(self.router.page.params, self.router.page.raw_path))
        if self.autenticado and self.token:
            return rx.redirect(self.proximo)

    async def _concluir_entrada(self, token: str):
        situacao, usuario = await buscar_me(token)
        if usuario is None:
            self.enviando = False
            self.erro_formulario = ERRO_GENERICO
            return
        self.token = token
        self.usuario = usuario
        self.verificado = True
        self.enviando = False
        return rx.redirect(destino_seguro(self.proximo))

    @rx.event
    async def entrar(self, dados_formulario: dict):
        payload, erro = validar_login(dados_formulario)
        if payload is None:
            self.erro_formulario = erro
            return
        self.erro_formulario = ""
        self.enviando = True
        yield
        status, corpo = await chamar_xano("POST", f"{auth_api_url()}/auth/login", dados=payload)
        token = _token_da_resposta(corpo) if status == 200 else ""
        if not token:
            self.enviando = False
            self.erro_formulario = ERRO_LOGIN if status in (400, 401, 403, 404) else ERRO_GENERICO
            return
        yield await self._concluir_entrada(token)

    @rx.event
    async def cadastrar(self, dados_formulario: dict):
        payload, erro = validar_cadastro(dados_formulario)
        if payload is None:
            self.erro_formulario = erro
            return
        self.erro_formulario = ""
        self.enviando = True
        yield
        status, corpo = await chamar_xano("POST", f"{auth_api_url()}/auth/signup", dados=payload)
        token = _token_da_resposta(corpo) if status == 200 else ""
        if not token:
            self.enviando = False
            self.erro_formulario = mensagem_erro_cadastro(status, corpo)
            return
        yield await self._concluir_entrada(token)

    @rx.event
    def sair(self):
        self._encerrar()
        return [rx.remove_cookie(NOME_COOKIE), rx.redirect("/")]


# ---------------------------------------------------------------------------
# Área administrativa.
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class LinhaUsuario:
    id: int = 0
    nome: str = ""
    email: str = ""
    perfil: str = ""
    desde: str = ""


def preparar_linhas_usuarios(dados: object) -> list[LinhaUsuario]:
    if not isinstance(dados, list):
        raise ValueError("Resposta inesperada da lista de usuários")
    linhas = []
    for item in dados:
        usuario = preparar_usuario(item)
        if usuario is not None:
            linhas.append(
                LinhaUsuario(usuario.id, usuario.nome, usuario.email, usuario.rotulo_perfil, usuario.desde)
            )
    return linhas


class AdminState(rx.State):
    """Painel administrativo: dados carregados somente após o backend aceitar o perfil."""

    situacao: str = "carregando"  # "carregando", "lista", "restrito" ou "erro"
    usuarios: list[LinhaUsuario] = []

    @rx.event
    async def carregar_usuarios(self):
        self.situacao = "carregando"
        self.usuarios = []
        yield
        auth = await self.get_state(AuthState)
        status, corpo = await chamar_xano("GET", f"{admin_api_url()}/users", auth.token)
        if status in (401, 403):
            self.situacao = "restrito"
            return
        try:
            if status != 200:
                raise ValueError(f"status {status}")
            self.usuarios = preparar_linhas_usuarios(corpo)
        except ValueError as erro:
            print(f"Falha ao carregar usuários: {erro}")
            self.situacao = "erro"
            return
        self.situacao = "lista"
