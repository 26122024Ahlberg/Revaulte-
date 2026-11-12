# Testes da Change visual-paginas-internas.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from pathlib import Path

from revaulte.components import (
    BANNERS_ESTOQUE,
    ROTA_ESTOQUE,
    ROTA_MODIFICADOS,
    ROTA_USADOS,
    SLIDES_CARROSSEL,
    pagina_estoque,
    pagina_inicial,
    pagina_veiculo,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def codigo(componente) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


class TestPaginasInternas(unittest.TestCase):
    def test_banner_em_cada_pagina_de_estoque(self):
        for rota, titulo in ((ROTA_ESTOQUE, "Estoque"), (ROTA_USADOS, "Usados"), (ROTA_MODIFICADOS, "Modificados")):
            with self.subTest(rota=rota):
                gerado = codigo(pagina_estoque(rota, titulo, "vazio"))
                imagem, texto, chave = BANNERS_ESTOQUE[rota]
                self.assertIn(f'className:"page-banner is-{chave}"', gerado)
                self.assertIn(f'src:"{imagem}"', gerado)
                self.assertIn(texto, gerado)
                self.assertIn(f'jsx("h1",{{className:"page-banner-title"}},"{titulo}")', gerado)
                self.assertEqual(gerado.count('jsx("h1"'), 1)
                self.assertIn('className:"inner-page"', gerado)
                # A foto do banner é decorativa.
                self.assertIn('alt:"","aria-hidden":"true",className:"page-banner-image"', gerado)

    def test_imagens_proprias_leves_e_diferentes_da_home(self):
        imagens_home = {slide["imagem"] for slide in SLIDES_CARROSSEL}
        banners = [imagem for imagem, _, _ in BANNERS_ESTOQUE.values()]
        self.assertEqual(len(set(banners)), 3)
        for imagem in banners:
            with self.subTest(imagem=imagem):
                arquivo = ASSETS / imagem.lstrip("/")
                self.assertTrue(arquivo.is_file())
                self.assertLess(arquivo.stat().st_size, 420_000)
                self.assertNotIn(imagem, imagens_home)

    def test_home_nao_usa_os_estilos_internos(self):
        gerado = codigo(pagina_inicial())
        for classe in ("inner-page", "page-banner", "vehicle-backdrop"):
            self.assertNotIn(classe, gerado)

    def test_pagina_do_veiculo_com_fundo_decorativo(self):
        gerado = codigo(pagina_veiculo())
        self.assertIn('className:"inner-page inner-vehicle"', gerado)
        self.assertIn('alt:"","aria-hidden":"true",className:"vehicle-backdrop"', gerado)


if __name__ == "__main__":
    unittest.main()
