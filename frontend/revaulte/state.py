# Estado do catálogo: requisição ao Xano e preparação dos cartões (tarefas 8.2 a 8.5).
import dataclasses
import re
import unicodedata
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from urllib.parse import quote, urlparse

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


# ---------------------------------------------------------------------------
# Pesquisa e filtros do estoque (Change pesquisa-filtros-catalogo).
# Aplicados sobre a lista já recebida; nenhuma nova consulta ao backend.
# ---------------------------------------------------------------------------

FILTROS_CONDICAO = ("todos", "novo", "usado")
FILTROS_MODIFICACAO = ("todos", "modificados", "originais")


def normalizar_texto(texto: object) -> str:
    """Minúsculas, sem acentos e com espaços simples: "  Citroën  C4 " -> "citroen c4"."""
    if not isinstance(texto, str):
        return ""
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.casefold().split())


def filtrar_cartoes(
    cartoes: list[CartaoVeiculo], busca: str, condicao: str, modificacao: str
) -> list[CartaoVeiculo]:
    """Cartões que atendem à pesquisa e aos dois filtros ao mesmo tempo."""
    termo = normalizar_texto(busca)
    resultado = []
    for c in cartoes:
        if termo and termo not in normalizar_texto(c.titulo):
            continue
        if condicao == "novo" and c.usado or condicao == "usado" and not c.usado:
            continue
        if modificacao == "modificados" and not c.modificado:
            continue
        if modificacao == "originais" and c.modificado:
            continue
        resultado.append(c)
    return resultado


class CatalogState(rx.State):
    """Lista de cartões do catálogo e situação do carregamento."""

    # "carregando", "lista", "vazio" ou "erro".
    situacao: str = "carregando"
    # Lista completa recebida do Xano; a página exibe somente o recorte atual.
    cartoes: list[CartaoVeiculo] = []
    recorte: str = "todos"
    # Pesquisa e filtros escolhidos pelo visitante.
    busca: str = ""
    filtro_condicao: str = "todos"
    filtro_modificacao: str = "todos"

    @rx.var
    def cartoes_exibidos(self) -> list[CartaoVeiculo]:
        return filtrar_cartoes(
            aplicar_recorte(self.cartoes, self.recorte),
            self.busca,
            self.filtro_condicao,
            self.filtro_modificacao,
        )

    @rx.var
    def filtros_ativos(self) -> bool:
        return bool(normalizar_texto(self.busca)) or (
            self.filtro_condicao != "todos" or self.filtro_modificacao != "todos"
        )

    @rx.var
    def total_exibido(self) -> str:
        total = len(self.cartoes_exibidos)
        return "1 veículo" if total == 1 else f"{total} veículos"

    @rx.event
    def definir_busca(self, texto: str):
        self.busca = texto if isinstance(texto, str) else ""

    @rx.event
    def definir_condicao(self, valor: str):
        self.filtro_condicao = valor if valor in FILTROS_CONDICAO else "todos"

    @rx.event
    def definir_modificacao(self, valor: str):
        self.filtro_modificacao = valor if valor in FILTROS_MODIFICACAO else "todos"

    @rx.event
    def limpar_filtros(self):
        self.busca = ""
        self.filtro_condicao = "todos"
        self.filtro_modificacao = "todos"

    @rx.event
    def abrir_pagina(self, recorte: str):
        """on_load das páginas de estoque: define o recorte e carrega a lista.

        A lista anterior é descartada já aqui, para que cartões de outra página não
        apareçam com o novo recorte enquanto a carga não começa.
        """
        self.recorte = recorte if recorte in RECORTES else "todos"
        # Um filtro de outra página não pode esconder veículos nesta.
        self.busca = ""
        self.filtro_condicao = "todos"
        self.filtro_modificacao = "todos"
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
# Página individual do veículo (Change detalhes-veiculo).
# Usa o endpoint público GET /vehicles/{vehicle_id}, que só devolve Disponíveis e
# Vendidos e responde 404 para Rascunho e inexistente: Rascunho nunca chega aqui.
# ---------------------------------------------------------------------------

# Áreas de modificação do backend, na ordem e com os nomes de docs/domain-model.md (seção 8).
ROTULOS_AREA = {
    "engine": "Preparação do motor",
    "forced_induction": "Turbo/sobrealimentação",
    "power": "Potência",
    "fuel": "Combustível",
    "transmission": "Alterações de câmbio",
    "suspension": "Suspensão",
    "wheels_tires": "Rodas e pneus",
    "brakes": "Freios",
    "interior": "Interior",
    "exterior": "Modificações estéticas",
    "other": "Outras modificações",
}


@dataclasses.dataclass
class GrupoModificacoes:
    """Modificações cadastradas de uma área, já com o rótulo em português."""

    area: str = ""
    itens: list[str] = dataclasses.field(default_factory=list)


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
    preco_numero: str = "0"  # preço como texto decimal ("189900.00"), usado pelo simulador
    modificado: bool = False
    vendido: bool = False
    capa: str = IMAGEM_PROVISORIA
    # Configuração original e descrição; vazio quando não cadastrado.
    cor: str = ""
    motorizacao: str = ""
    cambio: str = ""
    descricao: str = ""
    # Modificações cadastradas, agrupadas por área; vazio quando não há registros.
    modificacoes: list[GrupoModificacoes] = dataclasses.field(default_factory=list)
    # Anunciante (Change contato-vendedor): nome de exibição e link do WhatsApp.
    # Vazios quando não há anunciante, autorização ou número válido, ou o veículo foi vendido.
    anunciante: str = ""
    link_whatsapp: str = ""


def _texto(valor: object) -> str:
    return " ".join(valor.split()) if isinstance(valor, str) else ""


def _texto_longo(valor: object) -> str:
    """Texto com parágrafos: mantém as quebras de linha, sem espaços nem linhas vazias sobrando."""
    if not isinstance(valor, str):
        return ""
    linhas = [" ".join(linha.split()) for linha in valor.strip().splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(linhas)).strip()


def agrupar_modificacoes(registros: object) -> list[GrupoModificacoes]:
    """Agrupa as modificações por área, na ordem do domínio e na ordem de cadastro.

    Registros sem descrição são ignorados (nada é exibido sem conteúdo cadastrado);
    uma área desconhecida vai para "Outras modificações". Ausência equivale a lista vazia.
    """
    if registros is None:
        return []
    if not isinstance(registros, list) or not all(isinstance(r, dict) for r in registros):
        raise ValueError(f"Modificações inválidas: {registros!r}")
    por_area: dict[str, list[str]] = {}
    for registro in registros:
        descricao = _texto_longo(registro.get("description"))
        if not descricao:
            continue
        area = registro.get("area")
        chave = area if isinstance(area, str) and area in ROTULOS_AREA else "other"
        por_area.setdefault(chave, []).append(descricao)
    return [
        GrupoModificacoes(area=rotulo, itens=por_area[chave])
        for chave, rotulo in ROTULOS_AREA.items()
        if chave in por_area
    ]


# WhatsApp: somente dígitos, com DDI e DDD (por exemplo, 55 + DDD + número = 12 ou 13 dígitos).
_NUMERO_WHATSAPP = re.compile(r"[0-9]{12,13}")  # só ASCII: \d aceitaria outros numerais


def mensagem_whatsapp(titulo: str, ano: str) -> str:
    """Mensagem inicial que identifica o veículo; sem endereço enquanto não houver domínio público."""
    return f"Olá! Tenho interesse no {titulo} {ano} anunciado na Revaulte."


def link_whatsapp(numero: object, titulo: str, ano: str) -> str:
    """Link wa.me com a mensagem codificada, ou vazio se o número não for válido."""
    if not isinstance(numero, str) or not _NUMERO_WHATSAPP.fullmatch(numero):
        return ""
    return f"https://wa.me/{numero}?text={quote(mensagem_whatsapp(titulo, ano), safe='')}"


def preparar_anunciante(seller: object, titulo: str, ano: str, vendido: bool) -> tuple[str, str]:
    """(nome, link do WhatsApp) do anunciante; ("", "") quando não há o que exibir.

    O backend só envia o número com autorização e só para veículo Disponível; a página
    confere de novo: vendido nunca recebe contato e sem nome não há anunciante a exibir.
    """
    if seller is None or vendido:
        return "", ""
    if not isinstance(seller, dict):
        raise ValueError(f"Anunciante inválido: {seller!r}")
    nome = _texto(seller.get("display_name"))
    if not nome:
        return "", ""
    return nome, link_whatsapp(seller.get("whatsapp"), titulo, ano)


def preparar_detalhe(veiculo: dict) -> DetalheVeiculo:
    """Converte um veículo da API nos dados da página; reutiliza a validação do cartão."""
    cartao = preparar_cartao(veiculo)
    anunciante, link = preparar_anunciante(
        veiculo.get("seller"), cartao.titulo, cartao.ano, cartao.vendido
    )
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
        preco_numero=str(_numero(veiculo.get("price"), "price").quantize(Decimal("0.01"))),
        modificado=cartao.modificado,
        vendido=cartao.vendido,
        capa=cartao.capa,
        cor=_texto(veiculo.get("color")),
        motorizacao=_texto(veiculo.get("engine")),
        cambio=_texto(veiculo.get("transmission")),
        descricao=_texto_longo(veiculo.get("description")),
        modificacoes=agrupar_modificacoes(veiculo.get("modifications")),
        anunciante=anunciante,
        link_whatsapp=link,
    )


# ---------------------------------------------------------------------------
# Simulador de financiamento (Change simulador-financiamento).
# Estimativa hipotética pela Tabela Price; nada é enviado a terceiros.
# ---------------------------------------------------------------------------

OPCOES_PARCELAS = (12, 24, 36, 48, 60)
PARCELAS_INICIAIS = 48
ENTRADA_INICIAL = Decimal("0.20")  # 20% do preço
TAXA_INICIAL = "1,50"  # % ao mês, ilustrativa
TAXA_MAXIMA = Decimal("5")
CENTAVO = Decimal("0.01")

_MILHAR_SEM_DECIMAL = re.compile(r"\d{1,3}(\.\d{3})+")
_NUMERO = re.compile(r"-?\d+(\.\d+)?")


def ler_valor_br(texto: object) -> Decimal | None:
    """Lê um número digitado no formato brasileiro ("20.000,50", "1,5", "R$ 20000").

    Retorna None quando o texto não é um número.
    """
    if not isinstance(texto, str):
        return None
    t = texto.replace("R$", "").replace(" ", "").replace("\u00a0", "").replace("%", "")
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif _MILHAR_SEM_DECIMAL.fullmatch(t.lstrip("-")):
        t = t.replace(".", "")  # "20.000" é vinte mil
    if not _NUMERO.fullmatch(t):
        return None
    return Decimal(t)


def _casas_decimais(numero: Decimal) -> int:
    expoente = numero.as_tuple().exponent
    return -expoente if isinstance(expoente, int) and expoente < 0 else 0


def texto_valor_br(valor: Decimal) -> str:
    """Valor para um campo de texto: 37980 -> "37.980,00"."""
    return _milhar(f"{valor.quantize(CENTAVO, rounding=ROUND_HALF_UP):,.2f}")


def _reais(valor: Decimal) -> str:
    return "R$ " + texto_valor_br(valor)


def calcular_financiamento(
    preco: Decimal, entrada: Decimal, parcelas: int, taxa_percentual: Decimal
) -> dict[str, Decimal]:
    """Tabela Price: parcela = F·i / (1 − (1 + i)^−n); com taxa zero, F / n.

    A parcela é arredondada ao centavo, e o total pago e os juros partem dela,
    para que os números exibidos fechem entre si.
    """
    financiado = preco - entrada
    i = taxa_percentual / 100
    if i == 0:
        parcela = financiado / parcelas
    else:
        parcela = financiado * i / (1 - (1 + i) ** -parcelas)
    parcela = parcela.quantize(CENTAVO, rounding=ROUND_HALF_UP)
    total = entrada + parcela * parcelas
    return {"financiado": financiado, "parcela": parcela, "total": total, "juros": total - preco}


@dataclasses.dataclass
class Simulacao:
    """Resultado exibido pelo simulador: valores formatados ou a mensagem de erro."""

    erro: str = ""
    entrada: str = ""
    financiado: str = ""
    parcela: str = ""
    total: str = ""
    juros: str = ""


def simular(preco_texto: str, entrada_texto: str, parcelas: int, taxa_texto: str) -> Simulacao:
    """Valida o que o visitante digitou e calcula a estimativa."""
    try:
        preco = Decimal(preco_texto)
    except (InvalidOperation, TypeError):
        return Simulacao(erro="Valor do veículo indisponível para simulação.")
    if not preco.is_finite() or preco <= 0:
        return Simulacao(erro="Valor do veículo indisponível para simulação.")

    entrada = ler_valor_br(entrada_texto)
    if entrada is None:
        return Simulacao(erro="Informe a entrada em reais, por exemplo 20.000,00.")
    if entrada < 0:
        return Simulacao(erro="A entrada não pode ser negativa.")
    if _casas_decimais(entrada) > 2:
        return Simulacao(erro="Use no máximo duas casas decimais na entrada.")
    if entrada >= preco:
        return Simulacao(erro="A entrada deve ser menor que o valor do veículo.")

    if parcelas not in OPCOES_PARCELAS:
        return Simulacao(erro="Escolha um prazo entre 12 e 60 parcelas.")

    taxa = ler_valor_br(taxa_texto)
    if taxa is None or taxa < 0 or taxa > TAXA_MAXIMA or _casas_decimais(taxa) > 2:
        return Simulacao(erro="Informe uma taxa entre 0% e 5% ao mês, com até duas casas decimais.")

    r = calcular_financiamento(preco, entrada, parcelas, taxa)
    return Simulacao(
        entrada=_reais(entrada),
        financiado=_reais(r["financiado"]),
        parcela=_reais(r["parcela"]),
        total=_reais(r["total"]),
        juros=_reais(r["juros"]),
    )


def entrada_inicial(preco_texto: str) -> str:
    """20% do preço, arredondado a reais, no formato do campo."""
    try:
        preco = Decimal(preco_texto)
    except (InvalidOperation, TypeError):
        return ""
    return texto_valor_br((preco * ENTRADA_INICIAL).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


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

    Retorna ("encontrado", detalhe), ("nao_encontrado", None) para a resposta 404
    (Rascunho ou inexistente) ou ("erro", None) para qualquer outra falha.
    """
    try:
        async with httpx.AsyncClient(timeout=TEMPO_LIMITE_SEGUNDOS) as cliente:
            resposta = await cliente.get(
                f"{catalog_api_url()}/vehicles/{id_veiculo}",
                headers={"Accept": "application/json"},
            )
        if resposta.status_code == 404:
            return "nao_encontrado", None
        resposta.raise_for_status()
        dados = resposta.json()
        if not isinstance(dados, dict):
            raise ValueError("Resposta inesperada do detalhe")
        id_recebido = dados.get("id")
        if isinstance(id_recebido, bool) or id_recebido != id_veiculo:
            raise ValueError(f"Veículo {id_recebido!r} recebido no lugar de {id_veiculo}")
        return "encontrado", preparar_detalhe(dados)
    except (httpx.HTTPError, ValueError) as erro:
        print(f"Falha ao carregar o veículo {id_veiculo}: {erro!r}")
        return "erro", None


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
    # Simulador: textos como o visitante digitou e o prazo escolhido.
    entrada_texto: str = ""
    taxa_texto: str = TAXA_INICIAL
    parcelas: int = PARCELAS_INICIAIS

    def _reiniciar_simulador(self):
        self.entrada_texto = entrada_inicial(self.veiculo.preco_numero)
        self.taxa_texto = TAXA_INICIAL
        self.parcelas = PARCELAS_INICIAIS

    @rx.var
    def simulacao(self) -> Simulacao:
        return simular(self.veiculo.preco_numero, self.entrada_texto, self.parcelas, self.taxa_texto)

    @rx.event
    def definir_entrada(self, texto: str):
        self.entrada_texto = texto if isinstance(texto, str) else ""

    @rx.event
    def definir_taxa(self, texto: str):
        self.taxa_texto = texto if isinstance(texto, str) else ""

    @rx.event
    def definir_parcelas(self, parcelas: int):
        if isinstance(parcelas, int) and parcelas in OPCOES_PARCELAS:
            self.parcelas = parcelas

    @rx.event
    def abrir(self):
        """on_load da página: lê o identificador da rota e carrega o veículo."""
        self.veiculo = DetalheVeiculo()
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
        self._reiniciar_simulador()
        self.situacao = situacao

    @rx.event
    def usar_imagem_provisoria(self, capa: str):
        if self.veiculo.capa == capa:
            self.veiculo = dataclasses.replace(self.veiculo, capa=IMAGEM_PROVISORIA)


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
