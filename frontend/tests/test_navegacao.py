# Testes da navegação (Change navegacao-principal; menu "Minha conta" da Change contas-acesso).
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from unittest.mock import AsyncMock, patch

from revaulte.components import (
    ITENS_ADMINISTRADOR,
    ITENS_ANUNCIOS,
    ITENS_AUTENTICADO,
    ITENS_EM_BREVE,
    ITENS_MENU,
    ITENS_VISITANTE,
    item_em_breve,
    itens_conta,
    painel_menu,
    topo,
)
from revaulte.revaulte import app


def codigo(componente) -> str:
    """Código gerado do componente, com os acentos (escapados como \\uXXXX) restaurados."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


def _fecha(texto: str, inicio: int) -> int:
    """Posição do parêntese que fecha o aberto em texto[inicio]."""
    nivel = 0
    for i in range(inicio, len(texto)):
        if texto[i] == "(":
            nivel += 1
        elif texto[i] == ")":
            nivel -= 1
            if nivel == 0:
                return i
    raise ValueError("parêntese sem par")


def resolver(texto: str, variavel: str, valor: bool) -> str:
    """Substitui cada `<variavel>?(A):(B)` do JSX gerado pelo ramo escolhido (A ou B)."""
    marca = f"{variavel}_rx_state_?("
    while marca in texto:
        inicio = texto.index(marca)
        abre_a = inicio + len(marca) - 1
        fecha_a = _fecha(texto, abre_a)
        assert texto[fecha_a + 1: fecha_a + 3] == ":(", "ternário inesperado"
        fecha_b = _fecha(texto, fecha_a + 2)
        ramo = texto[abre_a + 1: fecha_a] if valor else texto[fecha_a + 3: fecha_b]
        # Remove também o prefixo do nome da variável (estado e módulo).
        comeco = texto.rfind("reflex___state", 0, inicio)
        texto = texto[:comeco] + ramo + texto[fecha_b + 1:]
    return texto


def itens_visiveis(autenticado: bool, administrador: bool, atual: str = "/estoque") -> list[tuple]:
    """(rótulo, destino) dos itens da seção "Minha conta" para a sessão indicada."""
    texto = codigo(itens_conta(atual))
    texto = resolver(texto, "auth_state.autenticado", autenticado)
    texto = resolver(texto, "auth_state.administrador", administrador)
    itens = []
    posicao = texto.find('jsx("li",')
    while posicao != -1:
        abre = posicao + len("jsx")
        li = texto[abre: _fecha(texto, abre) + 1]
        destino = re.search(r'to:"([^"]+)"', li)
        if "soon-tag" in li:
            itens.append((re.search(r'jsx\("span",\{\},"([^"]+)"\)', li).group(1), "em breve"))
        elif destino:
            itens.append((re.findall(r'\},"([^"]+)"\)', li)[-1], destino.group(1)))
        elif "auth_state.sair" in li:
            itens.append(("Sair", "sair"))
        else:
            itens.append(("?", li))
        posicao = texto.find('jsx("li",', abre + len(li))
    return itens


# Change anuncios-cliente: Anunciar veículo e Meus anúncios viraram links; só Favoritos continua "Em breve".
ANUNCIOS = [("Anunciar veículo", "/anunciar"), ("Meus anúncios", "/meus-anuncios")]
EM_BREVE = [*ANUNCIOS, ("Favoritos", "em breve")]


class TestNavegacao(unittest.TestCase):
    def test_itens_da_navegacao_principal(self):
        self.assertEqual(
            ITENS_MENU,
            (("Home", "/"), ("Estoque", "/estoque"), ("Usados", "/usados"), ("Modificados", "/modificados")),
        )

    def test_toda_rota_do_menu_esta_registrada(self):
        rotas = set(app._unevaluated_pages) | set(getattr(app, "_pages", {}))
        for _, rota in ITENS_MENU:
            with self.subTest(rota=rota):
                self.assertIn("index" if rota == "/" else rota.strip("/"), rotas)
        for rota in ("catalogo", "404"):
            self.assertIn(rota, rotas)

    def test_itens_da_conta(self):
        self.assertEqual(ITENS_VISITANTE, (("Entrar", "/entrar"), ("Cadastrar", "/cadastro")))
        self.assertEqual(ITENS_AUTENTICADO, (("Minha conta", "/conta"),))
        self.assertEqual(ITENS_ADMINISTRADOR, (("Painel administrativo", "/admin"),))
        self.assertEqual(ITENS_ANUNCIOS, (("Anunciar veículo", "/anunciar"), ("Meus anúncios", "/meus-anuncios")))
        self.assertEqual(ITENS_EM_BREVE, ("Favoritos",))

    def test_rotas_da_conta_estao_registradas(self):
        rotas = set(app._unevaluated_pages) | set(getattr(app, "_pages", {}))
        for _, rota in ITENS_VISITANTE + ITENS_AUTENTICADO + ITENS_ADMINISTRADOR + ITENS_ANUNCIOS:
            with self.subTest(rota=rota):
                self.assertIn(rota.strip("/"), rotas)

    def test_itens_em_breve_nao_sao_links(self):
        for rotulo in ITENS_EM_BREVE:
            with self.subTest(rotulo=rotulo):
                gerado = codigo(item_em_breve(rotulo))
                self.assertIn(rotulo, gerado)
                self.assertIn("Em breve", gerado)
                self.assertIn("aria-disabled", gerado)
                self.assertNotIn("href", gerado)
                self.assertNotIn("to:", gerado)
                self.assertNotIn("onClick", gerado)

    def test_pagina_atual_marcada_somente_uma_vez(self):
        for _, rota in ITENS_MENU:
            with self.subTest(rota=rota):
                # O topo contém a navegação do cabeçalho e a do painel: uma marca em cada.
                self.assertEqual(codigo(topo(rota)).count("aria-current"), 2)
                self.assertEqual(codigo(painel_menu(rota)).count("aria-current"), 1)

    def test_painel_tem_as_duas_secoes(self):
        gerado = codigo(painel_menu("/estoque"))
        for texto in ("Navegação", "Minha conta", "Entrar", "Cadastrar", "Sair", "Painel administrativo",
                      *ITENS_EM_BREVE, "Home", "Estoque", "Usados", "Modificados"):
            self.assertIn(texto, gerado)


class TestMenuDaConta(unittest.TestCase):
    """Itens visíveis da seção "Minha conta" para cada tipo de sessão."""

    def test_visitante(self):
        self.assertEqual(itens_visiveis(False, False),
                         [("Entrar", "/entrar"), ("Cadastrar", "/cadastro"), *EM_BREVE])

    def test_cliente(self):
        self.assertEqual(itens_visiveis(True, False), [("Minha conta", "/conta"), *EM_BREVE, ("Sair", "sair")])

    def test_administrador(self):
        self.assertEqual(itens_visiveis(True, True),
                         [("Minha conta", "/conta"), ("Painel administrativo", "/admin"), *EM_BREVE, ("Sair", "sair")])

    def test_painel_administrativo_nunca_para_visitante(self):
        # Mesmo com "administrador" verdadeiro, sem sessão confirmada o item não aparece.
        self.assertNotIn(("Painel administrativo", "/admin"), itens_visiveis(False, True))

    def test_resolvedor_encontra_as_duas_condicoes(self):
        texto = codigo(itens_conta("/estoque"))
        self.assertEqual(texto.count("auth_state.autenticado_rx_state_?("), 2)
        self.assertEqual(texto.count("auth_state.administrador_rx_state_?("), 1)

    def test_sair_fecha_o_menu_e_chama_o_logout(self):
        gerado = codigo(itens_conta("/estoque"))
        trecho = gerado[gerado.index('"menu-account-link menu-logout"') - 20:]
        trecho = trecho[: trecho.index('"Sair"')]
        self.assertLess(trecho.index("menu_state.fechar_menu"), trecho.index("auth_state.sair"))
        self.assertIn('type:"button"', trecho)

    def test_links_da_conta_fecham_o_menu(self):
        gerado = codigo(itens_conta("/estoque"))
        for rota in ("/entrar", "/cadastro", "/conta", "/admin", "/anunciar", "/meus-anuncios"):
            with self.subTest(rota=rota):
                link = gerado[: gerado.index(f'to:"{rota}"')]
                link = link[link.rindex("ReactRouterLink"):]
                self.assertIn("menu_state.fechar_menu", link)

    def test_pagina_atual_da_conta_marcada(self):
        gerado = codigo(itens_conta("/conta"))
        self.assertEqual(gerado.count('"aria-current":"page"'), 1)
        self.assertIn('className:"menu-account-link current"', gerado)

    def test_estilos_do_menu(self):
        from pathlib import Path

        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for seletor in (".menu-account-link {", ".menu-account-link.current {", ".menu-logout {"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor, css)


class TestCompilacaoDasPaginas(unittest.TestCase):
    """Regressão de 21/11/2026: duas funções item_conta no mesmo módulo; a segunda (da página
    /conta, com 2 parâmetros) sobrescrevia a do menu e o Reflex falhava em todas as páginas com
    "TypeError: item_conta() takes 2 positional arguments but 3 were given"."""

    def test_nenhuma_definicao_repetida_nos_modulos(self):
        import ast
        import collections
        from pathlib import Path

        pasta = Path(__file__).resolve().parents[1] / "revaulte"
        for arquivo in sorted(pasta.glob("*.py")):
            with self.subTest(arquivo=arquivo.name):
                arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
                nomes = collections.Counter(
                    no.name for no in arvore.body if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                )
                self.assertEqual([nome for nome, total in nomes.items() if total > 1], [])

    def test_todas_as_paginas_registradas_sao_geradas(self):
        for rota, pagina in app._unevaluated_pages.items():
            with self.subTest(rota=rota):
                componente = pagina.component() if callable(pagina.component) else pagina.component
                self.assertTrue(str(componente))


class TestVerificacaoDeSessao(unittest.IsolatedAsyncioTestCase):
    """verificar_sessao nas páginas públicas: chamadas ao Xano só quando necessárias."""

    def test_paginas_publicas_conferem_a_sessao(self):
        for rota in ("index", "estoque", "usados", "modificados", "veiculo/[veiculo_id]", "404"):
            with self.subTest(rota=rota):
                self.assertIn("verificar_sessao", repr(app._unevaluated_pages[rota].on_load))

    def test_paginas_da_conta_nao_repetem_a_conferencia(self):
        # /conta e /admin já chamam auth/me pelo exigir_*; /entrar e /cadastro não precisam.
        for rota in ("entrar", "cadastro", "conta", "admin", "catalogo"):
            with self.subTest(rota=rota):
                self.assertNotIn("verificar_sessao", repr(app._unevaluated_pages[rota].on_load))

    async def verificar(self, token, verificado=False, resposta=None):
        from revaulte.auth import AuthState, Usuario

        class Estado:
            pass

        estado = Estado()
        estado.token = token
        estado.verificado = verificado
        estado.usuario = Usuario(id=3, nome="Anterior", perfil="admin") if verificado else Usuario()
        estado._encerrar = lambda: AuthState._encerrar(estado)
        chamada = AsyncMock(return_value=resposta)
        with patch("revaulte.auth.chamar_xano", chamada):
            eventos = await AuthState.verificar_sessao.fn(estado)
        return estado, chamada, eventos

    async def test_visitante_nao_chama_o_xano(self):
        estado, chamada, _ = await self.verificar("")
        chamada.assert_not_called()
        self.assertEqual(estado.usuario.id, 0)

    async def test_sessao_ja_conferida_nao_chama_o_xano(self):
        estado, chamada, _ = await self.verificar("token-de-teste", verificado=True)
        chamada.assert_not_called()
        self.assertEqual(estado.usuario.perfil, "admin")

    async def test_primeira_conferencia_usa_o_perfil_do_backend(self):
        corpo = {"id": 5, "name": "Teste", "email": "t@exemplo.com", "role": "member"}
        estado, chamada, _ = await self.verificar("token-de-teste", resposta=(200, corpo))
        chamada.assert_awaited_once()
        self.assertTrue(chamada.await_args.args[1].endswith("/auth/me"))
        self.assertEqual((estado.usuario.perfil, estado.verificado), ("member", True))

    async def test_token_recusado_volta_a_visitante(self):
        estado, _, eventos = await self.verificar("token-de-teste", resposta=(401, None))
        self.assertEqual((estado.token, estado.usuario.id, estado.verificado), ("", 0, False))
        self.assertIn("revaulte_sessao", repr(eventos))


if __name__ == "__main__":
    unittest.main()
