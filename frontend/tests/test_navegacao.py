# Testes da navegação (Change navegacao-principal).
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest

from revaulte.components import ITENS_CONTA, ITENS_MENU, item_em_breve, painel_menu, topo
from revaulte.revaulte import app


def codigo(componente) -> str:
    """Código gerado do componente, com os acentos (escapados como \\uXXXX) restaurados."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


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
        self.assertEqual(
            ITENS_CONTA,
            ("Meu perfil", "Anunciar veículo", "Meus anúncios", "Favoritos", "Entrar / Cadastrar"),
        )

    def test_itens_em_breve_nao_sao_links(self):
        for rotulo in ITENS_CONTA:
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
        for texto in ("Navegação", "Minha conta", *ITENS_CONTA, "Home", "Estoque", "Usados", "Modificados"):
            self.assertIn(texto, gerado)


if __name__ == "__main__":
    unittest.main()
