# Anúncios enviados por Clientes autenticados (Change anuncios-cliente, tarefas 4.2 e 5.1).
# Funções puras: validação do formulário, preparação das respostas e tradução de erros.
# Os estados e as páginas (tarefas 4.3 e 5.2) usam estas funções; o navegador nunca acessa o Xano.
import dataclasses
import re
from datetime import date, datetime, timezone
from decimal import Decimal

import reflex as rx

from .auth import (
    NOME_COOKIE,
    ROTA_ANUNCIAR,
    ROTA_ENTRAR,
    ROTA_MEUS_ANUNCIOS,
    AuthState,
    _texto,
    chamar_xano,
    formatar_data,
)
from .config import anuncios_api_url
from .state import ROTULOS_CONDICAO, formatar_preco, formatar_quilometragem, ler_valor_br

# Estados do anúncio (vehicle.status) e o texto exibido ao dono.
ROTULOS_ESTADO = {
    "draft": "Rascunho — aguardando publicação",
    "available": "Publicado",
    "sold": "Vendido",
}
# Só anúncios publicados ou vendidos têm página pública (/veiculo/<id>).
ROTA_FICHA_ANUNCIO = "/meus-anuncios/[anuncio_id]"  # página privada de um anúncio
ESTADOS_PUBLICOS = frozenset({"available", "sold"})

# Limites da decisão 6 do design.md (iguais aos do backend, anuncios_POST.xs).
ANO_MINIMO = 1886
QUILOMETRAGEM_MAXIMA = 2_000_000
PRECO_MAXIMO = Decimal("100000000")
LIMITES_TEXTO = {  # campo do formulário -> (mínimo, máximo); mínimo 0 = opcional
    "marca": (1, 40),
    "modelo": (1, 60),
    "versao": (0, 80),
    "cor": (0, 60),
    "motorizacao": (0, 60),
    "cambio": (0, 60),
    "descricao": (0, 2000),
    "nome_exibicao": (2, 60),
}
# Campo do formulário -> campo do backend.
CAMPOS_BACKEND = {
    "nome_exibicao": "display_name",
    "marca": "brand",
    "modelo": "model",
    "versao": "version",
    "ano": "year",
    "condicao": "condition",
    "quilometragem": "mileage",
    "preco": "price",
    "modificado": "is_modified",
    "cor": "color",
    "motorizacao": "engine",
    "cambio": "transmission",
    "descricao": "description",
}

# Mensagens dos erros de validação, iguais no frontend e na tradução dos códigos do backend.
MENSAGENS_VALIDACAO = {
    "invalid_display_name": "Informe o nome de exibição do anunciante (2 a 60 caracteres).",
    "invalid_brand": "Informe a marca (até 40 caracteres).",
    "invalid_model": "Informe o modelo (até 60 caracteres).",
    "invalid_version": "A versão pode ter até 80 caracteres.",
    "invalid_year": "Informe um ano válido, de 1886 até o próximo ano.",
    "invalid_condition": "Informe se o veículo é novo ou usado.",
    "invalid_mileage": "Informe a quilometragem em km, de 0 a 2.000.000, sem casas decimais.",
    "invalid_price": "Informe um preço maior que zero, até R$ 100.000.000,00, com no máximo 2 casas decimais.",
    "invalid_is_modified": "Informe se o veículo é modificado.",
    "invalid_color": "A cor pode ter até 60 caracteres.",
    "invalid_engine": "A motorização pode ter até 60 caracteres.",
    "invalid_transmission": "O câmbio pode ter até 60 caracteres.",
    "invalid_description": "A descrição pode ter até 2.000 caracteres.",
}
_CODIGO_DO_CAMPO = {
    "nome_exibicao": "invalid_display_name",
    "marca": "invalid_brand",
    "modelo": "invalid_model",
    "versao": "invalid_version",
    "cor": "invalid_color",
    "motorizacao": "invalid_engine",
    "cambio": "invalid_transmission",
    "descricao": "invalid_description",
}

ERRO_LIMITE_RASCUNHOS = (
    "Você já tem 20 anúncios aguardando publicação. Aguarde a equipe publicar algum deles antes de enviar outro."
)
ERRO_MUITAS_TENTATIVAS = "Muitas tentativas em pouco tempo. Aguarde alguns segundos e tente novamente."
ERRO_SESSAO = "Sua sessão expirou. Entre novamente para continuar."
ERRO_RESTRITO = "Sua conta não tem permissão para anunciar. Fale com a equipe da Revaulte."
ERRO_NAO_ENCONTRADO = "Anúncio não encontrado."
ERRO_DADOS = "Confira os dados informados e tente novamente."
ERRO_GENERICO_ANUNCIO = "Não foi possível concluir agora. Verifique sua conexão e tente novamente."

_INTEIRO = re.compile(r"[0-9]{1,7}")
_INTEIRO_COM_MILHAR = re.compile(r"[0-9]{1,3}(\.[0-9]{3})+")


# ---------------------------------------------------------------------------
# Validação do formulário (tarefa 5.1).
# ---------------------------------------------------------------------------


def _texto_livre(valor: object) -> str:
    """Descrição: apara as pontas e preserva as quebras de linha."""
    return valor.strip() if isinstance(valor, str) else ""


def ler_ano(valor: object, hoje: date | None = None) -> int | None:
    """Ano inteiro de 1886 até o ano atual + 1. O backend calcula o ano em UTC; aqui também."""
    texto = valor.strip() if isinstance(valor, str) else ""
    if not re.fullmatch(r"[0-9]{4}", texto):
        return None
    ano = int(texto)
    atual = (hoje or datetime.now(timezone.utc).date()).year
    return ano if ANO_MINIMO <= ano <= atual + 1 else None


def ler_quilometragem(valor: object) -> int | None:
    """Inteiro de 0 a 2.000.000; aceita pontos de milhar ("120.000") e o sufixo "km"."""
    if not isinstance(valor, str):
        return None
    texto = valor.strip().lower().removesuffix("km").strip()
    if _INTEIRO_COM_MILHAR.fullmatch(texto):
        texto = texto.replace(".", "")
    if not _INTEIRO.fullmatch(texto):
        return None
    km = int(texto)
    return km if km <= QUILOMETRAGEM_MAXIMA else None


def ler_preco(valor: object) -> Decimal | None:
    """Preço no formato brasileiro ("45.000,00", "R$ 45000"): maior que 0, até 100 milhões, 2 casas."""
    numero = ler_valor_br(valor)
    if numero is None or numero <= 0 or numero > PRECO_MAXIMO:
        return None
    if numero != numero.quantize(Decimal("0.01")):
        return None
    return numero


def _ler_texto(dados: dict, campo: str) -> tuple[str | None, str]:
    """(texto aparado, "") ou (None, mensagem) conforme LIMITES_TEXTO; vazio em opcional vira ""."""
    minimo, maximo = LIMITES_TEXTO[campo]
    valor = _texto_livre(dados.get(campo)) if campo == "descricao" else _texto(dados.get(campo))
    if (minimo == 0 and valor == "") or minimo <= len(valor) <= maximo:
        return valor, ""
    return None, MENSAGENS_VALIDACAO[_CODIGO_DO_CAMPO[campo]]


def validar_anuncio(
    dados: dict, tem_anunciante: bool, hoje: date | None = None
) -> tuple[dict | None, str]:
    """(dados para o backend, "") ou (None, mensagem do primeiro problema, na ordem da tela).

    `tem_anunciante`: a conta já tem anunciante (GET /anuncios); então o nome de exibição não
    é enviado, porque o backend o ignora (decisão 3). Campos opcionais vazios não são enviados.
    Nunca inclui status, seller_id, user_id ou imagem: o backend os define (decisão 5).
    """
    payload: dict = {}

    def texto(campo: str) -> str | None:
        valor, erro = _ler_texto(dados, campo)
        if valor is None:
            raise _Invalido(erro)
        if valor:
            payload[CAMPOS_BACKEND[campo]] = valor
        return valor

    try:
        if not tem_anunciante:
            texto("nome_exibicao")
        texto("marca")
        texto("modelo")
        texto("versao")

        ano = ler_ano(dados.get("ano"), hoje)
        if ano is None:
            raise _Invalido(MENSAGENS_VALIDACAO["invalid_year"])
        payload["year"] = ano

        condicao = dados.get("condicao")
        if condicao not in ROTULOS_CONDICAO:
            raise _Invalido(MENSAGENS_VALIDACAO["invalid_condition"])
        payload["condition"] = condicao

        km = ler_quilometragem(dados.get("quilometragem"))
        if km is None:
            raise _Invalido(MENSAGENS_VALIDACAO["invalid_mileage"])
        payload["mileage"] = km

        preco = ler_preco(dados.get("preco"))
        if preco is None:
            raise _Invalido(MENSAGENS_VALIDACAO["invalid_price"])
        payload["price"] = float(preco)

        modificado = dados.get("modificado")
        if modificado not in ("sim", "nao"):
            raise _Invalido(MENSAGENS_VALIDACAO["invalid_is_modified"])
        payload["is_modified"] = modificado == "sim"

        for campo in ("cor", "motorizacao", "cambio", "descricao"):
            texto(campo)
    except _Invalido as erro:
        return None, str(erro)
    return payload, ""


class _Invalido(Exception):
    """Primeiro problema do formulário; a mensagem é o texto exibido."""


# ---------------------------------------------------------------------------
# Preparação das respostas (tarefa 4.2). Só os campos da lista da decisão 5 são lidos:
# qualquer outro campo que o backend devolva (por exemplo, seller_id) é descartado.
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class ResumoAnuncio:
    """Linha de "Meus anúncios", já formatada como texto."""

    id: int = 0
    titulo: str = ""  # marca, modelo e versão
    ano: str = ""
    preco: str = ""
    estado: str = ""  # draft, available ou sold
    rotulo_estado: str = ""
    enviado_em: str = ""  # dd/mm/aaaa
    endereco: str = ""  # /meus-anuncios/<id>


@dataclasses.dataclass
class FichaAnuncio(ResumoAnuncio):
    """Ficha privada do próprio anúncio (/meus-anuncios/<id>)."""

    marca: str = ""
    modelo: str = ""
    versao: str = ""
    condicao: str = ""
    quilometragem: str = ""
    modificado: str = ""  # "Sim" ou "Não"
    cor: str = ""
    motorizacao: str = ""
    cambio: str = ""
    descricao: str = ""
    endereco_publico: str = ""  # /veiculo/<id>, só para Publicado ou Vendido


def _id_valido(valor: object) -> int | None:
    return valor if isinstance(valor, int) and not isinstance(valor, bool) and valor > 0 else None


def _resumo(item: object) -> ResumoAnuncio | None:
    if not isinstance(item, dict):
        return None
    id_anuncio = _id_valido(item.get("id"))
    estado = item.get("status")
    if id_anuncio is None or estado not in ROTULOS_ESTADO:
        return None
    try:
        preco = formatar_preco(item.get("price"))
    except ValueError:
        return None
    ano = item.get("year")
    titulo = " ".join(p for p in (_texto(item.get("brand")), _texto(item.get("model")), _texto(item.get("version"))) if p)
    return ResumoAnuncio(
        id=id_anuncio,
        titulo=titulo,
        ano=str(ano) if _id_valido(ano) else "",
        preco=preco,
        estado=estado,
        rotulo_estado=ROTULOS_ESTADO[estado],
        enviado_em=formatar_data(item.get("created_at")),
        endereco=f"{ROTA_MEUS_ANUNCIOS}/{id_anuncio}",
    )


def preparar_lista(corpo: object) -> tuple[str, list[ResumoAnuncio]]:
    """GET /anuncios -> (nome de exibição do anunciante ou "", anúncios na ordem recebida).

    Levanta ValueError quando a resposta não tem o formato esperado (a página mostra o erro,
    nunca uma lista parcial). Itens malformados são descartados.
    """
    if not isinstance(corpo, dict) or not isinstance(corpo.get("anuncios"), list):
        raise ValueError("Resposta inesperada da lista de anúncios")
    anunciante = corpo.get("anunciante")
    nome = _texto(anunciante.get("display_name")) if isinstance(anunciante, dict) else ""
    anuncios = [r for r in (_resumo(item) for item in corpo["anuncios"]) if r is not None]
    return nome, anuncios


def preparar_ficha(corpo: object) -> FichaAnuncio | None:
    """GET /anuncios/{id} -> ficha, ou None quando a resposta não tem o formato esperado."""
    resumo = _resumo(corpo)
    if resumo is None:
        return None
    try:
        quilometragem = formatar_quilometragem(corpo.get("mileage"))
    except ValueError:
        quilometragem = ""
    modificado = corpo.get("is_modified")
    return FichaAnuncio(
        **dataclasses.asdict(resumo),
        marca=_texto(corpo.get("brand")),
        modelo=_texto(corpo.get("model")),
        versao=_texto(corpo.get("version")),
        condicao=ROTULOS_CONDICAO.get(corpo.get("condition"), ""),
        quilometragem=quilometragem,
        modificado="Sim" if modificado is True else "Não" if modificado is False else "",
        cor=_texto(corpo.get("color")),
        motorizacao=_texto(corpo.get("engine")),
        cambio=_texto(corpo.get("transmission")),
        descricao=_texto_livre(corpo.get("description")),
        endereco_publico=f"/veiculo/{resumo.id}" if resumo.estado in ESTADOS_PUBLICOS else "",
    )


def ler_id_anuncio(valor: object) -> int | None:
    """Identificador da rota /meus-anuncios/<id>: 1 a 12 dígitos, sem zero à esquerda."""
    if isinstance(valor, str) and re.fullmatch(r"[1-9][0-9]{0,11}", valor):
        return int(valor)
    return None


# ---------------------------------------------------------------------------
# Tradução de erros (tarefa 4.2).
# ---------------------------------------------------------------------------


def situacao_da_resposta(status: int) -> str:
    """Classifica a resposta: "ok", "sessao" (401), "restrito" (403), "nao_encontrado" (404),
    "limite" (429), "dados" (400) ou "erro" (rede = status 0, ou qualquer outro)."""
    return {200: "ok", 400: "dados", 401: "sessao", 403: "restrito", 404: "nao_encontrado", 429: "limite"}.get(
        status, "erro"
    )


def mensagem_erro_anuncio(status: int, corpo: object) -> str:
    """Texto exibido para uma resposta diferente de 200."""
    codigo = corpo.get("message") if isinstance(corpo, dict) else None
    if status == 400 and isinstance(codigo, str):
        if codigo in MENSAGENS_VALIDACAO:
            return MENSAGENS_VALIDACAO[codigo]
        if codigo == "draft_limit_reached":
            return ERRO_LIMITE_RASCUNHOS
    return {
        "dados": ERRO_DADOS,
        "sessao": ERRO_SESSAO,
        "restrito": ERRO_RESTRITO,
        "nao_encontrado": ERRO_NAO_ENCONTRADO,
        "limite": ERRO_MUITAS_TENTATIVAS,
    }.get(situacao_da_resposta(status), ERRO_GENERICO_ANUNCIO)


# ---------------------------------------------------------------------------
# Estados das páginas (tarefas 4.3 e 5.2). A sessão é conferida no backend (auth/me) por
# AuthState._exigir a cada abertura; o token só sai no cabeçalho das requisições do servidor.
# ---------------------------------------------------------------------------

AVISO_ENVIADO = "Anúncio enviado. Ele aparecerá no site depois de publicado pela equipe da Revaulte."
TAMANHO_MAXIMO_NOME = LIMITES_TEXTO["nome_exibicao"][1]


def _sessao_expirada(auth, rota: str) -> list:
    """401 de um endpoint de anúncios: encerra a sessão e leva ao login, voltando à mesma página."""
    auth._encerrar()
    return [rx.remove_cookie(NOME_COOKIE), rx.redirect(f"{ROTA_ENTRAR}?proximo={rota}")]


async def _consultar_anuncios(token: str) -> tuple[int, object]:
    return await chamar_xano("GET", f"{anuncios_api_url()}/anuncios", token)


class MeusAnunciosState(rx.State):
    """Página /meus-anuncios: lista somente os anúncios da conta (o backend filtra pelo token)."""

    situacao: str = "carregando"  # "carregando", "lista", "restrito" ou "erro"
    anunciante: str = ""
    anuncios: list[ResumoAnuncio] = []
    aviso: str = ""
    mensagem_erro: str = ""
    # Marcado por AnunciarState após um envio aceito; mostrado uma vez na próxima abertura.
    _aviso_pendente: bool = False

    @rx.event
    def limpar(self):
        """Apaga a lista (saída da conta)."""
        self.situacao = "carregando"
        self.anunciante = ""
        self.anuncios = []
        self.aviso = ""
        self.mensagem_erro = ""
        self._aviso_pendente = False

    @rx.event
    async def abrir(self):
        """on_load de /meus-anuncios e ação de "Tentar novamente"."""
        self.situacao = "carregando"
        self.anunciante = ""
        self.anuncios = []
        self.mensagem_erro = ""
        self.aviso = AVISO_ENVIADO if self._aviso_pendente else ""
        self._aviso_pendente = False
        yield
        auth = await self.get_state(AuthState)
        redirecionar = await auth._exigir(ROTA_MEUS_ANUNCIOS, None)
        if redirecionar is not None:
            self.aviso = ""
            yield redirecionar
            return
        if auth.situacao_protegida != "ok":
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_ANUNCIO
            return
        status, corpo = await _consultar_anuncios(auth.token)
        if status == 401:
            self.aviso = ""
            yield _sessao_expirada(auth, ROTA_MEUS_ANUNCIOS)
            return
        if status == 403:
            self.situacao = "restrito"
            return
        if status != 200:
            self.situacao = "erro"
            self.mensagem_erro = mensagem_erro_anuncio(status, corpo)
            return
        try:
            self.anunciante, self.anuncios = preparar_lista(corpo)
        except ValueError as erro:
            print(f"Falha ao carregar anúncios: {erro}")
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_ANUNCIO
            return
        self.situacao = "lista"


def _zerar_anunciar(estado) -> None:
    estado.situacao = "carregando"
    estado.tem_anunciante = False
    estado.nome_anunciante = ""
    estado.nome_sugerido = ""
    estado.mensagem_erro = ""
    estado.erro_formulario = ""
    estado.enviando = False


class AnunciarState(rx.State):
    """Página /anunciar. Os dados digitados não ficam no estado: só chegam no envio (formulário
    não controlado), como em /cadastro."""

    situacao: str = "carregando"  # "carregando", "pronto", "restrito" ou "erro"
    tem_anunciante: bool = False
    nome_anunciante: str = ""
    nome_sugerido: str = ""
    mensagem_erro: str = ""  # falha ao abrir a página
    erro_formulario: str = ""
    enviando: bool = False

    @rx.event
    def limpar(self):
        """Apaga o que veio da conta (saída da conta)."""
        _zerar_anunciar(self)

    @rx.event
    async def abrir(self):
        """on_load de /anunciar: confere a sessão e consulta se a conta já tem anunciante (decisão 3)."""
        _zerar_anunciar(self)
        yield
        auth = await self.get_state(AuthState)
        redirecionar = await auth._exigir(ROTA_ANUNCIAR, None)
        if redirecionar is not None:
            yield redirecionar
            return
        if auth.situacao_protegida != "ok":
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_ANUNCIO
            return
        status, corpo = await _consultar_anuncios(auth.token)
        if status == 401:
            yield _sessao_expirada(auth, ROTA_ANUNCIAR)
            return
        if status == 403:
            self.situacao = "restrito"
            return
        try:
            if status != 200:
                raise ValueError(f"status {status}")
            nome, _ = preparar_lista(corpo)
        except ValueError as erro:
            print(f"Falha ao consultar o anunciante: {erro}")
            self.situacao = "erro"
            self.mensagem_erro = mensagem_erro_anuncio(status, corpo) if status != 200 else ERRO_GENERICO_ANUNCIO
            return
        self.tem_anunciante = nome != ""
        self.nome_anunciante = nome
        # Sugestão: o nome da conta, quando cabe no limite; senão o Cliente preenche.
        nome_conta = auth.usuario.nome
        self.nome_sugerido = nome_conta if len(nome_conta) <= TAMANHO_MAXIMO_NOME else ""
        self.situacao = "pronto"

    @rx.event
    async def enviar(self, dados_formulario: dict):
        if self.enviando:
            return
        payload, erro = validar_anuncio(dados_formulario, self.tem_anunciante)
        if payload is None:
            self.erro_formulario = erro
            return
        self.erro_formulario = ""
        self.enviando = True
        yield
        auth = await self.get_state(AuthState)
        status, corpo = await chamar_xano("POST", f"{anuncios_api_url()}/anuncios", auth.token, payload)
        if status == 401:
            self.enviando = False
            yield _sessao_expirada(auth, ROTA_ANUNCIAR)
            return
        if status != 200 or not isinstance(corpo, dict) or _id_valido(corpo.get("id")) is None:
            self.enviando = False
            self.erro_formulario = (
                mensagem_erro_anuncio(status, corpo) if status != 200 else ERRO_GENERICO_ANUNCIO
            )
            return
        meus = await self.get_state(MeusAnunciosState)
        meus._aviso_pendente = True
        self.enviando = False
        yield rx.redirect(ROTA_MEUS_ANUNCIOS)


def _id_da_rota_anuncio(params: object, caminho: object) -> str:
    """Texto do identificador: parâmetro da rota dinâmica ou, na falta dele, o fim do caminho."""
    if isinstance(params, dict):
        valor = params.get("anuncio_id")
        if isinstance(valor, str):
            return valor
    if isinstance(caminho, str) and caminho.startswith(ROTA_MEUS_ANUNCIOS + "/"):
        return caminho.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    return ""


def _zerar_ficha(estado) -> None:
    estado.situacao = "carregando"
    estado.ficha = FichaAnuncio()
    estado.id_pedido = 0
    estado.mensagem_erro = ""


class FichaAnuncioState(rx.State):
    """Página /meus-anuncios/<id>: ficha do próprio anúncio. Só leitura: sem edição nem exclusão."""

    situacao: str = "carregando"  # "carregando", "ficha", "nao_encontrado", "restrito" ou "erro"
    ficha: FichaAnuncio = FichaAnuncio()
    id_pedido: int = 0  # 0 enquanto o identificador for inválido
    mensagem_erro: str = ""

    @rx.event
    def limpar(self):
        """Apaga a ficha (saída da conta)."""
        _zerar_ficha(self)

    @rx.event
    async def abrir(self):
        """on_load e "Tentar novamente": identificador inválido nem chega ao backend."""
        _zerar_ficha(self)
        identificador = ler_id_anuncio(_id_da_rota_anuncio(self.router.page.params, self.router.page.raw_path))
        if identificador is None:
            self.situacao = "nao_encontrado"
            return
        self.id_pedido = identificador
        yield
        rota = f"{ROTA_MEUS_ANUNCIOS}/{identificador}"
        auth = await self.get_state(AuthState)
        redirecionar = await auth._exigir(rota, None)
        if redirecionar is not None:
            yield redirecionar
            return
        if auth.situacao_protegida != "ok":
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_ANUNCIO
            return
        status, corpo = await chamar_xano("GET", f"{anuncios_api_url()}/anuncios/{identificador}", auth.token)
        if self.id_pedido != identificador:
            return  # já abriu outro anúncio
        if status == 401:
            yield _sessao_expirada(auth, rota)
            return
        if status == 403:
            self.situacao = "restrito"
            return
        if status == 404:
            # Mesma resposta para anúncio de outra conta, veículo da equipe e identificador inexistente.
            self.situacao = "nao_encontrado"
            return
        if status != 200:
            self.situacao = "erro"
            self.mensagem_erro = mensagem_erro_anuncio(status, corpo)
            return
        ficha = preparar_ficha(corpo)
        if ficha is None or ficha.id != identificador:
            print(f"Resposta inesperada para o anúncio {identificador}")
            self.situacao = "erro"
            self.mensagem_erro = ERRO_GENERICO_ANUNCIO
            return
        self.ficha = ficha
        self.situacao = "ficha"
