# Testes da preparação dos cartões e dos recortes do estoque.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import dataclasses
import unittest

from revaulte.state import (
    IMAGEM_PROVISORIA,
    CartaoVeiculo,
    CatalogState,
    aplicar_recorte,
    endereco_capa,
    formatar_preco,
    formatar_quilometragem,
    preparar_cartao,
)

OPALA = {
    "id": 1,
    "brand": "Chevrolet",
    "model": "Opala",
    "version": "SS",
    "year": 1978,
    "condition": "used",
    "mileage": 72000,
    "price": 118900,
    "is_modified": False,
    "status": "available",
    "cover_image_url": "https://images.pexels.com/photos/24536462/pexels-photo-24536462.jpeg",
}


def veiculo(**alteracoes):
    return {**OPALA, **alteracoes}


class TestFormatacao(unittest.TestCase):
    def test_preco_em_reais(self):
        self.assertEqual(formatar_preco(118900), "R$ 118.900,00")
        self.assertEqual(formatar_preco(75000.5), "R$ 75.000,50")
        self.assertEqual(formatar_preco(1234567.891), "R$ 1.234.567,89")
        self.assertEqual(formatar_preco(0), "R$ 0,00")
        self.assertEqual(formatar_preco(999.995), "R$ 1.000,00")

    def test_quilometragem(self):
        self.assertEqual(formatar_quilometragem(72000), "72.000 km")
        self.assertEqual(formatar_quilometragem(0), "0 km")
        self.assertEqual(formatar_quilometragem(1250300), "1.250.300 km")

    def test_numero_invalido(self):
        for valor in (None, True, "abc", "nan", [], {}):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                formatar_preco(valor)


class TestPrepararCartao(unittest.TestCase):
    def test_veiculo_usado_completo(self):
        cartao = preparar_cartao(OPALA)
        self.assertEqual(cartao.titulo, "Chevrolet Opala SS")
        self.assertEqual(cartao.ano, "1978")
        self.assertEqual(cartao.quilometragem, "72.000 km")
        self.assertEqual(cartao.condicao, "Usado")
        self.assertEqual(cartao.preco, "R$ 118.900,00")
        self.assertFalse(cartao.modificado)
        self.assertFalse(cartao.vendido)
        self.assertEqual(cartao.capa, OPALA["cover_image_url"])
        self.assertEqual(cartao.id, 1)
        self.assertTrue(cartao.usado)

    def test_veiculo_novo(self):
        self.assertEqual(preparar_cartao(veiculo(condition="new")).condicao, "Novo")

    def test_sem_versao(self):
        for versao in (None, "", "   "):
            with self.subTest(versao=versao):
                self.assertEqual(preparar_cartao(veiculo(version=versao)).titulo, "Chevrolet Opala")
        sem_campo = dict(OPALA)
        del sem_campo["version"]
        self.assertEqual(preparar_cartao(sem_campo).titulo, "Chevrolet Opala")

    def test_titulo_sem_espacos_sobrando(self):
        cartao = preparar_cartao(veiculo(brand=" Ford ", model="Maverick", version="GT  V8 "))
        self.assertEqual(cartao.titulo, "Ford Maverick GT V8")

    def test_selos(self):
        casos = [
            ({"is_modified": False, "status": "available"}, (False, False)),
            ({"is_modified": True, "status": "available"}, (True, False)),
            ({"is_modified": False, "status": "sold"}, (False, True)),
            ({"is_modified": True, "status": "sold"}, (True, True)),
            ({"is_modified": True, "status": "available", "condition": "new"}, (True, False)),
            # Somente o valor booleano verdadeiro indica modificado.
            ({"is_modified": "true", "status": "available"}, (False, False)),
        ]
        for campos, (modificado, vendido) in casos:
            with self.subTest(campos=campos):
                cartao = preparar_cartao(veiculo(**campos))
                self.assertEqual((cartao.modificado, cartao.vendido), (modificado, vendido))

    def test_capa(self):
        for url in (None, "", "  ", "ftp://x/y.jpg", "javascript:alert(1)", "/local.jpg", "https://"):
            with self.subTest(url=url):
                self.assertEqual(preparar_cartao(veiculo(cover_image_url=url)).capa, IMAGEM_PROVISORIA)
        self.assertEqual(endereco_capa("  http://exemplo.com/a.jpg "), "http://exemplo.com/a.jpg")

    def test_dados_obrigatorios_invalidos(self):
        for campos in (
            {"condition": "seminovo"},
            {"year": "1978"},
            {"year": None},
            {"price": None},
            {"mileage": "muito"},
            {"brand": "", "model": None, "version": None},
            {"id": None},
            {"id": "1"},
            {"id": True},
        ):
            with self.subTest(campos=campos), self.assertRaises(ValueError):
                preparar_cartao(veiculo(**campos))

    def test_cartao_contem_somente_dados_de_exibicao(self):
        campos = {f.name for f in dataclasses.fields(CartaoVeiculo)}
        self.assertEqual(
            campos,
            {"id", "titulo", "ano", "quilometragem", "condicao", "preco", "usado", "modificado", "vendido", "capa"},
        )


class TestImagemProvisoria(unittest.TestCase):
    """Troca da capa que falhou ao carregar, localizada pelo id do veículo."""

    def setUp(self):
        self.trocar = CatalogState.event_handlers["usar_imagem_provisoria"].fn
        a = preparar_cartao(OPALA)
        b = preparar_cartao(veiculo(id=2, cover_image_url="https://exemplo.invalido/b.jpg"))
        self.estado = type("Estado", (), {})()
        self.estado.cartoes = [a, b]

    def test_troca_somente_o_cartao_com_falha(self):
        capa_a = self.estado.cartoes[0].capa
        self.trocar(self.estado, 2, "https://exemplo.invalido/b.jpg")
        self.assertEqual(self.estado.cartoes[1].capa, IMAGEM_PROVISORIA)
        self.assertEqual(self.estado.cartoes[0].capa, capa_a)

    def test_ignora_erro_atrasado_ou_id_inexistente(self):
        antes = list(self.estado.cartoes)
        self.trocar(self.estado, 2, "https://outra-capa/antiga.jpg")
        self.trocar(self.estado, 99, "https://exemplo.invalido/b.jpg")
        self.assertEqual(self.estado.cartoes, antes)

    def test_troca_vale_com_qualquer_recorte(self):
        # O cartão com falha é o 1º exibido em "modificados", mas o 2º da lista completa.
        self.estado.cartoes[1] = dataclasses.replace(self.estado.cartoes[1], modificado=True)
        exibidos = aplicar_recorte(self.estado.cartoes, "modificados")
        self.assertEqual([c.id for c in exibidos], [2])
        self.trocar(self.estado, exibidos[0].id, exibidos[0].capa)
        self.assertEqual(self.estado.cartoes[1].capa, IMAGEM_PROVISORIA)
        self.assertNotEqual(self.estado.cartoes[0].capa, IMAGEM_PROVISORIA)


class TestRecortes(unittest.TestCase):
    """Páginas /estoque, /usados e /modificados (Change navegacao-principal)."""

    def setUp(self):
        self.cartoes = [
            preparar_cartao(veiculo(id=1)),  # usado original disponível
            preparar_cartao(veiculo(id=2, condition="new")),  # novo original
            preparar_cartao(veiculo(id=3, is_modified=True, status="sold")),  # usado modificado vendido
            preparar_cartao(veiculo(id=4, condition="new", is_modified=True)),  # novo modificado
        ]

    def ids(self, recorte):
        return [c.id for c in aplicar_recorte(self.cartoes, recorte)]

    def test_todos(self):
        self.assertEqual(self.ids("todos"), [1, 2, 3, 4])

    def test_usados(self):
        self.assertEqual(self.ids("usados"), [1, 3])

    def test_modificados_inclui_vendido_e_novo(self):
        self.assertEqual(self.ids("modificados"), [3, 4])

    def test_recorte_desconhecido_equivale_a_todos(self):
        self.assertEqual(self.ids("rascunho"), [1, 2, 3, 4])

    def test_recorte_vazio(self):
        originais = [c for c in self.cartoes if not c.modificado]
        self.assertEqual(aplicar_recorte(originais, "modificados"), [])

    def test_destaques_tres_disponiveis_mais_recentes(self):
        # Cinco disponíveis, do mais recente (id 10) para o mais antigo (id 14).
        cartoes = [preparar_cartao(veiculo(id=i)) for i in range(10, 15)]
        self.assertEqual([c.id for c in aplicar_recorte(cartoes, "destaques")], [10, 11, 12])

    def test_destaques_ignoram_vendido_mais_recente(self):
        cartoes = [preparar_cartao(veiculo(id=1, status="sold"))] + [
            preparar_cartao(veiculo(id=i)) for i in range(2, 6)
        ]
        self.assertEqual([c.id for c in aplicar_recorte(cartoes, "destaques")], [2, 3, 4])

    def test_destaques_com_menos_de_tres(self):
        cartoes = [preparar_cartao(veiculo(id=1)), preparar_cartao(veiculo(id=2, status="sold")), preparar_cartao(veiculo(id=3))]
        self.assertEqual([c.id for c in aplicar_recorte(cartoes, "destaques")], [1, 3])

    def test_destaques_sem_disponiveis(self):
        cartoes = [preparar_cartao(veiculo(id=1, status="sold"))]
        self.assertEqual(aplicar_recorte(cartoes, "destaques"), [])

    def test_abrir_pagina_define_recorte_e_descarta_lista_anterior(self):
        abrir = CatalogState.event_handlers["abrir_pagina"].fn
        estado = type("Estado", (), {})()
        estado.cartoes, estado.situacao, estado.recorte = list(self.cartoes), "lista", "todos"
        abrir(estado, "usados")
        self.assertEqual((estado.recorte, estado.situacao, estado.cartoes), ("usados", "carregando", []))
        abrir(estado, "qualquer")
        self.assertEqual(estado.recorte, "todos")


if __name__ == "__main__":
    unittest.main()
