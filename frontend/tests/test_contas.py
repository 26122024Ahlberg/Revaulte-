# Testes da lógica de contas (Change contas-acesso). Dados simulados, sem pessoas reais.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import unittest
from datetime import date
from pathlib import Path

from revaulte.auth import (
    ROTA_CONTA,
    cpf_valido,
    destino_seguro,
    ler_proximo,
    mensagem_erro_cadastro,
    preparar_linhas_usuarios,
    preparar_usuario,
    problema_senha,
    validar_cadastro,
    validar_login,
)

# CPF de teste gerado com dígitos verificadores válidos (não pertence a ninguém conhecido).
CPF_TESTE = "52998224725"
HOJE = date(2026, 11, 12)


def formulario(**extra) -> dict:
    base = {
        "nome": "  Pessoa   de Teste ", "email": "Teste@Exemplo.com", "cpf": "529.982.247-25",
        "telefone": "(11) 90000-0000", "nascimento": "1990-05-10", "endereco": "Rua de Teste, 100",
        "senha": "senha123", "confirmacao": "senha123",
    }
    base.update(extra)
    return base


class TestValidacao(unittest.TestCase):
    def test_cpf(self):
        self.assertTrue(cpf_valido(CPF_TESTE))
        for invalido in ("52998224724", "11111111111", "123", "", "5299822472a"):
            with self.subTest(cpf=invalido):
                self.assertFalse(cpf_valido(invalido))

    def test_senha(self):
        self.assertEqual(problema_senha("senha123"), "")
        self.assertIn("8 caracteres", problema_senha("a1"))
        self.assertIn("letra e um número", problema_senha("somenteletras"))
        self.assertIn("letra e um número", problema_senha("12345678"))

    def test_cadastro_valido_normaliza(self):
        dados, erro = validar_cadastro(formulario(), HOJE)
        self.assertEqual(erro, "")
        self.assertEqual(dados["name"], "Pessoa de Teste")
        self.assertEqual(dados["email"], "teste@exemplo.com")
        self.assertEqual(dados["cpf"], CPF_TESTE)
        self.assertEqual(dados["phone"], "11900000000")
        self.assertEqual(dados["birth_date"], "1990-05-10")
        self.assertNotIn("role", dados)  # o perfil nunca vem do formulário

    def test_cadastro_invalido(self):
        casos = {
            "nome": ("x", "nome"),
            "email": ("sem-arroba", "e-mail"),
            "cpf": ("111.111.111-11", "CPF"),
            "telefone": ("1234", "telefone"),
            "nascimento": ("2030-01-01", "nascimento"),
            "endereco": ("abc", "endereço"),
        }
        for campo, (valor, trecho) in casos.items():
            with self.subTest(campo=campo):
                dados, erro = validar_cadastro(formulario(**{campo: valor}), HOJE)
                self.assertIsNone(dados)
                self.assertIn(trecho, erro)
        dados, erro = validar_cadastro(formulario(confirmacao="outra123"), HOJE)
        self.assertIsNone(dados)
        self.assertEqual(erro, "As senhas não coincidem.")

    def test_data_impossivel(self):
        self.assertIsNone(validar_cadastro(formulario(nascimento="1990-02-31"), HOJE)[0])
        self.assertIsNone(validar_cadastro(formulario(nascimento="1899-12-31"), HOJE)[0])

    def test_login(self):
        self.assertEqual(validar_login({"email": " A@B.com ", "senha": "x"})[0], {"email": "a@b.com", "password": "x"})
        self.assertIsNone(validar_login({"email": "a@b.com", "senha": ""})[0])


class TestErrosEDestinos(unittest.TestCase):
    def test_mensagens_do_backend(self):
        self.assertIn("e-mail já está cadastrado", mensagem_erro_cadastro(403, {"message": "email_taken"}))
        self.assertIn("CPF já está cadastrado", mensagem_erro_cadastro(403, {"message": "cpf_taken"}))
        self.assertIn("conexão", mensagem_erro_cadastro(0, None))

    def test_destino_somente_interno(self):
        self.assertEqual(destino_seguro("/admin"), "/admin")
        for externo in ("https://exemplo.com", "//exemplo.com", "/\\exemplo.com", "", None, "/entrar"):
            with self.subTest(destino=externo):
                self.assertEqual(destino_seguro(externo), ROTA_CONTA)

    def test_ler_proximo(self):
        self.assertEqual(ler_proximo({}, "/entrar?proximo=/conta"), "/conta")
        self.assertEqual(ler_proximo({"proximo": "/admin"}, ""), "/admin")


class TestUsuario(unittest.TestCase):
    def test_perfil_desconhecido_vira_cliente(self):
        u = preparar_usuario({"id": 3, "name": "Teste", "email": "t@e.com", "role": "superuser"})
        self.assertEqual((u.perfil, u.rotulo_perfil), ("member", "Cliente"))

    def test_administrador(self):
        u = preparar_usuario({"id": 1, "name": "Adm", "email": "a@e.com", "role": "admin", "created_at": 1762905600000})
        self.assertEqual(u.rotulo_perfil, "Administrador")
        self.assertRegex(u.desde, r"\d{2}/\d{2}/\d{4}")

    def test_lista_ignora_campos_sensiveis(self):
        linhas = preparar_linhas_usuarios(
            [{"id": 2, "name": "T", "email": "t@e.com", "role": "member", "cpf": CPF_TESTE, "password": "x"}]
        )
        self.assertEqual(len(linhas), 1)
        self.assertNotIn(CPF_TESTE, repr(linhas))
        with self.assertRaises(ValueError):
            preparar_linhas_usuarios({"erro": 1})


class TestLogsSemDadosDeAutenticacao(unittest.TestCase):
    """Nenhum endpoint do Xano pode gravar o registro do usuário (com hash) no event_log."""

    def test_metadata_vazio_nos_endpoints_de_autenticacao(self):
        raiz = Path(__file__).resolve().parents[2] / "xano" / "api"
        arquivos = list(raiz.rglob("*.xs"))
        self.assertTrue(arquivos)
        for arquivo in arquivos:
            texto = arquivo.read_text(encoding="utf-8")
            with self.subTest(arquivo=arquivo.name):
                for proibido in ("metadata: $user", "metadata: $user1", "metadata  : $user"):
                    self.assertNotIn(proibido, texto)

    def test_frontend_nao_registra_senha(self):
        fonte = (Path(__file__).resolve().parents[1] / "revaulte" / "auth.py").read_text(encoding="utf-8")
        for linha in fonte.splitlines():
            if "print(" in linha:
                self.assertNotIn("senha", linha)
                self.assertNotIn("payload", linha)
                self.assertNotIn("token", linha)


if __name__ == "__main__":
    unittest.main()
