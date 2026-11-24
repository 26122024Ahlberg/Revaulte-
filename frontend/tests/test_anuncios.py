# Testes da lógica de anúncios do frontend (Change anuncios-cliente, tarefas 4.1, 4.2 e 5.1).
# Dados simulados; nenhum teste acessa a rede.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import dataclasses
import os
import re
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from revaulte.anuncios import (
    ERRO_DADOS,
    ERRO_GENERICO_ANUNCIO,
    ERRO_LIMITE_RASCUNHOS,
    ERRO_MUITAS_TENTATIVAS,
    ERRO_NAO_ENCONTRADO,
    ERRO_RESTRITO,
    ERRO_SESSAO,
    MENSAGENS_VALIDACAO,
    ROTULOS_ESTADO,
    FichaAnuncio,
    ResumoAnuncio,
    ler_ano,
    ler_id_anuncio,
    ler_preco,
    ler_quilometragem,
    mensagem_erro_anuncio,
    preparar_ficha,
    preparar_lista,
    situacao_da_resposta,
    validar_anuncio,
)
from revaulte.config import ANUNCIOS_API_URL_PADRAO, anuncios_api_url

HOJE = date(2026, 11, 23)
POST_XS = Path(__file__).resolve().parents[2] / "xano" / "api" / "anuncios" / "anuncios_POST.xs"
# Nunca podem aparecer no que o frontend envia nem no que guarda para exibir.
CAMPOS_INTERNOS = {"status", "seller_id", "user_id", "id", "created_at", "cover_image_url", "whatsapp",
                   "contact_authorized", "email", "cpf", "phone", "birth_date", "address", "password"}


def formulario(**extra) -> dict:
    base = {
        "nome_exibicao": "  Garagem   de Teste ", "marca": " Ford ", "modelo": "Maverick", "versao": "GT",
        "ano": "1975", "condicao": "used", "quilometragem": "120.000", "preco": "45.000,00",
        "modificado": "nao", "cor": "Vermelho", "motorizacao": "V8 302", "cambio": "Manual",
        "descricao": "  Primeira linha\nSegunda linha  ",
    }
    base.update(extra)
    return base


def item(**extra) -> dict:
    base = {
        "id": 7, "brand": "Revaulte Teste", "model": "Anuncio controlado A", "version": None, "year": 1975,
        "condition": "used", "mileage": 120000, "price": 45000, "is_modified": False, "status": "draft",
        "created_at": 1795456668473, "color": "", "engine": None, "transmission": None,
        "description": "Teste.",
    }
    base.update(extra)
    return base


class TestConfiguracao(unittest.TestCase):
    def test_endereco_padrao(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("REVAULTE_ANUNCIOS_API_URL", None)
            self.assertEqual(anuncios_api_url(), "https://x8ki-letl-twmt.n7.xano.io/api:revaulte-anuncios")
        self.assertEqual(ANUNCIOS_API_URL_PADRAO, "https://x8ki-letl-twmt.n7.xano.io/api:revaulte-anuncios")

    def test_variavel_de_ambiente_substitui(self):
        with patch.dict(os.environ, {"REVAULTE_ANUNCIOS_API_URL": " https://exemplo.invalido/api:x/ "}):
            self.assertEqual(anuncios_api_url(), "https://exemplo.invalido/api:x")

    def test_variavel_vazia_usa_padrao(self):
        with patch.dict(os.environ, {"REVAULTE_ANUNCIOS_API_URL": "   "}):
            self.assertEqual(anuncios_api_url(), ANUNCIOS_API_URL_PADRAO)


class TestLeituraDosCampos(unittest.TestCase):
    def test_ano(self):
        for texto, esperado in (
            ("1886", 1886), ("1975", 1975), (" 2027 ", 2027), ("1885", None), ("2028", None),
            ("75", None), ("19 75", None), ("1975.0", None), ("", None), (None, None), (1975, None),
        ):
            with self.subTest(texto=texto):
                self.assertEqual(ler_ano(texto, HOJE), esperado)

    def test_ano_maximo_acompanha_o_ano_atual(self):
        self.assertEqual(ler_ano("2031", date(2030, 1, 1)), 2031)
        self.assertIsNone(ler_ano("2032", date(2030, 1, 1)))

    def test_quilometragem(self):
        for texto, esperado in (
            ("0", 0), ("120000", 120000), ("120.000", 120000), ("120.000 km", 120000), ("2.000.000", 2000000),
            ("2000001", None), ("-1", None), ("1,5", None), ("12.5", None), ("1.20.000", None),
            ("", None), ("km", None), (None, None), (120000, None),
        ):
            with self.subTest(texto=texto):
                self.assertEqual(ler_quilometragem(texto), esperado)

    def test_preco(self):
        for texto, esperado in (
            ("45.000,00", Decimal("45000.00")), ("R$ 45000", Decimal("45000")), ("0,01", Decimal("0.01")),
            ("100.000.000,00", Decimal("100000000.00")), ("0", None), ("-5", None), ("100.000.000,01", None),
            ("1,234", None), ("abc", None), ("", None), (None, None),
        ):
            with self.subTest(texto=texto):
                self.assertEqual(ler_preco(texto), esperado)

    def test_id_da_rota(self):
        for texto, esperado in (("7", 7), ("123456789012", 123456789012), ("0", None), ("07", None),
                                ("1234567890123", None), ("abc", None), ("-1", None), ("7/", None), (7, None)):
            with self.subTest(texto=texto):
                self.assertEqual(ler_id_anuncio(texto), esperado)


class TestValidacaoDoAnuncio(unittest.TestCase):
    def test_formulario_completo_do_primeiro_anuncio(self):
        payload, erro = validar_anuncio(formulario(), tem_anunciante=False, hoje=HOJE)
        self.assertEqual(erro, "")
        self.assertEqual(payload, {
            "display_name": "Garagem de Teste", "brand": "Ford", "model": "Maverick", "version": "GT",
            "year": 1975, "condition": "used", "mileage": 120000, "price": 45000.0, "is_modified": False,
            "color": "Vermelho", "engine": "V8 302", "transmission": "Manual",
            "description": "Primeira linha\nSegunda linha",
        })

    def test_somente_obrigatorios(self):
        dados = formulario(versao="", cor=" ", motorizacao="", cambio="", descricao="")
        payload, _ = validar_anuncio(dados, tem_anunciante=True, hoje=HOJE)
        self.assertEqual(set(payload), {"brand", "model", "year", "condition", "mileage", "price", "is_modified"})

    def test_regressao_false_e_zero_sao_validos(self):
        # Mesmo defeito corrigido no backend em 23/11/2026: false e 0 não podem ser tratados como ausentes.
        payload, erro = validar_anuncio(formulario(modificado="nao", quilometragem="0"), True, HOJE)
        self.assertEqual(erro, "")
        self.assertIs(payload["is_modified"], False)
        self.assertEqual(payload["mileage"], 0)
        payload, _ = validar_anuncio(formulario(modificado="sim", condicao="new"), True, HOJE)
        self.assertIs(payload["is_modified"], True)
        self.assertEqual(payload["condition"], "new")

    def test_nome_de_exibicao_so_no_primeiro_anuncio(self):
        payload, _ = validar_anuncio(formulario(nome_exibicao="Outro nome"), tem_anunciante=True, hoje=HOJE)
        self.assertNotIn("display_name", payload)
        _, erro = validar_anuncio(formulario(nome_exibicao=" A "), tem_anunciante=False, hoje=HOJE)
        self.assertEqual(erro, MENSAGENS_VALIDACAO["invalid_display_name"])
        payload, erro = validar_anuncio(formulario(nome_exibicao=""), tem_anunciante=True, hoje=HOJE)
        self.assertEqual(erro, "")

    def test_limites_de_texto(self):
        for campo, maximo, codigo in (
            ("nome_exibicao", 60, "invalid_display_name"), ("marca", 40, "invalid_brand"),
            ("modelo", 60, "invalid_model"), ("versao", 80, "invalid_version"), ("cor", 60, "invalid_color"),
            ("motorizacao", 60, "invalid_engine"), ("cambio", 60, "invalid_transmission"),
            ("descricao", 2000, "invalid_description"),
        ):
            with self.subTest(campo=campo):
                _, erro = validar_anuncio(formulario(**{campo: "x" * maximo}), False, HOJE)
                self.assertEqual(erro, "")
                _, erro = validar_anuncio(formulario(**{campo: "x" * (maximo + 1)}), False, HOJE)
                self.assertEqual(erro, MENSAGENS_VALIDACAO[codigo])

    def test_obrigatorios_ausentes(self):
        for campo, codigo in (
            ("marca", "invalid_brand"), ("modelo", "invalid_model"), ("ano", "invalid_year"),
            ("condicao", "invalid_condition"), ("quilometragem", "invalid_mileage"),
            ("preco", "invalid_price"), ("modificado", "invalid_is_modified"),
        ):
            for vazio in ("", "   ", None):
                with self.subTest(campo=campo, vazio=vazio):
                    payload, erro = validar_anuncio(formulario(**{campo: vazio}), True, HOJE)
                    self.assertIsNone(payload)
                    self.assertEqual(erro, MENSAGENS_VALIDACAO[codigo])

    def test_valores_fora_da_lista(self):
        for campo, valor, codigo in (
            ("condicao", "seminovo", "invalid_condition"), ("condicao", "NEW", "invalid_condition"),
            ("modificado", "true", "invalid_is_modified"), ("modificado", True, "invalid_is_modified"),
            ("preco", "0", "invalid_price"), ("quilometragem", "2.000.001", "invalid_mileage"),
            ("ano", "1885", "invalid_year"),
        ):
            with self.subTest(campo=campo, valor=valor):
                self.assertEqual(validar_anuncio(formulario(**{campo: valor}), True, HOJE)[1],
                                 MENSAGENS_VALIDACAO[codigo])

    def test_primeiro_problema_na_ordem_da_tela(self):
        _, erro = validar_anuncio(formulario(cor="x" * 61, ano="abc", marca=""), True, HOJE)
        self.assertEqual(erro, MENSAGENS_VALIDACAO["invalid_brand"])
        _, erro = validar_anuncio(formulario(cor="x" * 61, ano="abc"), True, HOJE)
        self.assertEqual(erro, MENSAGENS_VALIDACAO["invalid_year"])

    def test_campos_internos_nunca_enviados(self):
        # Mesmo que um formulário adulterado traga esses campos, eles não chegam ao backend.
        adulterado = formulario(status="available", seller_id=1, user_id=5, id=1, cover_image_url="x",
                                created_at=0, display_name="Outro")
        payload, _ = validar_anuncio(adulterado, tem_anunciante=True, hoje=HOJE)
        self.assertFalse(CAMPOS_INTERNOS & set(payload))
        self.assertNotIn("display_name", payload)

    def test_mensagens_cobrem_os_codigos_do_backend(self):
        # Cada invalid_* do endpoint publicado tem mensagem, e nenhuma mensagem é de código inexistente.
        codigos = set(re.findall(r'error = "(invalid_[a-z_]+)"', POST_XS.read_text(encoding="utf-8")))
        self.assertEqual(codigos, set(MENSAGENS_VALIDACAO))
        self.assertIn('error = "draft_limit_reached"', POST_XS.read_text(encoding="utf-8"))


class TestPreparacaoDaLista(unittest.TestCase):
    def test_lista_com_anunciante(self):
        nome, anuncios = preparar_lista({
            "anunciante": {"display_name": "Garagem A Teste", "seller_id": 2},
            "anuncios": [item(), item(id=8, status="available", version="GT", price=118900.5)],
        })
        self.assertEqual(nome, "Garagem A Teste")
        self.assertEqual(anuncios[0], ResumoAnuncio(
            id=7, titulo="Revaulte Teste Anuncio controlado A", ano="1975", preco="R$ 45.000,00",
            estado="draft", rotulo_estado="Rascunho — aguardando publicação", enviado_em="23/11/2026",
            endereco="/meus-anuncios/7",
        ))
        self.assertEqual(anuncios[1].titulo, "Revaulte Teste Anuncio controlado A GT")
        self.assertEqual(anuncios[1].rotulo_estado, "Publicado")
        self.assertEqual(anuncios[1].preco, "R$ 118.900,50")

    def test_conta_sem_anunciante(self):
        self.assertEqual(preparar_lista({"anunciante": None, "anuncios": []}), ("", []))

    def test_rotulos_de_estado(self):
        self.assertEqual(ROTULOS_ESTADO, {
            "draft": "Rascunho — aguardando publicação", "available": "Publicado", "sold": "Vendido",
        })

    def test_itens_malformados_descartados(self):
        _, anuncios = preparar_lista({"anunciante": None, "anuncios": [
            item(), item(id=0), item(id="8"), item(id=True), item(status="reserved"), item(price=None),
            "texto", None,
        ]})
        self.assertEqual([a.id for a in anuncios], [7])

    def test_resposta_inesperada(self):
        for corpo in (None, [], "erro", {"anuncios": None}, {"anunciante": None}, {"code": "x", "message": "y"}):
            with self.subTest(corpo=corpo):
                with self.assertRaises(ValueError):
                    preparar_lista(corpo)

    def test_campos_internos_descartados(self):
        # A lista do backend nunca deveria trazer esses campos; se trouxer, nada deles é guardado.
        _, anuncios = preparar_lista({"anunciante": None, "anuncios": [
            item(seller_id=2, user_id=3, whatsapp="11999999999", cover_image_url="https://x"),
        ]})
        guardado = dataclasses.asdict(anuncios[0])
        self.assertFalse({"seller_id", "user_id", "whatsapp", "cover_image_url"} & set(guardado))
        self.assertNotIn("11999999999", str(guardado))


class TestPreparacaoDaFicha(unittest.TestCase):
    def test_ficha_de_rascunho(self):
        ficha = preparar_ficha(item(color="Azul", engine="V8", description="  Linha 1\nLinha 2 "))
        self.assertIsInstance(ficha, FichaAnuncio)
        self.assertEqual((ficha.marca, ficha.modelo, ficha.versao), ("Revaulte Teste", "Anuncio controlado A", ""))
        self.assertEqual((ficha.condicao, ficha.quilometragem, ficha.modificado), ("Usado", "120.000 km", "Não"))
        self.assertEqual((ficha.cor, ficha.motorizacao, ficha.cambio), ("Azul", "V8", ""))
        self.assertEqual(ficha.descricao, "Linha 1\nLinha 2")
        self.assertEqual(ficha.rotulo_estado, "Rascunho — aguardando publicação")
        self.assertEqual(ficha.endereco_publico, "")

    def test_link_publico_so_para_publicado_ou_vendido(self):
        self.assertEqual(preparar_ficha(item(status="available")).endereco_publico, "/veiculo/7")
        self.assertEqual(preparar_ficha(item(status="sold")).endereco_publico, "/veiculo/7")
        self.assertEqual(preparar_ficha(item(status="draft")).endereco_publico, "")

    def test_modificado_e_condicao(self):
        self.assertEqual(preparar_ficha(item(is_modified=True, condition="new")).modificado, "Sim")
        self.assertEqual(preparar_ficha(item(is_modified=True, condition="new")).condicao, "Novo")
        self.assertEqual(preparar_ficha(item(is_modified=None)).modificado, "")
        self.assertEqual(preparar_ficha(item(mileage=0)).quilometragem, "0 km")

    def test_ficha_invalida(self):
        for corpo in (None, {}, item(id=None), item(status="x"), {"code": "ERROR_CODE_NOT_FOUND"}):
            with self.subTest(corpo=corpo):
                self.assertIsNone(preparar_ficha(corpo))


class TestTraducaoDeErros(unittest.TestCase):
    def test_codigos_de_validacao(self):
        for codigo, texto in MENSAGENS_VALIDACAO.items():
            with self.subTest(codigo=codigo):
                corpo = {"code": "ERROR_CODE_INPUT_ERROR", "message": codigo}
                self.assertEqual(mensagem_erro_anuncio(400, corpo), texto)

    def test_limite_de_rascunhos(self):
        corpo = {"code": "ERROR_CODE_INPUT_ERROR", "message": "draft_limit_reached"}
        self.assertEqual(mensagem_erro_anuncio(400, corpo), ERRO_LIMITE_RASCUNHOS)

    def test_status(self):
        for status, situacao, texto in (
            (400, "dados", ERRO_DADOS), (401, "sessao", ERRO_SESSAO), (403, "restrito", ERRO_RESTRITO),
            (404, "nao_encontrado", ERRO_NAO_ENCONTRADO), (429, "limite", ERRO_MUITAS_TENTATIVAS),
            (0, "erro", ERRO_GENERICO_ANUNCIO), (500, "erro", ERRO_GENERICO_ANUNCIO),
            (502, "erro", ERRO_GENERICO_ANUNCIO), (200, "ok", ERRO_GENERICO_ANUNCIO),
        ):
            with self.subTest(status=status):
                self.assertEqual(situacao_da_resposta(status), situacao)
                if status != 200:
                    self.assertEqual(mensagem_erro_anuncio(status, None), texto)

    def test_mensagem_do_backend_nunca_exibida_crua(self):
        # Códigos desconhecidos ou mensagens livres (por exemplo, de duplicidade) viram texto próprio.
        for status, mensagem in ((400, "Duplicate record detected"), (400, "invalid_cpf"),
                                 (500, "SQLSTATE[23505]: unique violation"), (403, "invalid_brand")):
            with self.subTest(mensagem=mensagem):
                texto = mensagem_erro_anuncio(status, {"message": mensagem})
                self.assertNotIn(mensagem, texto)


# ---------------------------------------------------------------------------
# Estados das páginas (tarefas 4.3 e 5.2) e páginas/menu (6.1 e 6.2), com respostas simuladas.
# ---------------------------------------------------------------------------
from unittest.mock import AsyncMock  # noqa: E402

import sys  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))  # funciona também fora do discover
from test_contas import EstadoSessaoFalso, destinos_redirect, nomes_de_eventos  # noqa: E402

TOKEN = "token-de-teste"
URL_ANUNCIOS = ANUNCIOS_API_URL_PADRAO + "/anuncios"
LISTA_COM_ANUNCIANTE = {"anunciante": {"display_name": "Garagem A Teste"}, "anuncios": [item()]}
LISTA_SEM_ANUNCIANTE = {"anunciante": None, "anuncios": []}


class AuthFalso:
    """Substitui o AuthState: `redirecionar` simula visitante ou sessão recusada; `situacao`, o resultado do auth/me."""

    def __init__(self, token=TOKEN, situacao="ok", redirecionar=None, nome="Cliente Demo"):
        from revaulte.auth import Usuario

        self.token = token
        self.situacao_protegida = "carregando"
        self.usuario = Usuario(id=3, nome=nome, email="cliente@exemplo.com", perfil="member")
        self._situacao = situacao
        self._redirecionar = redirecionar
        self.rotas_exigidas = []

    async def _exigir(self, rota, perfil):
        self.rotas_exigidas.append((rota, perfil))
        if self._redirecionar is not None:
            return self._redirecionar
        self.situacao_protegida = self._situacao
        return None

    def _encerrar(self):
        self.token = ""


class MeusFalso:
    """Substitui o MeusAnunciosState."""

    def __init__(self, auth, **valores):
        from revaulte.auth import AuthState

        self.situacao, self.anunciante, self.anuncios = "carregando", "", []
        self.aviso, self.mensagem_erro, self._aviso_pendente = "", "", False
        self._estados = {AuthState: auth}
        for nome, valor in valores.items():
            setattr(self, nome, valor)

    async def get_state(self, classe):
        return self._estados[classe]


class AnunciarFalso:
    """Substitui o AnunciarState; guarda um MeusFalso para o aviso após o envio."""

    def __init__(self, auth, **valores):
        from revaulte.anuncios import MeusAnunciosState, _zerar_anunciar
        from revaulte.auth import AuthState

        _zerar_anunciar(self)
        self.meus = MeusFalso(auth)
        self._estados = {AuthState: auth, MeusAnunciosState: self.meus}
        for nome, valor in valores.items():
            setattr(self, nome, valor)

    async def get_state(self, classe):
        return self._estados[classe]


async def rodar(evento, estado, *args, resposta=(200, LISTA_COM_ANUNCIANTE)):
    """Executa o evento; devolve (eventos produzidos, chamada simulada ao Xano, `enviando` a cada passo)."""
    chamada = AsyncMock(return_value=resposta)
    eventos, enviando = [], []

    def guardar(saida):
        if saida is not None:
            eventos.extend(saida if isinstance(saida, list) else [saida])

    with patch("revaulte.anuncios.chamar_xano", chamada):
        resultado = evento.fn(estado, *args)
        if hasattr(resultado, "__anext__"):
            async for saida in resultado:
                enviando.append(getattr(estado, "enviando", None))
                guardar(saida)
        else:
            guardar(await resultado)
    return eventos, chamada, enviando


def redirect_login(rota):
    import reflex as rx

    return [rx.redirect(f"/entrar?proximo={rota}")]


class TestMeusAnunciosState(unittest.IsolatedAsyncioTestCase):
    async def abrir(self, auth=None, resposta=(200, LISTA_COM_ANUNCIANTE), **valores):
        from revaulte.anuncios import MeusAnunciosState

        estado = MeusFalso(auth or AuthFalso(), **valores)
        eventos, chamada, _ = await rodar(MeusAnunciosState.abrir, estado, resposta=resposta)
        return estado, eventos, chamada

    async def test_lista_do_cliente(self):
        estado, eventos, chamada = await self.abrir()
        self.assertEqual(eventos, [])
        chamada.assert_awaited_once_with("GET", URL_ANUNCIOS, TOKEN)
        self.assertEqual((estado.situacao, estado.anunciante), ("lista", "Garagem A Teste"))
        self.assertEqual([a.id for a in estado.anuncios], [7])
        self.assertEqual(estado.anuncios[0].rotulo_estado, "Rascunho — aguardando publicação")

    async def test_sessao_conferida_no_backend_antes_da_lista(self):
        auth = AuthFalso()
        await self.abrir(auth)
        self.assertEqual(auth.rotas_exigidas, [("/meus-anuncios", None)])

    async def test_conta_sem_anuncios(self):
        estado, _, _ = await self.abrir(resposta=(200, LISTA_SEM_ANUNCIANTE))
        self.assertEqual((estado.situacao, estado.anunciante, estado.anuncios), ("lista", "", []))

    async def test_visitante_vai_ao_login_sem_consultar_anuncios(self):
        estado, eventos, chamada = await self.abrir(AuthFalso(token="", redirecionar=redirect_login("/meus-anuncios")))
        chamada.assert_not_called()
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/meus-anuncios"])
        self.assertEqual((estado.anuncios, estado.anunciante), ([], ""))

    async def test_falha_ao_conferir_a_sessao(self):
        estado, _, chamada = await self.abrir(AuthFalso(situacao="erro"))
        chamada.assert_not_called()
        self.assertEqual((estado.situacao, estado.mensagem_erro), ("erro", ERRO_GENERICO_ANUNCIO))

    async def test_token_recusado_pelo_endpoint(self):
        auth = AuthFalso()
        estado, eventos, _ = await self.abrir(auth, resposta=(401, None))
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/meus-anuncios"])
        self.assertIn("_remove_cookie", nomes_de_eventos(eventos))
        self.assertEqual(auth.token, "")
        self.assertEqual(estado.anuncios, [])

    async def test_conta_sem_permissao(self):
        estado, eventos, _ = await self.abrir(resposta=(403, {"message": "role"}))
        self.assertEqual((estado.situacao, eventos), ("restrito", []))

    async def test_falhas_do_backend(self):
        for resposta, texto in (((0, None), ERRO_GENERICO_ANUNCIO), ((500, None), ERRO_GENERICO_ANUNCIO),
                                ((429, None), ERRO_MUITAS_TENTATIVAS), ((200, {"code": "x"}), ERRO_GENERICO_ANUNCIO),
                                ((200, None), ERRO_GENERICO_ANUNCIO)):
            with self.subTest(resposta=resposta):
                estado, _, _ = await self.abrir(resposta=resposta)
                self.assertEqual((estado.situacao, estado.mensagem_erro, estado.anuncios), ("erro", texto, []))

    async def test_aviso_de_envio_mostrado_uma_vez(self):
        from revaulte.anuncios import AVISO_ENVIADO, MeusAnunciosState

        estado, _, _ = await self.abrir(_aviso_pendente=True)
        self.assertEqual(estado.aviso, AVISO_ENVIADO)
        self.assertFalse(estado._aviso_pendente)
        await rodar(MeusAnunciosState.abrir, estado)
        self.assertEqual(estado.aviso, "")

    async def test_lista_anterior_apagada_ao_reabrir(self):
        estado, _, _ = await self.abrir(resposta=(500, None), anuncios=["anterior"], anunciante="Anterior")
        self.assertEqual((estado.anuncios, estado.anunciante), ([], ""))

    def test_limpar(self):
        from revaulte.anuncios import MeusAnunciosState

        estado = MeusFalso(AuthFalso(), situacao="lista", anunciante="X", anuncios=["a"], aviso="y",
                           mensagem_erro="z", _aviso_pendente=True)
        MeusAnunciosState.limpar.fn(estado)
        self.assertEqual((estado.situacao, estado.anunciante, estado.anuncios, estado.aviso, estado._aviso_pendente),
                         ("carregando", "", [], "", False))


class TestAnunciarState(unittest.IsolatedAsyncioTestCase):
    async def abrir(self, auth=None, resposta=(200, LISTA_SEM_ANUNCIANTE)):
        from revaulte.anuncios import AnunciarState

        estado = AnunciarFalso(auth or AuthFalso(), erro_formulario="anterior", enviando=True)
        eventos, chamada, _ = await rodar(AnunciarState.abrir, estado, resposta=resposta)
        return estado, eventos, chamada

    async def enviar(self, dados, resposta=(200, {"id": 8, "status": "draft"}), auth=None, **valores):
        from revaulte.anuncios import AnunciarState

        estado = AnunciarFalso(auth or AuthFalso(), situacao="pronto", **valores)
        eventos, chamada, enviando = await rodar(AnunciarState.enviar, estado, dados, resposta=resposta)
        return estado, eventos, chamada, enviando

    async def test_primeiro_anuncio_pede_nome_sugerido_pela_conta(self):
        estado, eventos, chamada = await self.abrir()
        chamada.assert_awaited_once_with("GET", URL_ANUNCIOS, TOKEN)
        self.assertEqual(eventos, [])
        self.assertEqual((estado.situacao, estado.tem_anunciante, estado.nome_sugerido),
                         ("pronto", False, "Cliente Demo"))
        self.assertEqual((estado.erro_formulario, estado.enviando), ("", False))

    async def test_nome_da_conta_longo_nao_e_sugerido(self):
        estado, _, _ = await self.abrir(AuthFalso(nome="N" * 61))
        self.assertEqual(estado.nome_sugerido, "")

    async def test_conta_com_anunciante_so_exibe_o_nome(self):
        estado, _, _ = await self.abrir(resposta=(200, LISTA_COM_ANUNCIANTE))
        self.assertEqual((estado.tem_anunciante, estado.nome_anunciante), (True, "Garagem A Teste"))

    async def test_visitante_vai_ao_login(self):
        estado, eventos, chamada = await self.abrir(AuthFalso(token="", redirecionar=redirect_login("/anunciar")))
        chamada.assert_not_called()
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/anunciar"])
        self.assertEqual(estado.situacao, "carregando")

    async def test_falhas_ao_abrir(self):
        for resposta, situacao in (((403, None), "restrito"), ((500, None), "erro"), ((0, None), "erro"),
                                   ((200, {"x": 1}), "erro")):
            with self.subTest(resposta=resposta):
                estado, _, _ = await self.abrir(resposta=resposta)
                self.assertEqual(estado.situacao, situacao)
        estado, eventos, _ = await self.abrir(resposta=(401, None))
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/anunciar"])

    async def test_envio_valido(self):
        estado, eventos, chamada, enviando = await self.enviar(formulario(), tem_anunciante=False)
        payload, _ = validar_anuncio(formulario(), False)
        chamada.assert_awaited_once_with("POST", URL_ANUNCIOS, TOKEN, payload)
        self.assertTrue(enviando[0], "o botão deve ficar desabilitado durante o envio")
        self.assertFalse(estado.enviando)
        self.assertEqual(destinos_redirect(eventos), ["/meus-anuncios"])
        self.assertTrue(estado.meus._aviso_pendente)

    async def test_envio_com_anunciante_nao_manda_nome(self):
        _, _, chamada, _ = await self.enviar(formulario(), tem_anunciante=True)
        self.assertNotIn("display_name", chamada.await_args.args[3])

    async def test_envio_invalido_nao_chama_o_backend(self):
        estado, eventos, chamada, _ = await self.enviar(formulario(preco="0"))
        chamada.assert_not_called()
        self.assertEqual((estado.erro_formulario, eventos), (MENSAGENS_VALIDACAO["invalid_price"], []))
        self.assertFalse(estado.enviando)

    async def test_envio_repetido_ignorado(self):
        _, eventos, chamada, _ = await self.enviar(formulario(), enviando=True)
        chamada.assert_not_called()
        self.assertEqual(eventos, [])

    async def test_erros_do_envio_mantem_a_pagina(self):
        for resposta, texto in (
            ((400, {"message": "draft_limit_reached"}), ERRO_LIMITE_RASCUNHOS),
            ((400, {"message": "invalid_year"}), MENSAGENS_VALIDACAO["invalid_year"]),
            ((429, None), ERRO_MUITAS_TENTATIVAS), ((403, None), ERRO_RESTRITO), ((0, None), ERRO_GENERICO_ANUNCIO),
            ((500, {"message": "SQLSTATE unique"}), ERRO_GENERICO_ANUNCIO),
            ((200, {"status": "draft"}), ERRO_GENERICO_ANUNCIO),
        ):
            with self.subTest(resposta=resposta):
                estado, eventos, _, _ = await self.enviar(formulario(), resposta=resposta)
                self.assertEqual((estado.erro_formulario, eventos, estado.enviando), (texto, [], False))
                self.assertFalse(estado.meus._aviso_pendente)

    async def test_sessao_expirada_no_envio(self):
        auth = AuthFalso()
        estado, eventos, _, _ = await self.enviar(formulario(), resposta=(401, None), auth=auth)
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/anunciar"])
        self.assertEqual((auth.token, estado.enviando), ("", False))

    def test_dados_digitados_nunca_ficam_no_estado(self):
        from revaulte.anuncios import AnunciarState

        campos = set(AnunciarState.get_fields())
        for proibido in ("marca", "modelo", "preco", "descricao", "nome_exibicao", "payload", "dados", "token"):
            with self.subTest(proibido=proibido):
                self.assertFalse(any(proibido in c for c in campos))

    def test_sair_limpa_os_estados_de_anuncios(self):
        from revaulte.auth import AuthState

        eventos = AuthState.sair.fn(EstadoSessaoFalso(TOKEN))
        nomes = nomes_de_eventos(eventos)
        for nome in ("AdminState.limpar", "AnunciarState.limpar", "MeusAnunciosState.limpar", "_remove_cookie"):
            with self.subTest(nome=nome):
                self.assertIn(nome, nomes)
        self.assertEqual(destinos_redirect(eventos), ["/"])


class TestPaginasDeAnuncios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_navegacao import codigo

        from revaulte.components import pagina_anunciar, pagina_meus_anuncios

        cls.anunciar = codigo(pagina_anunciar())
        cls.meus = codigo(pagina_meus_anuncios())

    def test_rotas_registradas_com_protecao(self):
        from revaulte.revaulte import app

        for rota, evento in (("anunciar", "AnunciarState.abrir"), ("meus-anuncios", "MeusAnunciosState.abrir")):
            with self.subTest(rota=rota):
                self.assertIn(rota, app._unevaluated_pages)
                on_load = app._unevaluated_pages[rota].on_load
                self.assertEqual(nomes_de_eventos(on_load), ["MenuState.fechar_menu", evento])

    def test_destinos_seguros(self):
        from revaulte.auth import destino_seguro

        for rota in ("/anunciar", "/meus-anuncios"):
            self.assertEqual(destino_seguro(rota), rota)
        # A ficha /meus-anuncios/<id> tem teste próprio (TestPaginaFichaAnuncio).
        for invalida in ("/anunciar/", "/meus-anuncios?x=1", "//anunciar", "/Anunciar"):
            with self.subTest(invalida=invalida):
                self.assertEqual(destino_seguro(invalida), "/conta")

    def test_campos_do_formulario(self):
        for nome in ("nome_exibicao", "marca", "modelo", "versao", "ano", "quilometragem", "preco", "condicao",
                     "modificado", "cor", "motorizacao", "cambio", "descricao"):
            with self.subTest(nome=nome):
                self.assertIn(f'name:"{nome}"', self.anunciar)
        for proibido in ('name:"status"', 'name:"seller_id"', 'name:"user_id"', 'name:"cover_image_url"'):
            self.assertNotIn(proibido, self.anunciar)

    def test_formulario_nao_controlado(self):
        from revaulte.components import pagina_anunciar

        # O onSubmit fica no hook handleSubmit, fora do JSX (mesmo padrão de /cadastro).
        ganchos = " ".join(map(str, pagina_anunciar()._get_all_hooks()))
        self.assertEqual(sorted(set(re.findall(r"anunciar_state\.\w+", ganchos))), ["anunciar_state.enviar"])
        self.assertNotIn("auth_state.", ganchos)
        self.assertNotIn("onChange", self.anunciar)
        self.assertNotIn("checked", self.anunciar.lower())  # nenhuma opção marcada de antemão
        self.assertIn("noValidate:true", self.anunciar)

    def test_opcoes_de_escolha(self):
        for nome, valor in (("condicao", "used"), ("condicao", "new"), ("modificado", "nao"), ("modificado", "sim")):
            with self.subTest(valor=valor):
                self.assertIn(f'name:"{nome}",ref:ref_{nome}_{valor},type:"radio",value:'
                              f'(isNotNullOrUndefined("{valor}") ? "{valor}" : "")', self.anunciar)
        self.assertEqual(self.anunciar.count('type:"radio"'), 4)

    def test_nome_de_exibicao_condicionado_ao_anunciante(self):
        self.assertIn("anunciar_state.tem_anunciante", self.anunciar)
        self.assertIn("anunciar_state.nome_sugerido", self.anunciar)
        self.assertIn("Não poderá ser alterado depois.", self.anunciar)

    def test_botao_e_mensagem_ligados_ao_estado_de_anuncios(self):
        self.assertIn("anunciar_state.enviando", self.anunciar)
        self.assertIn("anunciar_state.erro_formulario", self.anunciar)
        self.assertIn("Enviar anúncio", self.anunciar)
        self.assertNotIn("auth_state.enviando", self.anunciar)

    def test_estados_da_pagina_anunciar(self):
        for texto in ("Preparando o formulário…", "Acesso restrito", "Tentar novamente", "anunciar_state.mensagem_erro"):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.anunciar)

    def test_pagina_meus_anuncios(self):
        for texto in ("Meus anúncios", "Anúncio", "Ano", "Preço", "Estado", "Enviado em", "Você ainda não tem anúncios.",
                      "Carregando seus anúncios…", "Acesso restrito", "Tentar novamente", "meus_anuncios_state.aviso",
                      "meus_anuncios_state.anunciante", "Anunciar outro veículo", 'to:"/anunciar"'):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.meus)
        self.assertIn('"data-label":"Estado"', self.meus)

    def test_nenhum_dado_interno_nas_paginas(self):
        for pagina in (self.anunciar, self.meus):
            for proibido in ("seller_id", "user_id", "whatsapp", "cpf"):
                with self.subTest(proibido=proibido):
                    self.assertNotIn(proibido, pagina.lower())


class TestEstilosDosAnuncios(unittest.TestCase):
    """Tarefa 5.3: classes usadas pelas páginas têm regra, e nada força largura acima de 375 px."""

    @classmethod
    def setUpClass(cls):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        cls.css = css
        cls.secao = css[css.index("Anúncios dos Clientes: /anunciar e /meus-anuncios"):]

    def test_chaves_balanceadas(self):
        self.assertEqual(self.css.count("{"), self.css.count("}"))

    def test_classes_das_paginas_tem_estilo(self):
        for seletor in (".filter-field textarea {", ".choice-field {", ".choice-field legend {", ".choice-group {",
                        ".choice {", ".choice input {", ".choice input:focus-visible {", ".choice:has(input:checked) {",
                        ".seller-readonly {", ".form-success {", ".ads-toolbar {", ".status-tag {",
                        ".status-tag.is-available {", ".status-tag.is-sold {"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor, self.secao)

    def test_classes_usadas_existem_no_css(self):
        from test_navegacao import codigo

        from revaulte.components import pagina_anunciar, pagina_meus_anuncios

        gerado = codigo(pagina_anunciar()) + codigo(pagina_meus_anuncios())
        classes = set()
        for valor in re.findall(r'className:"([^"]+)"', gerado):
            classes.update(valor.split())
        # A etiqueta de estado monta a classe com o estado: is-draft, is-available ou is-sold.
        classes.update({"status-tag"})
        # menu-panel-account: marcador do menu (Change contas-acesso), sem regra própria desde antes.
        classes.discard("menu-panel-account")
        sem_regra = sorted(c for c in classes if not re.search(rf"\.{re.escape(c)}\b", self.css))
        self.assertEqual(sem_regra, [])

    def test_celular_sem_largura_fixa(self):
        # Nenhuma largura ou largura mínima em px na seção (o layout depende de 100%, flex e grid).
        # Só declarações (linhas recuadas dentro de regras); "@media (min-width: 561px)" é condição.
        self.assertIsNone(re.search(r"^\s+(min-)?width:\s*\d{3,}px", self.secao, re.M))
        self.assertIn("@media (max-width: 760px)", self.secao)
        self.assertRegex(self.secao, r"@media \(max-width: 560px\) \{\s*\.ads-toolbar \{\s*flex-direction: column;")
        self.assertRegex(self.secao, r"\.choice \{\s*flex-basis: 100%;")

    def test_textos_longos_quebram(self):
        for seletor in (".seller-readonly {", ".ads-toolbar strong {"):
            bloco = self.secao[self.secao.index(seletor):]
            self.assertIn("overflow-wrap: anywhere;", bloco[: bloco.index("}")])

    def test_movimento_reduzido_coberto_pela_regra_global(self):
        # As transições novas são desligadas pela regra global de prefers-reduced-motion.
        self.assertRegex(self.css, r"@media \(prefers-reduced-motion: reduce\) \{[^}]*\*,\s*\*::before,\s*\*::after \{"
                                   r"\s*transition: none !important;\s*animation: none !important;")
        self.assertNotIn("animation:", self.secao)
        self.assertIsNone(re.search(r"(?<!-)transform:", self.secao))  # text-transform é permitido


# ---------------------------------------------------------------------------
# Ficha privada /meus-anuncios/<id> (tarefa 4.4 e restante da 6.1), com respostas simuladas.
# ---------------------------------------------------------------------------
class RoteadorFalso:
    def __init__(self, params, raw_path):
        self.page = type("Pagina", (), {"params": params, "raw_path": raw_path})()


class FichaFalso:
    """Substitui o FichaAnuncioState."""

    def __init__(self, auth, id_na_rota="7", usar_params=True, **valores):
        from revaulte.anuncios import _zerar_ficha
        from revaulte.auth import AuthState

        _zerar_ficha(self)
        params = {"anuncio_id": id_na_rota} if usar_params else {}
        self.router = RoteadorFalso(params, f"/meus-anuncios/{id_na_rota}")
        self._estados = {AuthState: auth}
        for nome, valor in valores.items():
            setattr(self, nome, valor)

    async def get_state(self, classe):
        return self._estados[classe]


class TestFichaAnuncioState(unittest.IsolatedAsyncioTestCase):
    async def abrir(self, id_na_rota="7", auth=None, resposta=(200, item()), **opcoes):
        from revaulte.anuncios import FichaAnuncioState

        estado = FichaFalso(auth or AuthFalso(), id_na_rota, **opcoes)
        eventos, chamada, _ = await rodar(FichaAnuncioState.abrir, estado, resposta=resposta)
        return estado, eventos, chamada

    async def test_ficha_do_proprio_anuncio(self):
        auth = AuthFalso()
        estado, eventos, chamada = await self.abrir(auth=auth)
        self.assertEqual(eventos, [])
        chamada.assert_awaited_once_with("GET", URL_ANUNCIOS + "/7", TOKEN)
        self.assertEqual(auth.rotas_exigidas, [("/meus-anuncios/7", None)])
        self.assertEqual((estado.situacao, estado.ficha.id, estado.ficha.endereco_publico), ("ficha", 7, ""))
        self.assertEqual(estado.ficha.rotulo_estado, "Rascunho — aguardando publicação")

    async def test_anuncio_publicado_tem_link_publico(self):
        estado, _, _ = await self.abrir(resposta=(200, item(status="available")))
        self.assertEqual(estado.ficha.endereco_publico, "/veiculo/7")

    async def test_identificador_lido_do_caminho_sem_parametro(self):
        estado, _, chamada = await self.abrir("7", usar_params=False)
        chamada.assert_awaited_once_with("GET", URL_ANUNCIOS + "/7", TOKEN)
        self.assertEqual(estado.situacao, "ficha")

    async def test_identificador_invalido_nao_consulta_o_backend(self):
        for texto in ("abc", "0", "07", "-1", "1.5", "7x", "1234567890123", "%2F", ""):
            with self.subTest(texto=texto):
                auth = AuthFalso()
                estado, eventos, chamada = await self.abrir(texto, auth=auth, usar_params=True)
                chamada.assert_not_called()
                self.assertEqual((estado.situacao, eventos, auth.rotas_exigidas), ("nao_encontrado", [], []))

    async def test_visitante_vai_ao_login_e_volta_para_a_ficha(self):
        estado, eventos, chamada = await self.abrir(
            auth=AuthFalso(token="", redirecionar=redirect_login("/meus-anuncios/7"))
        )
        chamada.assert_not_called()
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/meus-anuncios/7"])
        self.assertEqual(estado.ficha.id, 0)

    async def test_404_igual_para_anuncio_alheio_da_equipe_ou_inexistente(self):
        for corpo in ({"code": "ERROR_CODE_NOT_FOUND", "message": "Not Found."}, None, {}):
            with self.subTest(corpo=corpo):
                estado, eventos, _ = await self.abrir(resposta=(404, corpo))
                self.assertEqual((estado.situacao, estado.ficha.id, eventos), ("nao_encontrado", 0, []))

    async def test_token_recusado(self):
        auth = AuthFalso()
        estado, eventos, _ = await self.abrir(auth=auth, resposta=(401, None))
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/meus-anuncios/7"])
        self.assertIn("_remove_cookie", nomes_de_eventos(eventos))
        self.assertEqual((auth.token, estado.ficha.id), ("", 0))

    async def test_conta_sem_permissao(self):
        estado, eventos, _ = await self.abrir(resposta=(403, None))
        self.assertEqual((estado.situacao, eventos), ("restrito", []))

    async def test_falhas_e_respostas_inesperadas(self):
        for resposta in ((0, None), (500, None), (429, None), (200, None), (200, {"x": 1}),
                         (200, item(id=8)), (200, item(status="reserved"))):
            with self.subTest(resposta=resposta):
                estado, _, _ = await self.abrir(resposta=resposta)
                self.assertEqual((estado.situacao, estado.ficha.id), ("erro", 0))
                self.assertNotEqual(estado.mensagem_erro, "")

    async def test_falha_ao_conferir_a_sessao(self):
        estado, _, chamada = await self.abrir(auth=AuthFalso(situacao="erro"))
        chamada.assert_not_called()
        self.assertEqual((estado.situacao, estado.mensagem_erro), ("erro", ERRO_GENERICO_ANUNCIO))

    async def test_ficha_anterior_apagada_ao_reabrir(self):
        from revaulte.anuncios import FichaAnuncio

        estado, _, _ = await self.abrir("abc", ficha=FichaAnuncio(id=99, titulo="Anterior"))
        self.assertEqual((estado.ficha.id, estado.ficha.titulo), (0, ""))

    def test_limpar_e_nenhum_dado_digitado(self):
        from revaulte.anuncios import FichaAnuncio, FichaAnuncioState

        estado = FichaFalso(AuthFalso(), situacao="ficha", ficha=FichaAnuncio(id=7), id_pedido=7)
        FichaAnuncioState.limpar.fn(estado)
        self.assertEqual((estado.situacao, estado.ficha.id, estado.id_pedido), ("carregando", 0, 0))
        campos = set(FichaAnuncioState.get_fields())
        self.assertFalse({"token", "senha", "dados", "payload"} & campos)

    def test_sair_limpa_tambem_a_ficha(self):
        from revaulte.auth import AuthState

        self.assertIn("FichaAnuncioState.limpar", nomes_de_eventos(AuthState.sair.fn(EstadoSessaoFalso(TOKEN))))


class TestPaginaFichaAnuncio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_navegacao import codigo

        from revaulte.components import pagina_ficha_anuncio, pagina_meus_anuncios

        cls.ficha = codigo(pagina_ficha_anuncio())
        cls.lista = codigo(pagina_meus_anuncios())

    def test_rota_registrada_com_protecao(self):
        from revaulte.revaulte import app

        self.assertIn("meus-anuncios/[anuncio_id]", app._unevaluated_pages)
        self.assertEqual(nomes_de_eventos(app._unevaluated_pages["meus-anuncios/[anuncio_id]"].on_load),
                         ["MenuState.fechar_menu", "FichaAnuncioState.abrir"])

    def test_rotulos_da_ficha(self):
        for texto in ("Marca", "Modelo", "Versão", "Ano", "Condição", "Quilometragem", "Preço",
                      "Modificado/preparado", "Cor", "Motorização", "Câmbio", "Enviado em", "Descrição",
                      "Ver página pública", "← Meus anúncios", "Ver meus anúncios", "Tentar novamente",
                      "Carregando o anúncio…", "Acesso restrito", "Anúncio não encontrado.",
                      "Este anúncio ainda não está no site."):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.ficha)

    def test_link_publico_condicionado_ao_endereco_publico(self):
        self.assertIn('ficha_rx_state_?.["endereco_publico"]', self.ficha)
        # O link fica no ramo "endereço público diferente de vazio"; o outro ramo só tem a explicação.
        i = self.ficha.index('"Ver página pública"')
        self.assertIn('["endereco_publico"]},"Ver página pública"', self.ficha)
        self.assertIn('=== ""?.valueOf?.()))?(jsx(Fragment,{},jsx(ReactRouterLink,{className:"btn btn-red",to:',
                      self.ficha[i - 400: i])
        self.assertGreater(self.ficha.index("Este anúncio ainda não está no site."), i)
        self.assertIn("ficha_anuncio_state.situacao", self.ficha)

    def test_somente_leitura(self):
        for proibido in ("<form", 'jsx("form"', "onSubmit", 'type:"submit"', "Editar", "Excluir", "Apagar",
                         "Remover", 'jsx("input"', "textarea"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, self.ficha)

    def test_nenhum_dado_interno(self):
        for proibido in ("seller_id", "user_id", "whatsapp", "cpf", "token"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, self.ficha.lower())

    def test_lista_tem_ver_detalhes_com_o_endereco_do_anuncio(self):
        self.assertIn("Ver detalhes", self.lista)
        self.assertIn("Detalhes", self.lista)
        self.assertIn('"data-label":"Detalhes"', self.lista)
        self.assertIn("meus_anuncios_state.anuncios", self.lista)
        self.assertIn('to:anuncio_rx_state_?.["endereco"]', self.lista)

    def test_destinos_seguros_da_ficha(self):
        from revaulte.auth import destino_seguro

        for valido in ("/meus-anuncios/7", "/meus-anuncios/123456789012", "/meus-anuncios/10"):
            with self.subTest(valido=valido):
                self.assertEqual(destino_seguro(valido), valido)
        for invalido in ("/meus-anuncios/0", "/meus-anuncios/07", "/meus-anuncios/1234567890123",
                         "/meus-anuncios/abc", "/meus-anuncios/-1", "/meus-anuncios/7/", "/meus-anuncios/7?x=1",
                         "/meus-anuncios/7#a", "/meus-anuncios/7/editar", "/meus-anuncios//7",
                         "/meus-anuncios/%37", "//meus-anuncios/7", "https://exemplo.com/meus-anuncios/7",
                         "/meus-anuncios/7 ", "/meus-anuncios/\\7", "/Meus-anuncios/7", "/meus-anuncios/../7",
                         "/meus-anuncios/٧"):
            with self.subTest(invalido=invalido):
                self.assertEqual(destino_seguro(invalido), "/conta")

    def test_estilos_da_ficha(self):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for seletor in (".ad-back {", ".ad-state {", ".ad-facts {", ".ad-block {", ".ad-subtitle {", ".ad-description {"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor, css)
        self.assertRegex(css, r"\.ad-description \{[^}]*white-space: pre-line;[^}]*overflow-wrap: anywhere;")
        self.assertRegex(css, r"@media \(max-width: 560px\) \{\s*\.auth-card \.btn \{\s*width: 100%;")


if __name__ == "__main__":
    unittest.main()
