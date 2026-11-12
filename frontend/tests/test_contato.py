# Testes do contato com o anunciante (Change contato-vendedor).
# Os anunciantes e números abaixo são simulados e existem só nestes testes.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from urllib.parse import parse_qs, urlparse

from revaulte.components import bloco_anunciante, pagina_veiculo
from revaulte.state import link_whatsapp, mensagem_whatsapp, preparar_anunciante, preparar_detalhe

NUMERO_SIMULADO = "5511900000000"


def codigo(componente) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


def detalhe(**extra) -> dict:
    base = {
        "id": 3, "brand": "Volkswagen", "model": "Gol", "version": "GTI Turbo", "year": 1994,
        "condition": "used", "mileage": 85000, "price": 75000, "is_modified": True,
        "status": "available", "cover_image_url": None, "color": "", "engine": "",
        "transmission": "", "description": "", "modifications": [], "seller": None,
    }
    base.update(extra)
    return base


class TestLink(unittest.TestCase):
    def test_mensagem_identifica_o_veiculo_sem_endereco(self):
        msg = mensagem_whatsapp("Volkswagen Gol GTI Turbo", "1994")
        self.assertEqual(msg, "Olá! Tenho interesse no Volkswagen Gol GTI Turbo 1994 anunciado na Revaulte.")
        self.assertNotIn("localhost", msg)
        self.assertNotIn("http", msg)

    def test_link_codificado(self):
        link = link_whatsapp(NUMERO_SIMULADO, "Ford Maverick GT V8", "1976")
        partes = urlparse(link)
        self.assertEqual((partes.scheme, partes.netloc, partes.path), ("https", "wa.me", "/" + NUMERO_SIMULADO))
        self.assertEqual(
            parse_qs(partes.query)["text"],
            ["Olá! Tenho interesse no Ford Maverick GT V8 1976 anunciado na Revaulte."],
        )
        self.assertNotIn(" ", link)

    def test_numeros_invalidos_nao_geram_link(self):
        for numero in (None, "", "11900000000", "55119000000000", "+5511900000000",
                       "55 11 900000000", "551190000000a", 5511900000000, "５５１１９０００００００"):
            with self.subTest(numero=numero):
                self.assertEqual(link_whatsapp(numero, "Carro", "2000"), "")


class TestAnunciante(unittest.TestCase):
    def test_autorizado(self):
        nome, link = preparar_anunciante(
            {"display_name": "  Anunciante   Simulado ", "whatsapp": NUMERO_SIMULADO}, "Carro", "2000", False
        )
        self.assertEqual(nome, "Anunciante Simulado")
        self.assertTrue(link.startswith(f"https://wa.me/{NUMERO_SIMULADO}?text="))

    def test_sem_autorizacao_mostra_so_o_nome(self):
        # O backend envia whatsapp nulo quando o anunciante não autorizou.
        self.assertEqual(
            preparar_anunciante({"display_name": "Anunciante Simulado", "whatsapp": None}, "Carro", "2000", False),
            ("Anunciante Simulado", ""),
        )

    def test_sem_anunciante(self):
        self.assertEqual(preparar_anunciante(None, "Carro", "2000", False), ("", ""))

    def test_sem_nome_nao_ha_anunciante_nem_contato(self):
        self.assertEqual(
            preparar_anunciante({"display_name": " ", "whatsapp": NUMERO_SIMULADO}, "Carro", "2000", False),
            ("", ""),
        )

    def test_vendido_nunca_recebe_contato(self):
        seller = {"display_name": "Anunciante Simulado", "whatsapp": NUMERO_SIMULADO}
        self.assertEqual(preparar_anunciante(seller, "Carro", "2000", True), ("", ""))

    def test_anunciante_invalido(self):
        with self.assertRaises(ValueError):
            preparar_anunciante("x", "Carro", "2000", False)

    def test_detalhe_completo(self):
        d = preparar_detalhe(detalhe(seller={"display_name": "Anunciante Simulado", "whatsapp": NUMERO_SIMULADO}))
        self.assertEqual(d.anunciante, "Anunciante Simulado")
        self.assertIn("Volkswagen%20Gol%20GTI%20Turbo%201994", d.link_whatsapp)

    def test_resposta_atual_do_xano_sem_campo_seller(self):
        # Antes do envio, o endpoint não tem "seller": a página mostra "Contato não disponível".
        d = preparar_detalhe({k: v for k, v in detalhe().items() if k != "seller"})
        self.assertEqual((d.anunciante, d.link_whatsapp), ("", ""))


class TestComponentes(unittest.TestCase):
    def test_link_externo_seguro(self):
        gerado = codigo(bloco_anunciante())
        self.assertIn('target:"_blank"', gerado)
        self.assertIn('rel:"noopener noreferrer"', gerado)
        self.assertIn("Conversar no WhatsApp", gerado)
        self.assertIn("Contato não disponível", gerado)
        self.assertIn("Anunciado por", gerado)

    def test_demonstrativo_removido(self):
        gerado = codigo(pagina_veiculo())
        self.assertNotIn("Tenho interesse", gerado)
        self.assertNotIn("mostrar_interesse", gerado)


if __name__ == "__main__":
    unittest.main()
