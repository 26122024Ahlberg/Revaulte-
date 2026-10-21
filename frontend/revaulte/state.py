# Estado do catálogo: requisição ao Xano e preparação dos cartões (tarefas 8.2 a 8.5).
import dataclasses
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from urllib.parse import urlparse

import httpx
import reflex as rx

from .config import catalog_api_url

# Imagem provisória exibida quando o veículo não tem capa ou a capa falha ao carregar.
IMAGEM_PROVISORIA = "/placeholder.svg"

# Tempo máximo de espera pela resposta do Xano.
TEMPO_LIMITE_SEGUNDOS = 10


def endereco_capa(url: object) -> str:
    """Retorna o endereço da capa, ou a imagem provisória se não for http/https."""
    if not isinstance(url, str) or not url.strip():
        return IMAGEM_PROVISORIA
    url = url.strip()
    partes = urlparse(url)
    if partes.scheme not in ("http", "https") or not partes.netloc:
        return IMAGEM_PROVISORIA
    return url


@dataclasses.dataclass
class CartaoVeiculo:
    """Dados de exibição de um cartão, já formatados como texto."""

    id: int  # identificador do veículo no Xano
    titulo: str  # marca, modelo e versão (quando houver)
    ano: str
    quilometragem: str  # por exemplo, "72.000 km"
    condicao: str  # "Novo" ou "Usado"
    preco: str  # por exemplo, "R$ 118.900,00"
    usado: bool
    modificado: bool
    vendido: bool
    capa: str  # endereço já preparado por endereco_capa


ROTULOS_CONDICAO = {"new": "Novo", "used": "Usado"}


def _numero(valor: object, campo: str) -> Decimal:
    # bool é subclasse de int em Python e não é um número válido aqui.
    if isinstance(valor, bool) or not isinstance(valor, (int, float, str)):
        raise ValueError(f"Campo {campo} inválido: {valor!r}")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"Campo {campo} inválido: {valor!r}") from None
    if not numero.is_finite():
        raise ValueError(f"Campo {campo} inválido: {valor!r}")
    return numero


def _milhar(texto_en: str) -> str:
    """Troca os separadores do formato "1,234.56" para o padrão brasileiro "1.234,56"."""
    return texto_en.replace(",", "_").replace(".", ",").replace("_", ".")


def formatar_preco(valor: object) -> str:
    """118900 -> "R$ 118.900,00", sem depender da localidade do sistema."""
    preco = _numero(valor, "price").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "R$ " + _milhar(f"{preco:,.2f}")


def formatar_quilometragem(valor: object) -> str:
    """72000 -> "72.000 km"."""
    km = _numero(valor, "mileage").quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return _milhar(f"{km:,}") + " km"


def formatar_titulo(veiculo: dict) -> str:
    """Marca, modelo e versão (quando houver), sem espaços sobrando."""
    partes = []
    for campo in ("brand", "model", "version"):
        valor = veiculo.get(campo)
        if isinstance(valor, str) and valor.strip():
            partes.append(" ".join(valor.split()))
    return " ".join(partes)


def preparar_cartao(veiculo: dict) -> CartaoVeiculo:
    """Converte um veículo da API em cartão; dados obrigatórios inválidos geram ValueError."""
    condicao = ROTULOS_CONDICAO.get(veiculo.get("condition"))
    if condicao is None:
        raise ValueError(f"Condição inválida: {veiculo.get('condition')!r}")
    ano = veiculo.get("year")
    if isinstance(ano, bool) or not isinstance(ano, int):
        raise ValueError(f"Ano inválido: {ano!r}")
    id_veiculo = veiculo.get("id")
    if isinstance(id_veiculo, bool) or not isinstance(id_veiculo, int):
        raise ValueError(f"Identificador inválido: {id_veiculo!r}")
    titulo = formatar_titulo(veiculo)
    if not titulo:
        raise ValueError("Veículo sem marca e modelo")
    return CartaoVeiculo(
        id=id_veiculo,
        titulo=titulo,
        ano=str(ano),
        quilometragem=formatar_quilometragem(veiculo.get("mileage")),
        condicao=condicao,
        usado=veiculo.get("condition") == "used",
        preco=formatar_preco(veiculo.get("price")),
        modificado=veiculo.get("is_modified") is True,
        vendido=veiculo.get("status") == "sold",
        capa=endereco_capa(veiculo.get("cover_image_url")),
    )


# Recortes fixos das páginas: estoque (/estoque, /usados e /modificados) e destaques da Home.
RECORTES = ("todos", "usados", "modificados", "destaques")

# Quantidade de veículos em destaque na página inicial.
QUANTIDADE_DESTAQUES = 3


def aplicar_recorte(cartoes: list[CartaoVeiculo], recorte: str) -> list[CartaoVeiculo]:
    """Cartões exibidos em cada página; recorte desconhecido equivale a "todos"."""
    if recorte == "usados":
        return [c for c in cartoes if c.usado]
    if recorte == "modificados":
        return [c for c in cartoes if c.modificado]
    if recorte == "destaques":
        # A lista já vem do mais recente para o mais antigo; vendidos não são destaque.
        return [c for c in cartoes if not c.vendido][:QUANTIDADE_DESTAQUES]
    return list(cartoes)


class CatalogState(rx.State):
    """Lista de cartões do catálogo e situação do carregamento."""

    # "carregando", "lista", "vazio" ou "erro".
    situacao: str = "carregando"
    # Lista completa recebida do Xano; a página exibe somente o recorte atual.
    cartoes: list[CartaoVeiculo] = []
    recorte: str = "todos"

    @rx.var
    def cartoes_exibidos(self) -> list[CartaoVeiculo]:
        return aplicar_recorte(self.cartoes, self.recorte)

    @rx.event
    def abrir_pagina(self, recorte: str):
        """on_load das páginas de estoque: define o recorte e carrega a lista.

        A lista anterior é descartada já aqui, para que cartões de outra página não
        apareçam com o novo recorte enquanto a carga não começa.
        """
        self.recorte = recorte if recorte in RECORTES else "todos"
        self.situacao = "carregando"
        self.cartoes = []
        return CatalogState.carregar_catalogo

    @rx.event
    async def carregar_catalogo(self):
        """Busca os veículos no Xano; disparado ao abrir a página e por "Tentar novamente"."""
        self.situacao = "carregando"
        self.cartoes = []
        yield  # envia o estado "carregando" ao navegador antes da requisição

        try:
            async with httpx.AsyncClient(timeout=TEMPO_LIMITE_SEGUNDOS) as cliente:
                resposta = await cliente.get(
                    f"{catalog_api_url()}/vehicles", headers={"Accept": "application/json"}
                )
            resposta.raise_for_status()
            dados = resposta.json()
            if not isinstance(dados, list) or not all(isinstance(v, dict) for v in dados):
                raise ValueError("Resposta inesperada do catálogo")
            cartoes = [preparar_cartao(v) for v in dados]
        except (httpx.HTTPError, ValueError) as erro:
            # Falha de rede, tempo esgotado, status HTTP de erro ou corpo inválido.
            print(f"Falha ao carregar o catálogo: {erro!r}")
            self.cartoes = []
            self.situacao = "erro"
            return

        self.cartoes = cartoes
        self.situacao = "lista" if cartoes else "vazio"

    @rx.event
    def usar_imagem_provisoria(self, id_veiculo: int, capa: str):
        """Troca a capa que falhou ao carregar pela imagem provisória.

        O cartão é localizado pelo identificador do veículo, e a capa é conferida para
        ignorar um erro atrasado de uma lista já recarregada.
        """
        cartoes = [
            dataclasses.replace(c, capa=IMAGEM_PROVISORIA)
            if c.id == id_veiculo and c.capa == capa
            else c
            for c in self.cartoes
        ]
        if cartoes != self.cartoes:
            self.cartoes = cartoes


# ---------------------------------------------------------------------------
# Página individual do veículo (Change detalhes-veiculo, etapa A).
# Usa a listagem pública GET /vehicles, que já contém somente Disponíveis e Vendidos;
# veículos em Rascunho nunca chegam aqui. Na etapa B, só buscar_veiculo muda.
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class DetalheVeiculo:
    """Dados de exibição da página do veículo, já formatados como texto."""

    id: int = 0
    titulo: str = ""
    marca: str = ""
    modelo: str = ""
    versao: str = ""  # vazio quando não cadastrada
    ano: str = ""
    quilometragem: str = ""
    condicao: str = ""
    preco: str = ""
    modificado: bool = False
    vendido: bool = False
    capa: str = IMAGEM_PROVISORIA


def _texto(valor: object) -> str:
    return " ".join(valor.split()) if isinstance(valor, str) else ""


def preparar_detalhe(veiculo: dict) -> DetalheVeiculo:
    """Converte um veículo da API nos dados da página; reutiliza a validação do cartão."""
    cartao = preparar_cartao(veiculo)
    return DetalheVeiculo(
        id=cartao.id,
        titulo=cartao.titulo,
        marca=_texto(veiculo.get("brand")),
        modelo=_texto(veiculo.get("model")),
        versao=_texto(veiculo.get("version")),
        ano=cartao.ano,
        quilometragem=cartao.quilometragem,
        condicao=cartao.condicao,
        preco=cartao.preco,
        modificado=cartao.modificado,
        vendido=cartao.vendido,
        capa=cartao.capa,
    )


# Limite de dígitos aceitos no identificador da rota (evita números absurdos).
MAX_DIGITOS_ID = 12


def ler_id_veiculo(texto: object) -> int | None:
    """Identificador da rota como inteiro positivo; qualquer outro valor resulta em None."""
    if not isinstance(texto, str):
        return None
    texto = texto.strip()
    if not texto.isascii() or not texto.isdigit() or len(texto) > MAX_DIGITOS_ID:
        return None
    numero = int(texto)
    return numero if numero > 0 else None


async def buscar_veiculo(id_veiculo: int) -> tuple[str, DetalheVeiculo | None]:
    """Busca um veículo publicado pelo identificador.

    Retorna ("encontrado", detalhe), ("nao_encontrado", None) ou ("erro", None).
    """
    try:
        async with httpx.AsyncClient(timeout=TEMPO_LIMITE_SEGUNDOS) as cliente:
            resposta = await cliente.get(
                f"{catalog_api_url()}/vehicles", headers={"Accept": "application/json"}
            )
        resposta.raise_for_status()
        dados = resposta.json()
        if not isinstance(dados, list) or not all(isinstance(v, dict) for v in dados):
            raise ValueError("Resposta inesperada do catálogo")
        for veiculo in dados:
            if veiculo.get("id") == id_veiculo and not isinstance(veiculo.get("id"), bool):
                return "encontrado", preparar_detalhe(veiculo)
    except (httpx.HTTPError, ValueError) as erro:
        print(f"Falha ao carregar o veículo {id_veiculo}: {erro!r}")
        return "erro", None
    return "nao_encontrado", None


def _id_da_rota(params: object, caminho: object) -> str:
    """Texto do identificador: parâmetro da rota dinâmica ou, na falta dele, o fim do caminho."""
    if isinstance(params, dict):
        valor = params.get("veiculo_id")
        if isinstance(valor, str):
            return valor
    if isinstance(caminho, str) and caminho.startswith("/veiculo/"):
        return caminho.split("?")[0].rstrip("/").rsplit("/", 1)[-1]
    return ""


class DetalheState(rx.State):
    """Página /veiculo/<id>: veículo exibido e situação do carregamento."""

    # "carregando", "encontrado", "nao_encontrado" ou "erro".
    situacao: str = "carregando"
    veiculo: DetalheVeiculo = DetalheVeiculo()
    # Identificador pedido pela rota; None quando inválido.
    id_pedido: int | None = None
    interesse_aberto: bool = False

    @rx.event
    def abrir(self):
        """on_load da página: lê o identificador da rota e carrega o veículo."""
        self.veiculo = DetalheVeiculo()
        self.interesse_aberto = False
        self.id_pedido = ler_id_veiculo(
            _id_da_rota(self.router.page.params, self.router.page.raw_path)
        )
        if self.id_pedido is None:
            self.situacao = "nao_encontrado"
            return
        self.situacao = "carregando"
        return DetalheState.carregar

    @rx.event
    async def carregar(self):
        """Busca o veículo; disparado ao abrir a página e por "Tentar novamente"."""
        id_veiculo = self.id_pedido
        if id_veiculo is None:
            self.situacao = "nao_encontrado"
            return
        self.situacao = "carregando"
        yield
        situacao, detalhe = await buscar_veiculo(id_veiculo)
        if self.id_pedido != id_veiculo:
            return  # o visitante já abriu outro veículo
        self.veiculo = detalhe if detalhe is not None else DetalheVeiculo()
        self.situacao = situacao

    @rx.event
    def usar_imagem_provisoria(self, capa: str):
        if self.veiculo.capa == capa:
            self.veiculo = dataclasses.replace(self.veiculo, capa=IMAGEM_PROVISORIA)

    @rx.event
    def mostrar_interesse(self):
        self.interesse_aberto = True


# Quantidade de slides do carrossel da página inicial (ver SLIDES_CARROSSEL em components.py).
TOTAL_SLIDES = 3


class CarrosselState(rx.State):
    """Slide visível no carrossel da página inicial; troca somente por ação do visitante."""

    indice: int = 0

    @rx.event
    def proximo(self):
        self.indice = (self.indice + 1) % TOTAL_SLIDES

    @rx.event
    def anterior(self):
        self.indice = (self.indice - 1) % TOTAL_SLIDES

    @rx.event
    def ir_para(self, indice: int):
        if isinstance(indice, int) and 0 <= indice < TOTAL_SLIDES:
            self.indice = indice

    @rx.event
    def reiniciar(self):
        self.indice = 0


class MenuState(rx.State):
    """Menu recolhível das telas estreitas."""

    menu_aberto: bool = False

    @rx.event
    def alternar_menu(self):
        self.menu_aberto = not self.menu_aberto

    @rx.event
    def fechar_menu(self):
        self.menu_aberto = False
