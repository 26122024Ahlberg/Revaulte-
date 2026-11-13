# Testes da Change animacoes-interface.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from pathlib import Path

from revaulte.components import regiao_detalhe, regiao_estoque

CSS = (Path(__file__).resolve().parent.parent / "assets" / "styles.css").read_text()


def codigo(componente) -> str:
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


class TestAnimacoes(unittest.TestCase):
    def test_carregamento_com_texto_e_anel_decorativo(self):
        for gerado, texto in (
            (codigo(regiao_estoque("vazio")), "Carregando veículos…"),
            (codigo(regiao_detalhe()), "Carregando veículo…"),
        ):
            with self.subTest(texto=texto):
                self.assertIn(texto, gerado)
                self.assertIn('{"aria-hidden":"true",className:"spinner"}', gerado)
                self.assertIn('"aria-live":"polite"', gerado)

    def test_movimento_reduzido_desativa_animacoes(self):
        blocos = re.findall(r"@media \(prefers-reduced-motion: reduce\) \{(.*?)\n\}", CSS, re.S)
        tudo = " ".join(blocos)
        self.assertIn("animation: none !important", tudo)
        self.assertIn("transition: none !important", tudo)
        self.assertIn("transform: none !important", tudo)

    def test_movimento_reduzido_alcanca_pseudoelementos(self):
        # A névoa do estoque anima um ::before; `*` sozinho não o alcança.
        bloco = re.search(r"@media \(prefers-reduced-motion: reduce\) \{(.*?)\n\}", CSS, re.S).group(1)
        seletor = re.search(r"([^{}]*)\{[^{}]*animation: none !important", bloco).group(1)
        seletor = re.sub(r"/\*.*?\*/", "", seletor, flags=re.S)
        partes = {s.strip() for s in seletor.split(",")}
        self.assertTrue({"*", "*::before", "*::after"} <= partes, partes)

    def test_entradas_curtas(self):
        # Entradas novas: no máximo 0,4 s de duração + 0,15 s de atraso nos cartões.
        for nome in ("revaulte-rise", "revaulte-drop"):
            for duracao in re.findall(rf"animation: {nome} ([\d.]+)s", CSS):
                with self.subTest(nome=nome):
                    self.assertLessEqual(float(duracao), 0.4)
        atrasos = [float(a) for a in re.findall(r"animation-delay: ([\d.]+)s", CSS)]
        self.assertLessEqual(max(atrasos), 0.24)


if __name__ == "__main__":
    unittest.main()
