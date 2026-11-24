# Testes da Change favoritos: funções puras, estados (respostas simuladas), arquivos XanoScript
# locais e componentes. Não chamam o Xano. Execução, dentro de frontend/:
#   python -m unittest discover -s tests
import os
import re
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import reflex as rx

from revaulte.config import FAVORITOS_API_URL_PADRAO, favoritos_api_url
from revaulte.revaulte import app  # noqa: F401  registra os estados e as páginas antes dos demais imports

TOKEN = "token-de-teste"
URL = f"{FAVORITOS_API_URL_PADRAO}/favoritos"
XANO = Path(__file__).resolve().parents[2] / "xano"


def veiculo(i, status="available", **extra):
    base = {"id": i, "brand": "Chevrolet", "model": f"Modelo{i}", "year": 1975, "condition": "used",
            "mileage": 1000, "price": "50000", "is_modified": False, "status": status}
    return {**base, **extra}


class AuthFalso:
    def __init__(self, token=TOKEN, situacao="ok", redirecionar=None):
        self.token, self._situacao, self._redirecionar = token, situacao, redirecionar
        self.situacao_protegida = "carregando"
        self.rotas = []

    async def _exigir(self, rota, perfil):
        self.rotas.append(rota)
        if self._redirecionar is not None:
            return self._redirecionar
        self.situacao_protegida = self._situacao

    def _encerrar(self):
        self.token = ""


class EstadoFalso:
    def __init__(self, auth, caminho="/veiculo/5", **valores):
        from revaulte.auth import AuthState

        self.situacao, self.cartoes, self.mensagem_erro = "carregando", [], ""
        self.veiculo_id, self.favorito_atual, self.ocupado, self.erro_botao = 0, False, False, ""
        self.router = SimpleNamespace(page=SimpleNamespace(params={"veiculo_id": caminho.rsplit("/", 1)[-1]}, raw_path=caminho))
        self._auth = auth
        self._estados = {AuthState: auth}
        for k, v in valores.items():
            setattr(self, k, v)

    async def get_state(self, classe):
        return self._estados[classe]


async def rodar(evento, estado, *args, respostas):
    """respostas: lista de (status, corpo), uma por chamada ao Xano, na ordem."""
    chamada = AsyncMock(side_effect=list(respostas))
    eventos = []

    def guardar(saida):
        if saida is not None:
            eventos.extend(saida if isinstance(saida, list) else [saida])

    with patch("revaulte.favoritos.chamar_xano", chamada):
        resultado = evento.fn(estado, *args)
        if hasattr(resultado, "__anext__"):
            async for saida in resultado:
                guardar(saida)
        else:
            guardar(await resultado)
    return eventos, chamada


def destinos(eventos):
    return [e.args[0].get("path") if hasattr(e, "args") else None for e in eventos]


class TestConfig(unittest.TestCase):
    def test_padrao_e_substituicao(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("REVAULTE_FAVORITOS_API_URL", None)
            self.assertEqual(favoritos_api_url(), FAVORITOS_API_URL_PADRAO)
        with patch.dict(os.environ, {"REVAULTE_FAVORITOS_API_URL": " https://x.invalido/api:f/ "}):
            self.assertEqual(favoritos_api_url(), "https://x.invalido/api:f")
        with patch.dict(os.environ, {"REVAULTE_FAVORITOS_API_URL": "  "}):
            self.assertEqual(favoritos_api_url(), FAVORITOS_API_URL_PADRAO)


class TestFuncoesPuras(unittest.TestCase):
    def test_preparar_ids(self):
        from revaulte.favoritos import preparar_ids

        corpo = [{"vehicle_id": 3}, {"vehicle_id": 1}, {"vehicle_id": 3}, {"vehicle_id": True},
                 {"vehicle_id": 0}, {"vehicle_id": "2"}, {"x": 1}, "lixo"]
        self.assertEqual(preparar_ids(corpo), [3, 1])
        self.assertEqual(preparar_ids([]), [])
        for ruim in (None, {}, "x", 5):
            with self.assertRaises(ValueError):
                preparar_ids(ruim)

    def test_selecionar_cartoes_respeita_ordem_e_catalogo_publico(self):
        from revaulte.favoritos import selecionar_cartoes

        catalogo = [veiculo(1), veiculo(2, status="sold"), veiculo(4), {"id": 9}, "lixo"]
        cartoes = selecionar_cartoes([2, 7, 1, 9], catalogo)  # 7 fora do catálogo; 9 malformado
        self.assertEqual([c.id for c in cartoes], [2, 1])
        self.assertTrue(cartoes[0].vendido)
        with self.assertRaises(ValueError):
            selecionar_cartoes([1], {"x": 1})

    def test_mensagens_de_erro_nunca_cruas(self):
        from revaulte.favoritos import (ERRO_GENERICO_FAVORITO, ERRO_INDISPONIVEL, ERRO_MUITAS_TENTATIVAS,
                                         ERRO_RESTRITO_FAVORITO, mensagem_erro_favorito)

        self.assertEqual(mensagem_erro_favorito(404), ERRO_INDISPONIVEL)
        self.assertEqual(mensagem_erro_favorito(403), ERRO_RESTRITO_FAVORITO)
        self.assertEqual(mensagem_erro_favorito(429), ERRO_MUITAS_TENTATIVAS)
        for status in (0, 400, 500):
            self.assertEqual(mensagem_erro_favorito(status), ERRO_GENERICO_FAVORITO)


class TestBotaoDaPaginaDoVeiculo(unittest.IsolatedAsyncioTestCase):
    async def test_verificar_marca_favorito_existente(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso())
        _, chamada = await rodar(FavoritosState.verificar_veiculo, e, respostas=[(200, [{"vehicle_id": 5}])])
        chamada.assert_awaited_once_with("GET", URL, TOKEN)
        self.assertEqual((e.veiculo_id, e.favorito_atual), (5, True))

    async def test_verificar_sem_favorito(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso())
        await rodar(FavoritosState.verificar_veiculo, e, respostas=[(200, [{"vehicle_id": 2}])])
        self.assertFalse(e.favorito_atual)

    async def test_visitante_nao_consulta_o_backend(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso(token=""))
        _, chamada = await rodar(FavoritosState.verificar_veiculo, e, respostas=[])
        chamada.assert_not_called()
        self.assertEqual(e.veiculo_id, 5)

    async def test_identificador_invalido_nao_consulta(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso(), caminho="/veiculo/abc")
        _, chamada = await rodar(FavoritosState.verificar_veiculo, e, respostas=[])
        chamada.assert_not_called()
        self.assertEqual(e.veiculo_id, 0)

    async def test_falha_ao_verificar_nao_quebra_o_botao(self):
        from revaulte.favoritos import FavoritosState

        for resposta in ((500, None), (0, None), (200, {"x": 1}), (401, None)):
            e = EstadoFalso(AuthFalso())
            await rodar(FavoritosState.verificar_veiculo, e, respostas=[resposta])
            self.assertEqual((e.favorito_atual, e.erro_botao), (False, ""))

    async def test_favoritar(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso(), veiculo_id=5)
        _, chamada = await rodar(FavoritosState.alternar, e, respostas=[(200, {"favorited": True})])
        chamada.assert_awaited_once_with("POST", f"{URL}/5", TOKEN)
        self.assertEqual((e.favorito_atual, e.ocupado, e.erro_botao), (True, False, ""))

    async def test_remover(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso(), veiculo_id=5, favorito_atual=True)
        _, chamada = await rodar(FavoritosState.alternar, e, respostas=[(200, {})])
        chamada.assert_awaited_once_with("DELETE", f"{URL}/5", TOKEN)
        self.assertFalse(e.favorito_atual)

    async def test_visitante_vai_ao_login_e_volta_ao_veiculo(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso(token=""), veiculo_id=5)
        eventos, chamada = await rodar(FavoritosState.alternar, e, respostas=[])
        chamada.assert_not_called()
        self.assertEqual(len(eventos), 1)
        self.assertIn("/entrar?proximo=/veiculo/5", str(eventos[0]))
        self.assertFalse(e.favorito_atual)

    async def test_erros_mantem_o_estado_e_mostram_texto_proprio(self):
        from revaulte.favoritos import ERRO_GENERICO_FAVORITO, ERRO_INDISPONIVEL, FavoritosState

        for resposta, texto in (((404, {"message": "not_found"}), ERRO_INDISPONIVEL),
                                ((500, {"message": "segredo interno"}), ERRO_GENERICO_FAVORITO),
                                ((0, None), ERRO_GENERICO_FAVORITO)):
            e = EstadoFalso(AuthFalso(), veiculo_id=5)
            await rodar(FavoritosState.alternar, e, respostas=[resposta])
            self.assertEqual((e.favorito_atual, e.ocupado, e.erro_botao), (False, False, texto))
            self.assertNotIn("segredo", e.erro_botao)

    async def test_token_recusado_encerra_a_sessao(self):
        from revaulte.favoritos import FavoritosState

        auth = AuthFalso()
        e = EstadoFalso(auth, veiculo_id=5)
        eventos, _ = await rodar(FavoritosState.alternar, e, respostas=[(401, None)])
        self.assertEqual(auth.token, "")
        self.assertIn("/entrar?proximo=/veiculo/5", "".join(str(x) for x in eventos))
        self.assertFalse(e.favorito_atual)

    async def test_clique_repetido_durante_envio_e_ignorado(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso(), veiculo_id=5, ocupado=True)
        _, chamada = await rodar(FavoritosState.alternar, e, respostas=[])
        chamada.assert_not_called()


class TestPaginaFavoritos(unittest.IsolatedAsyncioTestCase):
    async def abrir(self, auth=None, respostas=None, **valores):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(auth or AuthFalso(), **valores)
        eventos, chamada = await rodar(FavoritosState.abrir, e, respostas=respostas or [])
        return e, eventos, chamada

    async def test_lista_so_os_favoritos_publicos_na_ordem(self):
        e, _, chamada = await self.abrir(respostas=[(200, [{"vehicle_id": 2}, {"vehicle_id": 8}, {"vehicle_id": 1}]),
                                                   (200, [veiculo(1), veiculo(2, status="sold"), veiculo(3)])])
        self.assertEqual(chamada.await_args_list[0].args, ("GET", URL, TOKEN))
        self.assertEqual(chamada.await_args_list[1].args[0:2], ("GET", chamada.await_args_list[1].args[1]))
        self.assertTrue(chamada.await_args_list[1].args[1].endswith("/vehicles"))
        self.assertEqual(len(chamada.await_args_list[1].args), 2)  # catálogo público: sem token
        self.assertEqual(([c.id for c in e.cartoes], e.situacao), ([2, 1], "lista"))

    async def test_sessao_conferida_no_backend(self):
        auth = AuthFalso()
        await self.abrir(auth, respostas=[(200, [])])
        self.assertEqual(auth.rotas, ["/favoritos"])

    async def test_vazio_nao_consulta_o_catalogo(self):
        e, _, chamada = await self.abrir(respostas=[(200, [])])
        self.assertEqual((e.situacao, chamada.await_count), ("vazio", 1))

    async def test_favoritos_fora_do_catalogo_viram_vazio(self):
        e, _, _ = await self.abrir(respostas=[(200, [{"vehicle_id": 9}]), (200, [veiculo(1)])])
        self.assertEqual((e.situacao, e.cartoes), ("vazio", []))

    async def test_visitante_vai_ao_login(self):
        redirect = [rx.redirect("/entrar?proximo=/favoritos")]
        e, eventos, chamada = await self.abrir(AuthFalso(token="", redirecionar=redirect))
        chamada.assert_not_called()
        self.assertIn("/entrar?proximo=/favoritos", str(eventos))

    async def test_erros(self):
        from revaulte.favoritos import ERRO_GENERICO_FAVORITO

        for respostas, situacao in (([(500, None)], "erro"), ([(403, None)], "restrito"),
                                    ([(200, {"x": 1})], "erro"),
                                    ([(200, [{"vehicle_id": 1}]), (500, None)], "erro"),
                                    ([(200, [{"vehicle_id": 1}]), (200, {"x": 1})], "erro")):
            e, _, _ = await self.abrir(respostas=respostas)
            self.assertEqual((e.situacao, e.cartoes), (situacao, []))
            if situacao == "erro":
                self.assertTrue(e.mensagem_erro)
        e, _, _ = await self.abrir(AuthFalso(situacao="erro"))
        self.assertEqual((e.situacao, e.mensagem_erro), ("erro", ERRO_GENERICO_FAVORITO))

    async def test_token_recusado(self):
        auth = AuthFalso()
        e, eventos, _ = await self.abrir(auth, respostas=[(401, None)])
        self.assertEqual(auth.token, "")
        self.assertIn("/entrar?proximo=/favoritos", str(eventos))

    async def test_remover_da_lista(self):
        from revaulte.favoritos import FavoritosState
        from revaulte.state import preparar_cartao

        cartoes = [preparar_cartao(veiculo(1)), preparar_cartao(veiculo(2))]
        e = EstadoFalso(AuthFalso(), situacao="lista", cartoes=cartoes)
        _, chamada = await rodar(FavoritosState.remover, e, 1, respostas=[(200, {})])
        chamada.assert_awaited_once_with("DELETE", f"{URL}/1", TOKEN)
        self.assertEqual(([c.id for c in e.cartoes], e.situacao), ([2], "lista"))
        await rodar(FavoritosState.remover, e, 2, respostas=[(200, {})])
        self.assertEqual((e.cartoes, e.situacao), ([], "vazio"))

    async def test_falha_ao_remover_mantem_a_lista(self):
        from revaulte.favoritos import ERRO_GENERICO_FAVORITO, FavoritosState
        from revaulte.state import preparar_cartao

        e = EstadoFalso(AuthFalso(), situacao="lista", cartoes=[preparar_cartao(veiculo(1))])
        await rodar(FavoritosState.remover, e, 1, respostas=[(500, None)])
        self.assertEqual(([c.id for c in e.cartoes], e.mensagem_erro), ([1], ERRO_GENERICO_FAVORITO))

    async def test_remover_ignora_identificador_invalido(self):
        from revaulte.favoritos import FavoritosState

        e = EstadoFalso(AuthFalso())
        _, chamada = await rodar(FavoritosState.remover, e, True, respostas=[])
        chamada.assert_not_called()

    def test_limpar_apaga_tudo_da_conta(self):
        from revaulte.favoritos import FavoritosState
        from revaulte.state import preparar_cartao

        e = EstadoFalso(AuthFalso(), situacao="lista", cartoes=[preparar_cartao(veiculo(1))],
                        veiculo_id=5, favorito_atual=True, erro_botao="x", mensagem_erro="y")
        FavoritosState.limpar.fn(e)
        self.assertEqual((e.situacao, e.cartoes, e.veiculo_id, e.favorito_atual, e.erro_botao, e.mensagem_erro),
                         ("carregando", [], 0, False, "", ""))

    def test_sair_limpa_favoritos(self):
        from revaulte.auth import AuthState

        e = SimpleNamespace(_encerrar=lambda: None)
        eventos = AuthState.sair.fn(e)
        self.assertIn("favoritos_state.limpar", " ".join(str(x) for x in eventos).lower().replace("favoritosstate", "favoritos_state"))


class TestRotasEComponentes(unittest.TestCase):
    def test_destino_seguro(self):
        from revaulte.auth import destino_seguro

        self.assertEqual(destino_seguro("/favoritos"), "/favoritos")
        for ruim in ("/favoritos/", "/favoritos?x=1", "/favoritos/1", "//favoritos", "/Favoritos"):
            self.assertEqual(destino_seguro(ruim), "/conta", ruim)

    def test_pagina_registrada_e_protegida(self):
        from revaulte.revaulte import app

        rotas = set(app._unevaluated_pages) | set(getattr(app, "_pages", {}))
        self.assertIn("favoritos", rotas)

    def test_paginas_geram_codigo_sem_html_cru(self):
        from revaulte.components import botao_favorito, pagina_favoritos

        codigo = str(pagina_favoritos()) + str(botao_favorito())
        self.assertIn("Favoritos", codigo)
        self.assertNotIn("dangerouslySetInnerHTML", codigo)
        self.assertNotIn("<script", codigo)

    def test_classes_usadas_existem_no_css(self):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for classe in ("btn-outline", "favorite-box", "favorite-btn", "favorite-item", "favorite-remove"):
            self.assertRegex(css, rf"\.{classe}\b", classe)


# ---------------------------------------------------------------------------
# Arquivos XanoScript locais (sem chamar o Xano).
# ---------------------------------------------------------------------------


def ler_xs(caminho: Path) -> str:
    texto = caminho.read_text(encoding="utf-8")
    return "\n".join(l for l in texto.splitlines() if not l.strip().startswith("//"))


ENDPOINTS = ("favoritos_GET.xs", "favoritos_vehicle_id_POST.xs", "favoritos_vehicle_id_DELETE.xs")


class TestXanoFavoritos(unittest.TestCase):
    def arquivos(self):
        return {n: ler_xs(XANO / "api" / "favoritos" / n) for n in ENDPOINTS}

    def test_grupo_e_endpoints_existem(self):
        grupo = ler_xs(XANO / "api" / "favoritos" / "favoritos.xs")
        self.assertIn('canonical = "revaulte-favoritos"', grupo)
        for nome in ENDPOINTS:
            self.assertTrue((XANO / "api" / "favoritos" / nome).exists(), nome)

    def test_todos_exigem_token_e_cargo_antes_de_consultar(self):
        for nome, texto in self.arquivos().items():
            with self.subTest(nome):
                self.assertIn('auth = "user"', texto)
                self.assertIn('"Quick Start/enforce_role"', texto)
                self.assertIn('required_role: "member"', texto)
                self.assertLess(texto.index("enforce_role"), texto.index("db."))

    def test_conta_sempre_vem_do_token(self):
        for nome, texto in self.arquivos().items():
            with self.subTest(nome):
                entrada = re.search(r"input \{(.*?)\n  \}", texto, re.S).group(1)
                self.assertNotIn("user_id", entrada)
                self.assertIn("$auth.id", texto)
        for nome in ENDPOINTS[1:]:
            self.assertRegex(self.arquivos()[nome], r"favorite\.user_id == \$auth\.id")

    def test_get_so_devolve_ids_da_propria_conta(self):
        texto = self.arquivos()["favoritos_GET.xs"]
        self.assertIn("$db.favorite.user_id == $auth.id", texto)
        self.assertIn('output = ["vehicle_id", "created_at"]', texto)

    def test_post_so_aceita_veiculo_publico_e_nao_duplica(self):
        texto = self.arquivos()["favoritos_vehicle_id_POST.xs"]
        self.assertIn('$db.vehicle.status == "available"', texto)
        self.assertIn('$db.vehicle.status == "sold"', texto)
        self.assertNotIn('"draft"', texto)
        self.assertIn('error = "not_found"', texto)
        self.assertLess(texto.index("$existente"), texto.index("db.add favorite"))

    def test_delete_so_apaga_da_propria_conta(self):
        texto = self.arquivos()["favoritos_vehicle_id_DELETE.xs"]
        self.assertIn("db.bulk.delete favorite", texto)
        self.assertIn("$db.favorite.user_id == $auth.id", texto)
        self.assertEqual(texto.count("db.bulk.delete"), 1)
        self.assertNotIn("db.truncate", texto)

    def test_tabela_com_par_unico(self):
        tabela = ler_xs(XANO / "table" / "favorite.xs")
        self.assertRegex(tabela, r'btree\|unique"\s*field: \[\{name: "user_id"\}, \{name: "vehicle_id"\}\]')

    def test_catalogo_publico_continua_sem_token(self):
        for nome in ("vehicles_GET.xs", "vehicles_vehicle_id_GET.xs"):
            self.assertNotIn("auth =", ler_xs(XANO / "api" / "catalog" / nome))
