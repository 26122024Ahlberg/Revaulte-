# Testes da página inicial (Change pagina-inicial).
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from pathlib import Path

from revaulte.components import (
    PILARES_PROPOSTA,
    SLIDES_CARROSSEL,
    carrossel_inicial,
    pagina_inicial,
    secao_destaques,
    secao_proposta,
)
from revaulte.revaulte import app
from revaulte.state import TOTAL_SLIDES, CarrosselState

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Afirmações que a Home não pode fazer sem definição na documentação do projeto.
TERMOS_PROIBIDOS = (
    "garantia", "garantido", "laudo", "vistoria", "procedência", "financiamento",
    "parcela", "telefone", "whatsapp", "e-mail", "@", "endereço", "homologad", "legalizad",
)


def codigo(componente) -> str:
    """Código gerado do componente, com os acentos (escapados como \\uXXXX) restaurados."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


class TestPaginaInicial(unittest.TestCase):
    def test_rota_raiz_registrada(self):
        self.assertIn("index", app._unevaluated_pages)

    def test_slides_na_ordem_pedida(self):
        self.assertEqual([s["categoria"] for s in SLIDES_CARROSSEL], ["Esportivos", "Modificados", "Clássicos"])
        self.assertEqual(len(SLIDES_CARROSSEL), TOTAL_SLIDES)

    def test_carrossel(self):
        gerado = codigo(carrossel_inicial())
        for slide in SLIDES_CARROSSEL:
            with self.subTest(slide=slide["categoria"]):
                self.assertIn(f'src:"{slide["imagem"]}"', gerado)
                self.assertIn(f'alt:"{slide["alt"]}"', gerado)
                self.assertIn(slide["titulo"], gerado)
        self.assertEqual(gerado.count("Explorar estoque"), TOTAL_SLIDES)
        self.assertEqual(gerado.count('to:"/estoque"'), TOTAL_SLIDES)
        self.assertIn('"aria-label":"Slide anterior"', gerado)
        self.assertIn('"aria-label":"Próximo slide"', gerado)
        self.assertIn('"aria-roledescription":"carrossel"', gerado)
        self.assertEqual(gerado.count('"aria-roledescription":"slide"'), TOTAL_SLIDES)
        self.assertEqual(gerado.count('jsx("h1"'), 1)

    def test_imagens_do_carrossel_existem_e_sao_leves(self):
        for slide in SLIDES_CARROSSEL:
            imagem = ASSETS / slide["imagem"].lstrip("/")
            with self.subTest(imagem=imagem.name):
                self.assertTrue(imagem.is_file())
                self.assertLess(imagem.stat().st_size, 420_000)
        self.assertFalse((ASSETS / "hero.jpg").exists())

    def test_navegacao_circular(self):
        ev = CarrosselState.event_handlers
        estado = type("Estado", (), {})()
        estado.indice = 0
        ev["proximo"].fn(estado)
        self.assertEqual(estado.indice, 1)
        ev["proximo"].fn(estado)
        ev["proximo"].fn(estado)
        self.assertEqual(estado.indice, 0)
        ev["anterior"].fn(estado)
        self.assertEqual(estado.indice, 2)
        ev["ir_para"].fn(estado, 1)
        self.assertEqual(estado.indice, 1)
        for invalido in (-1, 3, "2", None):
            ev["ir_para"].fn(estado, invalido)
            self.assertEqual(estado.indice, 1)
        ev["reiniciar"].fn(estado)
        self.assertEqual(estado.indice, 0)

    def test_destaques_com_link_para_o_estoque(self):
        gerado = codigo(secao_destaques())
        self.assertIn("Veículos em destaque", gerado)
        self.assertIn("Ver todo o estoque", gerado)
        self.assertIn("Não há destaques no momento.", gerado)
        self.assertIn("Tentar novamente", gerado)
        self.assertIn("cartoes_exibidos", gerado)

    def test_proposta_sem_promessas_nao_definidas(self):
        self.assertEqual(len(PILARES_PROPOSTA), 3)
        textos = codigo(secao_proposta()) + codigo(carrossel_inicial())
        textos_visiveis = " ".join(re.findall(r'"([^"]*)"', textos)).lower()
        for termo in TERMOS_PROIBIDOS:
            with self.subTest(termo=termo):
                self.assertNotIn(termo, textos_visiveis)

    def test_nome_ghostpay_nao_aparece(self):
        self.assertNotIn("ghostpay", codigo(pagina_inicial()).lower())


if __name__ == "__main__":
    unittest.main()
