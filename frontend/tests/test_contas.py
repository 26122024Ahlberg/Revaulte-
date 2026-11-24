# Testes da lógica de contas (Change contas-acesso). Dados simulados, sem pessoas reais.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import dataclasses
import re
import subprocess
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

from revaulte.auth import (
    DESTINOS_INTERNOS,
    FUSO,
    ROTA_ADMIN,
    ROTA_CONTA,
    buscar_me,
    cpf_valido,
    destino_seguro,
    formatar_data,
    ler_data_nascimento,
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
        self.assertIn("uma letra (A–Z) e um número (0–9)", problema_senha("somenteletras"))
        self.assertIn("uma letra (A–Z) e um número (0–9)", problema_senha("12345678"))

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

    def test_destino_rotas_internas_conhecidas(self):
        for interno in ("/", "/estoque", "/usados", "/modificados", "/conta", "/admin", "/veiculo/1", "/veiculo/42"):
            with self.subTest(destino=interno):
                self.assertEqual(destino_seguro(interno), interno)

    def test_destino_rejeita_urls_externas(self):
        for externo in (
            "https://exemplo.com", "http://exemplo.com/conta", "//exemplo.com", "///exemplo.com",
            "/\\exemplo.com", "\\\\exemplo.com", "javascript:alert(1)", "data:text/html,oi",
            "exemplo.com", "/%2F%2Fexemplo.com", "/%5Cexemplo.com", "https:/exemplo.com",
        ):
            with self.subTest(destino=externo):
                self.assertEqual(destino_seguro(externo), ROTA_CONTA)

    def test_destino_rejeita_caminhos_malformados(self):
        for malformado in (
            "", " ", None, 123, ["/conta"], "conta", " /conta", "/conta ", "/conta\n", "/con\tta",
            "/conta\x00", "/../admin", "/conta/../admin", "/./conta", "/conta/", "/CONTA",
            "/conta?x=1", "/conta#topo", "/admin?proximo=https://exemplo.com", "/%63onta",
            "/veiculo/", "/veiculo/0", "/veiculo/01", "/veiculo/-1", "/veiculo/abc", "/veiculo/1/extra",
            "/veiculo/1234567890123", "/veiculo/١", "/veiculo/[veiculo_id]",
        ):
            with self.subTest(destino=malformado):
                self.assertEqual(destino_seguro(malformado), ROTA_CONTA)

    def test_destino_rejeita_rotas_desconhecidas_e_formularios(self):
        for rota in ("/entrar", "/cadastro", "/pagina-que-nao-existe", "/catalogo", "/404", "/admin/users"):
            with self.subTest(destino=rota):
                self.assertEqual(destino_seguro(rota), ROTA_CONTA)

    def test_destinos_coincidem_com_rotas_do_site(self):
        from revaulte.auth import ROTA_ANUNCIAR, ROTA_FAVORITOS, ROTA_MEUS_ANUNCIOS
        from revaulte.components import ROTA_ESTOQUE, ROTA_HOME, ROTA_MODIFICADOS, ROTA_USADOS, ROTA_VEICULO

        # Anúncios: Change anuncios-cliente, tarefa 6.1.
        self.assertEqual(
            DESTINOS_INTERNOS,
            {ROTA_HOME, ROTA_ESTOQUE, ROTA_USADOS, ROTA_MODIFICADOS, ROTA_CONTA, ROTA_ADMIN,
             ROTA_ANUNCIAR, ROTA_MEUS_ANUNCIOS, ROTA_FAVORITOS},
        )
        self.assertEqual((ROTA_ANUNCIAR, ROTA_MEUS_ANUNCIOS), ("/anunciar", "/meus-anuncios"))
        self.assertEqual(ROTA_VEICULO, "/veiculo/[veiculo_id]")

    def test_ler_proximo(self):
        self.assertEqual(ler_proximo({}, "/entrar?proximo=/conta"), "/conta")
        self.assertEqual(ler_proximo({"proximo": "/admin"}, ""), "/admin")

    def test_ler_proximo_externo_vira_minha_conta(self):
        proximo = ler_proximo({}, "/entrar?proximo=https://exemplo.com")
        self.assertEqual(destino_seguro(proximo), ROTA_CONTA)


class TestFusoBrasilia(unittest.TestCase):
    def test_fuso_fixo_menos_tres_horas(self):
        self.assertEqual(FUSO.utcoffset(None), timedelta(hours=-3))

    def test_formatar_data_no_horario_de_brasilia(self):
        # 2026-01-01 02:00 UTC ainda é 31/12/2025 em Brasília.
        self.assertEqual(formatar_data(1767232800000), "31/12/2025")
        # 2026-01-01 03:00 UTC já é 01/01/2026 em Brasília.
        self.assertEqual(formatar_data(1767236400000), "01/01/2026")
        # Em julho (inverno) o deslocamento continua −03:00, sem horário de verão.
        self.assertEqual(formatar_data(1783047600000), "03/07/2026")

    def test_formatar_data_valores_invalidos(self):
        for valor in (None, "123", True, float("inf"), 10**20):
            with self.subTest(valor=valor):
                self.assertEqual(formatar_data(valor), "")

    def test_nascimento_usa_hoje_em_brasilia(self):
        self.assertIsNotNone(ler_data_nascimento("1990-05-10"))
        self.assertIsNone(ler_data_nascimento("2999-01-01"))
        hoje = date(2026, 11, 18)
        self.assertIsNone(ler_data_nascimento("2026-11-18", hoje))
        self.assertEqual(ler_data_nascimento("2026-11-17", hoje), date(2026, 11, 17))

    def test_modulo_nao_depende_de_zoneinfo(self):
        # Simula o Windows sem base IANA nem tzdata: o import do módulo não pode falhar.
        codigo = (
            "import sys\n"
            "class Bloqueio:\n"
            "    def find_spec(self, nome, *args, **kwargs):\n"
            "        if nome in ('zoneinfo', 'tzdata'):\n"
            "            raise ModuleNotFoundError(nome)\n"
            "sys.meta_path.insert(0, Bloqueio())\n"
            "sys.modules.pop('zoneinfo', None)\n"
            "import revaulte.auth as auth\n"
            "print(auth.formatar_data(1767232800000))\n"
        )
        resultado = subprocess.run(
            [sys.executable, "-c", codigo],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr[-2000:])
        self.assertEqual(resultado.stdout.strip().splitlines()[-1], "31/12/2025")


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


XANO = Path(__file__).resolve().parents[2] / "xano"
CAMPOS_SENSIVEIS = ("password", "password_reset", "cpf", "phone", "birth_date", "address")


def ler_xs(caminho: str) -> str:
    return (XANO / caminho).read_text(encoding="utf-8")


def sem_comentarios(texto: str) -> str:
    return "\n".join(linha for linha in texto.splitlines() if not linha.strip().startswith("//"))


def bloco_precondition(texto: str, condicao: str) -> str:
    """Trecho do precondition com a condição dada (até o fechamento do bloco)."""
    inicio = texto.index(f"precondition ({condicao})")
    return texto[inicio : texto.index("}", inicio)]


class TestPermissoesXano(unittest.TestCase):
    """Regras de permissão nos arquivos XanoScript locais (sem chamar o Xano)."""

    def test_enforce_role_conta_excluida_401(self):
        texto = ler_xs("function/quick_start/enforce_role.xs")
        self.assertIn('error_type = "unauthorized"', bloco_precondition(texto, "$user != null"))

    def test_enforce_role_sem_cargo_403(self):
        texto = ler_xs("function/quick_start/enforce_role.xs")
        self.assertIn('error_type = "accessdenied"', bloco_precondition(texto, "$user.role != null"))
        # A verificação do cargo vem antes de qualquer uso do cargo.
        self.assertLess(texto.index("precondition ($user.role != null)"), texto.index("|get:$user.role"))

    def test_enforce_role_cargo_insuficiente_403_sem_revelar_cargo(self):
        texto = sem_comentarios(ler_xs("function/quick_start/enforce_role.xs"))
        bloco = bloco_precondition(texto, "$user_role_level >= $required_role_level")
        self.assertIn('error_type = "accessdenied"', bloco)
        self.assertNotIn("throw", texto)
        self.assertNotIn("Actual", texto)
        self.assertNotIn("~ $user", texto)

    def test_auth_me_conta_excluida_401_antes_do_log(self):
        texto = ler_xs("api/authentication/auth/me_GET.xs")
        self.assertIn('auth = "user"', texto)
        self.assertIn('error_type = "unauthorized"', bloco_precondition(texto, "$user != null"))
        self.assertLess(texto.index("precondition ($user != null)"), texto.index("log_event"))

    def test_login_credenciais_invalidas_401_com_mesma_mensagem(self):
        texto = sem_comentarios(ler_xs("api/authentication/auth/login_POST.xs"))
        self.assertNotIn("accessdenied", texto)
        self.assertEqual(texto.count('error_type = "unauthorized"'), 3)
        self.assertEqual(texto.count('error = "Invalid Credentials."'), 3)

    def test_login_campos_vazios_401_antes_da_consulta(self):
        # Divergência A6 (19/11/2026): sem e-mail, o db.get respondia 400 "Missing param: field_value".
        texto = sem_comentarios(ler_xs("api/authentication/auth/login_POST.xs"))
        condicao = ('$input.email != null && $input.email != "" && '
                    '$input.password != null && $input.password != ""')
        bloco = bloco_precondition(texto, condicao)
        self.assertIn('error_type = "unauthorized"', bloco)
        self.assertIn('error = "Invalid Credentials."', bloco)
        # A verificação vem antes de qualquer consulta ao banco, do token e do log.
        posicao = texto.index(f"precondition ({condicao})")
        for passo in ("db.get user", "security.check_password", "security.create_auth_token", "log_event"):
            with self.subTest(passo=passo):
                self.assertLess(posicao, texto.index(passo))

    def test_login_preserva_rota_guid_e_fluxo_valido(self):
        texto = sem_comentarios(ler_xs("api/authentication/auth/login_POST.xs"))
        self.assertIn('query "auth/login" verb=POST', texto)
        self.assertIn('guid = "qCB-D3BkW5oJHVVilsjYcLnOlkg"', texto)
        self.assertIn("response = {authToken: $authToken, user_id: $user.id}", texto)
        self.assertLess(texto.index("security.check_password"), texto.index("security.create_auth_token"))

    def test_cadastro_rejeita_data_impossivel_em_utc(self):
        # Falha V9 (19/11/2026): 1990-02-30 passava no backend porque o to_timestamp a convertia em outro dia.
        texto = sem_comentarios(ler_xs("api/authentication/auth/signup_POST.xs"))
        condicao = '($nascimento|format_timestamp:"Y-m-d":"UTC") == $input.birth_date'
        self.assertIn('error = "invalid_birth_date"', bloco_precondition(texto, condicao))
        # Conversão e formatação no mesmo fuso (UTC): sem deslocamento de dia.
        self.assertIn('$input.birth_date|to_timestamp:"UTC"', texto)
        posicao = texto.index(f"precondition ({condicao})")
        self.assertLess(texto.index("var $nascimento"), posicao)
        for passo in ("precondition ($nascimento < now", "precondition ($input.address", "db.add user"):
            with self.subTest(passo=passo):
                self.assertLess(posicao, texto.index(passo))

    def test_cadastro_preserva_validacoes_e_identidade(self):
        texto = sem_comentarios(ler_xs("api/authentication/auth/signup_POST.xs"))
        self.assertIn('query "auth/signup" verb=POST', texto)
        self.assertIn('guid = "la96rUuCVyDv3BIMVm138VE8Rm0"', texto)
        erros = ("invalid_name", "invalid_email", "invalid_password", "invalid_cpf", "invalid_phone",
                 "invalid_birth_date", "invalid_address", "email_taken", "cpf_taken")
        posicoes = [texto.index(f'error = "{erro}"') for erro in erros]
        self.assertEqual(posicoes, sorted(posicoes))
        self.assertEqual(texto.count('error = "invalid_birth_date"'), 3)
        self.assertLess(posicoes[-1], texto.index("db.add user"))
        self.assertIn('role      : "member"', texto)

    def test_cadastro_exige_senha_com_letra_e_numero_antes_da_gravacao(self):
        # Pendência B10 (20/11/2026): letra e número dependiam só do filtro da tabela no db.add.
        texto = sem_comentarios(ler_xs("api/authentication/auth/signup_POST.xs"))
        condicao = ('$input.password != null && ($input.password|strlen) >= 8 && '
                    '("/[A-Za-z]/"|regex_matches:$input.password) && ("/[0-9]/"|regex_matches:$input.password)')
        bloco = bloco_precondition(texto, condicao)
        self.assertIn('error_type = "inputerror"', bloco)
        self.assertIn('error = "invalid_password"', bloco)
        self.assertEqual(texto.count('error = "invalid_password"'), 1)
        posicao = texto.index(f"precondition ({condicao})")
        for passo in ("db.get user", "db.add user", "security.create_auth_token", "log_event"):
            with self.subTest(passo=passo):
                self.assertLess(posicao, texto.index(passo))

    def test_regra_de_senha_do_backend_e_do_frontend(self):
        # Modelo da regra do backend (mesmas expressões regulares) comparado ao frontend.
        def backend_aceita(senha: str) -> bool:
            return len(senha) >= 8 and bool(re.search(r"[A-Za-z]", senha)) and bool(re.search(r"[0-9]", senha))

        for senha, valida in (("senha123", True), ("Abcdefg1", True), ("12345678a", True), ("Teste 2026!", True),
                              ("abcdefghij", False), ("12345678", False), ("abc1234", False), ("", False),
                              ("!!!!!!!!", False),
                              # Tarefa 2.14: letras e dígitos fora do ASCII não contam, como no backend.
                              ("çççççç12", False), ("éééééééé1", False), ("abcdefgh١", False),
                              ("senhá123", True)):
            with self.subTest(senha=senha):
                self.assertEqual(backend_aceita(senha), valida)
                self.assertEqual(problema_senha(senha) == "", valida)

    def test_regra_de_ida_e_volta_da_data(self):
        # Modelo da regra do backend: o to_timestamp "transborda" dias inexistentes para o mês seguinte
        # (1990-02-30 -> 1990-03-02); a data só vale se, formatada de volta, for igual ao texto recebido.
        def ida_e_volta(texto: str) -> bool:
            ano, mes, dia = (int(parte) for parte in texto.split("-"))
            convertida = date(ano, mes, 1) + timedelta(days=dia - 1)
            return convertida.isoformat() == texto

        for texto, valida in (("1990-02-30", False), ("2026-02-29", False), ("1990-04-31", False),
                              ("2000-02-29", True), ("1990-05-10", True), ("1985-01-31", True),
                              ("1999-12-31", True), ("2001-01-01", True)):
            with self.subTest(data=texto):
                self.assertEqual(ida_e_volta(texto), valida)
                # O frontend aplica a mesma regra antes de enviar.
                hoje = date(2026, 11, 19)
                self.assertEqual(ler_data_nascimento(texto, hoje) is not None, valida)
                if valida:
                    self.assertEqual(ler_data_nascimento(texto, hoje).isoformat(), texto)

    def test_lista_administrativa_protegida_e_sem_dados_sensiveis(self):
        texto = ler_xs("api/admin/users_GET.xs")
        codigo = sem_comentarios(texto)
        self.assertIn('auth = "user"', codigo)
        self.assertIn('required_role: "admin"', codigo)
        self.assertLess(codigo.index("enforce_role"), codigo.index("db.query user"))
        inicio = codigo.index("output = [")
        saida = codigo[inicio : codigo.index("]", inicio) + 1]
        self.assertEqual(saida, 'output = ["id", "created_at", "name", "email", "role"]')
        for campo in CAMPOS_SENSIVEIS:
            with self.subTest(campo=campo):
                self.assertNotIn(f'"{campo}"', codigo)
        self.assertIn("response = $users", codigo)


# Endpoints do Quick Start desativados (decisão 10): caminho, (nome, verbo, guid publicados no Xano).
ENDPOINTS_DESATIVADOS = {
    "api/authentication/message/send_welcome_email_POST.xs": (
        'query "message/send_welcome_email" verb=POST', "rw5loJr5zd0y9ViGgL4ZpcBhKQA"),
    "api/authentication/reset/request_reset_link_GET.xs": (
        'query "reset/request-reset-link" verb=GET', "TODx3DGJ3o0L9UAANFUmU6QDDyU"),
    "api/authentication/reset/magic_link_login_POST.xs": (
        'query "reset/magic-link-login" verb=POST', "-6gXbVbSs_1-jKvlhohLG4VmDw0"),
}


class TestEndpointsQuickStartDesativados(unittest.TestCase):
    """Os bloqueios respondem 404 sem banco, e-mail, token, sessão ou log (sem chamar o Xano)."""

    def test_identidade_preservada(self):
        for caminho, (cabecalho, guid) in ENDPOINTS_DESATIVADOS.items():
            codigo = sem_comentarios(ler_xs(caminho))
            with self.subTest(arquivo=caminho):
                self.assertIn(cabecalho, codigo)
                self.assertIn('api_group = "Authentication"', codigo)
                self.assertIn('tags = ["xano:quick-start"]', codigo)
                self.assertIn(f'guid = "{guid}"', codigo)

    def test_bloqueio_404_sem_entrada(self):
        for caminho in ENDPOINTS_DESATIVADOS:
            codigo = sem_comentarios(ler_xs(caminho))
            with self.subTest(arquivo=caminho):
                entrada = codigo[codigo.index("input {") : codigo.index("}", codigo.index("input {"))]
                self.assertEqual(entrada.replace("input {", "").strip(), "")
                pilha = codigo[codigo.index("stack {") :]
                self.assertTrue(pilha.replace("stack {", "", 1).lstrip().startswith("precondition (false)"))
                self.assertIn('error_type = "notfound"', bloco_precondition(codigo, "false"))
                self.assertIn("response = null", codigo)

    def test_sem_banco_email_token_sessao_ou_log(self):
        proibidos = ("db.", "util.send_email", "function.run", "security.", "log_event",
                     "generate_magic_link", "$auth", "$input", "auth =")
        for caminho in ENDPOINTS_DESATIVADOS:
            codigo = sem_comentarios(ler_xs(caminho))
            for termo in proibidos:
                with self.subTest(arquivo=caminho, termo=termo):
                    self.assertNotIn(termo, codigo)

    def test_login_e_cadastro_continuam_ativos(self):
        for caminho in ("api/authentication/auth/login_POST.xs", "api/authentication/auth/signup_POST.xs"):
            codigo = sem_comentarios(ler_xs(caminho))
            with self.subTest(arquivo=caminho):
                self.assertNotIn("precondition (false)", codigo)
                self.assertIn("security.create_auth_token", codigo)


class TestRespostasDeSessao(unittest.IsolatedAsyncioTestCase):
    """Como o frontend trata 401/403 do backend."""

    async def test_conta_excluida_invalida_a_sessao(self):
        with patch("revaulte.auth.chamar_xano", AsyncMock(return_value=(401, {"message": "unauthorized"}))):
            self.assertEqual(await buscar_me("token-de-teste"), ("invalido", None))

    async def test_acesso_negado_invalida_a_sessao(self):
        with patch("revaulte.auth.chamar_xano", AsyncMock(return_value=(403, None))):
            self.assertEqual(await buscar_me("token-de-teste"), ("invalido", None))

    async def test_resposta_vazia_nao_autentica(self):
        with patch("revaulte.auth.chamar_xano", AsyncMock(return_value=(200, None))):
            self.assertEqual(await buscar_me("token-de-teste"), ("erro", None))

    async def test_conta_sem_cargo_nao_vira_administrador(self):
        corpo = {"id": 5, "name": "Teste", "email": "t@e.com", "role": None}
        with patch("revaulte.auth.chamar_xano", AsyncMock(return_value=(200, corpo))):
            situacao, usuario = await buscar_me("token-de-teste")
        self.assertEqual(situacao, "ok")
        self.assertNotEqual(usuario.perfil, "admin")

    def test_lista_ignora_campos_sensiveis_mesmo_se_o_backend_enviar(self):
        item = {"id": 2, "name": "T", "email": "t@e.com", "role": "member", "phone": "11900000000",
                "address": "Rua de Teste, 1", "birth_date": "1990-05-10", "password_reset": {"token": "x"}}
        linhas = preparar_linhas_usuarios([item])
        self.assertEqual(
            set(dataclasses.asdict(linhas[0])), {"id", "nome", "email", "perfil", "desde"}
        )
        for valor in ("11900000000", "Rua de Teste", "1990-05-10"):
            self.assertNotIn(valor, repr(linhas))


# ---------------------------------------------------------------------------
# Página /entrar (tarefa 3.2, parte do login). Sem rede: chamar_xano simulado.
# ---------------------------------------------------------------------------


def codigo(componente) -> str:
    """Código gerado do componente, com os acentos (escapados como \\uXXXX) restaurados."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), str(componente))


def eventos_de_envio(nome_pagina: str) -> list[str]:
    """Eventos do AuthState chamados pelo onSubmit (ficam no hook handleSubmit, fora do JSX)."""
    from revaulte import components

    ganchos = components.__dict__[nome_pagina]()._get_all_hooks()
    return sorted(set(re.findall(r"auth_state\.\w+", " ".join(map(str, ganchos)))))


class TestPaginaEntrar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from revaulte.components import pagina_entrar

        cls.gerado = codigo(pagina_entrar())

    def test_textos_em_portugues(self):
        for texto in ("Entrar", "Entrando…", "E-mail", "Senha", "Acesse sua conta com e-mail e senha.",
                      "Ainda não tem conta?", "Cadastre-se", "Minha conta"):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.gerado)

    def test_campos_de_email_e_senha(self):
        for trecho in ('name:"email"', 'type:"email"', 'autoComplete:"email"', 'htmlFor:"email"',
                       'name:"senha"', 'type:"password"', 'autoComplete:"current-password"', 'htmlFor:"senha"'):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.gerado)

    def test_senha_nao_e_campo_controlado(self):
        # Sem value/onChange: a senha só existe no evento de envio, nunca no estado do Reflex.
        self.assertNotIn("value:", self.gerado)
        self.assertNotIn("onChange", self.gerado)

    def test_envio_pelo_auth_state_com_mensagens_proprias(self):
        self.assertIn("noValidate:true", self.gerado)
        self.assertIn("onSubmit", self.gerado)
        self.assertEqual(eventos_de_envio("pagina_entrar"), ["auth_state.entrar"])
        self.assertIn('"aria-live":"polite"', self.gerado)
        self.assertIn("erro_formulario", self.gerado)
        self.assertIn('className:"form-error"', self.gerado)

    def test_estado_de_carregamento(self):
        self.assertIn('type:"submit"', self.gerado)
        self.assertRegex(self.gerado, r"disabled:[^,}]*enviando")
        self.assertIn('"aria-busy"', self.gerado)
        self.assertIn('className:"spinner"', self.gerado)

    def test_link_para_cadastro(self):
        self.assertIn('to:"/cadastro"', self.gerado)

    def test_identidade_visual_reaproveitada(self):
        for classe in ("inner-page", "section-title", "btn btn-red", "filter-field", "topbar", "footer"):
            with self.subTest(classe=classe):
                self.assertIn(classe, self.gerado)

    def test_rota_registrada_com_on_load(self):
        from revaulte.revaulte import app

        self.assertIn("entrar", app._unevaluated_pages)
        on_load = repr(app._unevaluated_pages["entrar"].on_load)
        self.assertIn("abrir_formulario", on_load)
        self.assertIn("fechar_menu", on_load)

    def test_estilos_da_pagina(self):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for seletor in (".auth-card", ".auth-form", ".form-error", ".auth-submit:disabled", ".auth-link"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor + " {", css)


class EstadoFalso:
    """Substitui o AuthState para executar AuthState.entrar sem servidor do Reflex."""

    def __init__(self):
        self.erro_formulario = "mensagem anterior"
        self.enviando = False
        self.concluir = AsyncMock(return_value="redirecionar")

    async def _concluir_entrada(self, token):
        return await self.concluir(token)


class TestEventoEntrar(unittest.IsolatedAsyncioTestCase):
    async def executar(self, dados, resposta=None):
        from revaulte.auth import AuthState

        estado = EstadoFalso()
        chamada = AsyncMock(return_value=resposta)
        enviando_durante = []
        with patch("revaulte.auth.chamar_xano", chamada):
            gerador = AuthState.entrar.fn(estado, dados)
            if hasattr(gerador, "__anext__"):
                async for _ in gerador:
                    enviando_durante.append(estado.enviando)
            else:
                await gerador
        return estado, chamada, enviando_durante

    async def test_campos_vazios_nao_chamam_o_backend(self):
        for dados in ({"email": "", "senha": ""}, {"email": "teste@exemplo.com", "senha": ""},
                      {"email": "invalido", "senha": "senha123"}, {}):
            with self.subTest(dados=dados):
                estado, chamada, _ = await self.executar(dados)
                chamada.assert_not_called()
                self.assertEqual(estado.erro_formulario, "Informe e-mail e senha.")
                self.assertFalse(estado.enviando)

    async def test_credenciais_invalidas_mensagem_unica(self):
        for status in (400, 401, 403, 404):
            with self.subTest(status=status):
                estado, chamada, enviando = await self.executar(
                    {"email": "teste@exemplo.com", "senha": "errada123"}, (status, {"message": "Invalid Credentials."})
                )
                chamada.assert_awaited_once()
                self.assertEqual(estado.erro_formulario, "E-mail ou senha incorretos.")
                self.assertTrue(enviando[0], "o botão deve ficar desabilitado durante o envio")
                self.assertFalse(estado.enviando)
                estado.concluir.assert_not_called()

    async def test_falha_de_rede_ou_servidor_mensagem_generica(self):
        from revaulte.auth import ERRO_GENERICO

        for status in (0, 429, 500):
            with self.subTest(status=status):
                estado, _, _ = await self.executar({"email": "teste@exemplo.com", "senha": "senha123"}, (status, None))
                self.assertEqual(estado.erro_formulario, ERRO_GENERICO)
                self.assertFalse(estado.enviando)

    async def test_login_valido_envia_email_normalizado_e_conclui(self):
        estado, chamada, _ = await self.executar(
            {"email": "  Teste@Exemplo.com ", "senha": "senha123"}, (200, {"authToken": "token-de-teste", "user_id": 1})
        )
        metodo, url = chamada.await_args.args
        self.assertEqual(metodo, "POST")
        self.assertTrue(url.endswith("/auth/login"))
        self.assertEqual(chamada.await_args.kwargs["dados"], {"email": "teste@exemplo.com", "password": "senha123"})
        estado.concluir.assert_awaited_once_with("token-de-teste")
        self.assertEqual(estado.erro_formulario, "")

    async def test_senha_nao_fica_no_estado(self):
        estado, _, _ = await self.executar({"email": "teste@exemplo.com", "senha": "segredo123"}, (401, None))
        self.assertNotIn("segredo123", repr(vars(estado)))


# ---------------------------------------------------------------------------
# Página /cadastro (tarefa 3.2, parte do cadastro). Sem rede: chamar_xano simulado.
# ---------------------------------------------------------------------------

CAMPOS_CADASTRO = ("nome", "email", "cpf", "telefone", "nascimento", "endereco", "senha", "confirmacao")


class TestPaginaCadastro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from revaulte.components import pagina_cadastro

        cls.gerado = codigo(pagina_cadastro())

    def test_textos_em_portugues(self):
        for texto in ("Criar conta", "Criando conta…", "Nome completo", "E-mail", "CPF", "Telefone",
                      "Data de nascimento", "Endereço", "Senha", "Confirmar senha",
                      "Todos os campos são obrigatórios.", "Já tem conta?",
                      "No mínimo 8 caracteres, com pelo menos uma letra (A–Z) e um número (0–9)."):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.gerado)

    def test_campos_com_os_nomes_que_validar_cadastro_espera(self):
        for campo in CAMPOS_CADASTRO:
            with self.subTest(campo=campo):
                self.assertIn(f'name:"{campo}"', self.gerado)
                self.assertIn(f'htmlFor:"{campo}"', self.gerado)

    def test_tipos_e_preenchimento_automatico(self):
        for trecho in ('type:"email"', 'type:"tel"', 'type:"date"', 'min:"1900-01-01"', 'inputMode:"numeric"',
                       'autoComplete:"new-password"', 'autoComplete:"bday"', 'autoComplete:"street-address"',
                       'autoComplete:"name"'):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.gerado)
        self.assertEqual(self.gerado.count('type:"password"'), 2)
        self.assertNotIn("current-password", self.gerado)

    def test_dicas_ligadas_aos_campos(self):
        for campo in ("cpf", "telefone", "senha"):
            with self.subTest(campo=campo):
                self.assertIn(f'"aria-describedby":"{campo}-dica"', self.gerado)
                self.assertIn(f'id:"{campo}-dica"', self.gerado)

    def test_campos_nao_controlados(self):
        self.assertNotIn("value:", self.gerado)
        self.assertNotIn("onChange", self.gerado)

    def test_envio_mensagens_e_carregamento(self):
        self.assertIn("noValidate:true", self.gerado)
        self.assertIn("onSubmit", self.gerado)
        self.assertEqual(eventos_de_envio("pagina_cadastro"), ["auth_state.cadastrar"])
        self.assertIn('"aria-live":"polite"', self.gerado)
        self.assertIn('className:"form-error"', self.gerado)
        self.assertRegex(self.gerado, r"disabled:[^,}]*enviando")
        self.assertIn('"aria-busy"', self.gerado)
        self.assertIn('className:"spinner"', self.gerado)

    def test_link_para_entrar_e_visual(self):
        self.assertIn('to:"/entrar"', self.gerado)
        for classe in ("inner-page", "section-title", "btn btn-red", "auth-card is-wide", "auth-form is-grid"):
            with self.subTest(classe=classe):
                self.assertIn(classe, self.gerado)

    def test_rota_registrada_com_on_load(self):
        from revaulte.revaulte import app

        self.assertIn("cadastro", app._unevaluated_pages)
        on_load = repr(app._unevaluated_pages["cadastro"].on_load)
        self.assertIn("abrir_formulario", on_load)
        self.assertIn("fechar_menu", on_load)

    def test_estilos_responsivos(self):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for seletor in (".auth-card.is-wide", ".auth-form.is-grid", ".auth-form.is-grid > .is-wide", ".field-hint"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor + " {", css)
        # Uma coluna em telas estreitas (375 px).
        self.assertRegex(
            css,
            r"@media \(max-width: 560px\) \{\s*\.auth-form\.is-grid \{\s*grid-template-columns: minmax\(0, 1fr\);",
        )


class TestEventoCadastrar(unittest.IsolatedAsyncioTestCase):
    async def executar(self, dados, resposta=None):
        from revaulte.auth import AuthState

        estado = EstadoFalso()
        chamada = AsyncMock(return_value=resposta)
        enviando_durante = []
        with patch("revaulte.auth.chamar_xano", chamada):
            gerador = AuthState.cadastrar.fn(estado, dados)
            if hasattr(gerador, "__anext__"):
                async for _ in gerador:
                    enviando_durante.append(estado.enviando)
            else:
                await gerador
        return estado, chamada, enviando_durante

    async def test_dados_invalidos_nao_chamam_o_backend(self):
        casos = {
            "nome": ({"nome": ""}, "Informe seu nome completo."),
            "cpf": ({"cpf": "111.111.111-11"}, "Informe um CPF válido."),
            "senha curta": ({"senha": "abc123", "confirmacao": "abc123"}, "A senha deve ter pelo menos 8 caracteres."),
            "senha sem ASCII": ({"senha": "çççççç12", "confirmacao": "çççççç12"},
                                "A senha deve ter pelo menos uma letra (A–Z) e um número (0–9)."),
            "confirmação": ({"confirmacao": "outra123"}, "As senhas não coincidem."),
            "data": ({"nascimento": "1990-02-30"}, "Informe uma data de nascimento válida."),
        }
        for nome, (extra, mensagem) in casos.items():
            with self.subTest(caso=nome):
                estado, chamada, _ = await self.executar(formulario(**extra))
                chamada.assert_not_called()
                self.assertEqual(estado.erro_formulario, mensagem)
                self.assertFalse(estado.enviando)

    async def test_erros_do_backend_em_portugues(self):
        from revaulte.auth import ERRO_GENERICO

        casos = (
            (403, {"message": "email_taken"}, "Este e-mail já está cadastrado. Entre com ele ou use outro."),
            (403, {"message": "cpf_taken"}, "Este CPF já está cadastrado."),
            (400, {"message": "invalid_password"},
             "A senha deve ter pelo menos 8 caracteres, com uma letra (A–Z) e um número (0–9)."),
            (429, {"code": "ERROR_CODE_TOO_MANY_REQUESTS"}, ERRO_GENERICO),
            (0, None, ERRO_GENERICO),
        )
        for status, corpo, mensagem in casos:
            with self.subTest(status=status, corpo=corpo):
                estado, chamada, enviando = await self.executar(formulario(), (status, corpo))
                chamada.assert_awaited_once()
                self.assertEqual(estado.erro_formulario, mensagem)
                self.assertTrue(enviando[0], "o botão deve ficar desabilitado durante o envio")
                self.assertFalse(estado.enviando)
                estado.concluir.assert_not_called()

    async def test_cadastro_valido_envia_formato_do_xano(self):
        estado, chamada, _ = await self.executar(formulario(), (200, {"authToken": "token-de-teste", "user_id": 1}))
        metodo, url = chamada.await_args.args
        self.assertEqual(metodo, "POST")
        self.assertTrue(url.endswith("/auth/signup"))
        self.assertEqual(chamada.await_args.kwargs["dados"], {
            "name": "Pessoa de Teste", "email": "teste@exemplo.com", "cpf": CPF_TESTE, "phone": "11900000000",
            "birth_date": "1990-05-10", "address": "Rua de Teste, 100", "password": "senha123",
        })
        estado.concluir.assert_awaited_once_with("token-de-teste")

    async def test_senha_e_dados_pessoais_nao_ficam_no_estado(self):
        estado, _, _ = await self.executar(
            formulario(senha="segredo123", confirmacao="segredo123"), (403, {"message": "cpf_taken"})
        )
        texto = repr(vars(estado))
        for valor in ("segredo123", CPF_TESTE, "11900000000", "1990-05-10"):
            with self.subTest(valor=valor):
                self.assertNotIn(valor, texto)

# ---------------------------------------------------------------------------
# Página /conta (tarefa 3.3, parte de Minha conta). Sem rede: buscar_me/chamar_xano simulados.
# ---------------------------------------------------------------------------

USUARIO_XANO = {"id": 7, "created_at": 1763500000000, "name": "Pessoa de Teste", "email": "teste@exemplo.com",
                "role": "member"}


class TestPaginaConta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from revaulte.components import pagina_conta

        cls.gerado = codigo(pagina_conta())

    def test_textos_em_portugues(self):
        from revaulte.components import MENSAGEM_ERRO_CONTA

        for texto in ("Minha conta", "Nome", "E-mail", "Perfil", "Sair", "Carregando sua conta…",
                      "Tentar novamente", MENSAGEM_ERRO_CONTA):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.gerado)

    def test_exibe_nome_email_e_perfil_do_backend(self):
        for campo in ("usuario_rx_state_?.[\"nome\"]", "usuario_rx_state_?.[\"email\"]",
                      "usuario_rx_state_?.[\"rotulo_perfil\"]"):
            with self.subTest(campo=campo):
                self.assertIn(campo, self.gerado)

    def test_dados_so_com_sessao_confirmada(self):
        self.assertIn('situacao_protegida_rx_state_?.valueOf?.() === "ok"', self.gerado)
        self.assertIn('situacao_protegida_rx_state_?.valueOf?.() === "erro"', self.gerado)
        self.assertIn('"aria-live":"polite"', self.gerado)

    def test_nao_exibe_dados_sensiveis(self):
        for termo in ("cpf", "phone", "telefone", "birth", "nascimento", "address", "endereco", "password",
                      "senha", "hash", "token"):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, self.gerado.lower())

    def test_botao_sair(self):
        self.assertIn("auth_state.sair", self.gerado)
        self.assertIn('type:"button"', self.gerado)

    def test_rota_registrada_com_protecao(self):
        from revaulte.revaulte import app

        self.assertIn("conta", app._unevaluated_pages)
        on_load = repr(app._unevaluated_pages["conta"].on_load)
        self.assertIn("exigir_login", on_load)
        self.assertIn("fechar_menu", on_load)

    def test_estilos(self):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for seletor in (".account-list", ".account-item", ".account-item dt", ".account-item dd"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor + " {", css)
        self.assertIn("overflow-wrap: anywhere;", css)


class EstadoSessaoFalso:
    """Substitui o AuthState para executar exigir_login e sair sem servidor do Reflex."""

    def __init__(self, token=""):
        from revaulte.auth import Usuario

        self.token = token
        self.usuario = Usuario(id=99, nome="Sessão anterior", email="anterior@exemplo.com", perfil="admin")
        self.verificado = True
        self.situacao_protegida = "ok"

    def _encerrar(self):
        from revaulte.auth import AuthState

        AuthState._encerrar(self)

    async def _exigir(self, rota, perfil):
        from revaulte.auth import AuthState

        return await AuthState._exigir(self, rota, perfil)


def descrever(eventos) -> str:
    return repr(eventos if isinstance(eventos, list) else [eventos])


class TestProtecaoDaConta(unittest.IsolatedAsyncioTestCase):
    async def exigir(self, token, resposta=None):
        from revaulte.auth import AuthState

        estado = EstadoSessaoFalso(token)
        chamada = AsyncMock(return_value=resposta)
        with patch("revaulte.auth.chamar_xano", chamada):
            eventos = await AuthState.exigir_login.fn(estado)
        return estado, chamada, eventos

    async def test_visitante_sem_token_vai_para_entrar(self):
        estado, chamada, eventos = await self.exigir("")
        chamada.assert_not_called()
        self.assertIn("/entrar?proximo=/conta", descrever(eventos))
        self.assertEqual(estado.usuario.id, 0)
        self.assertNotEqual(estado.situacao_protegida, "ok")

    async def test_token_recusado_limpa_sessao_e_vai_para_entrar(self):
        for status in (401, 403):
            with self.subTest(status=status):
                estado, chamada, eventos = await self.exigir("token-de-teste", (status, None))
                chamada.assert_awaited_once()
                texto = descrever(eventos)
                self.assertIn("/entrar?proximo=/conta", texto)
                self.assertIn("revaulte_sessao", texto)
                self.assertEqual((estado.token, estado.usuario.id, estado.verificado), ("", 0, False))

    async def test_falha_do_backend_mostra_erro_sem_dados(self):
        for resposta in ((0, None), (429, None), (500, None), (200, None)):
            with self.subTest(resposta=resposta):
                estado, _, eventos = await self.exigir("token-de-teste", resposta)
                self.assertIsNone(eventos)
                self.assertEqual(estado.situacao_protegida, "erro")

    async def test_sessao_valida_exibe_dados_do_backend(self):
        estado, chamada, eventos = await self.exigir("token-de-teste", (200, USUARIO_XANO))
        metodo, url, token = chamada.await_args.args
        self.assertEqual((metodo, token), ("GET", "token-de-teste"))
        self.assertTrue(url.endswith("/auth/me"))
        self.assertIsNone(eventos)
        self.assertEqual(estado.situacao_protegida, "ok")
        self.assertEqual((estado.usuario.nome, estado.usuario.email, estado.usuario.rotulo_perfil),
                         ("Pessoa de Teste", "teste@exemplo.com", "Cliente"))

    async def test_conta_nao_guarda_dados_sensiveis_mesmo_se_o_backend_enviar(self):
        corpo = dict(USUARIO_XANO, cpf=CPF_TESTE, phone="11900000000", birth_date="1990-05-10",
                     address="Rua de Teste, 100", password="hash-de-teste")
        estado, _, _ = await self.exigir("token-de-teste", (200, corpo))
        texto = repr(estado.usuario)
        for valor in (CPF_TESTE, "11900000000", "1990-05-10", "Rua de Teste", "hash-de-teste"):
            with self.subTest(valor=valor):
                self.assertNotIn(valor, texto)

    def test_sair_limpa_a_sessao(self):
        from revaulte.auth import AuthState

        estado = EstadoSessaoFalso("token-de-teste")
        eventos = AuthState.sair.fn(estado)
        self.assertEqual((estado.token, estado.usuario.id, estado.usuario.nome, estado.verificado), ("", 0, "", False))
        texto = descrever(eventos)
        self.assertIn("revaulte_sessao", texto)
        self.assertIn("_remove_cookie", texto)
        # Redireciona para a página inicial (o "/" do caminho do cookie não conta).
        self.assertRegex(texto, r"_redirect.*?_js_expr='path'.*?_var_value='/'")

# ---------------------------------------------------------------------------
# Destino após o login (?proximo=): URL exata do redirecionamento e leitura pelo roteador
# real do Reflex (RouterData montado com os dados que o navegador envia).
# ---------------------------------------------------------------------------


def destinos_redirect(eventos) -> list[str]:
    """Caminhos exatos dos rx.redirect em um retorno de evento (um EventSpec ou uma lista)."""
    caminhos = []
    for evento in eventos if isinstance(eventos, list) else [eventos]:
        # O Reflex nomeia a função interna "fn"; o nome do evento fica em __qualname__.
        if getattr(getattr(getattr(evento, "handler", None), "fn", None), "__qualname__", "") != "_redirect":
            continue
        for nome, valor in evento.args:
            if getattr(nome, "_js_expr", None) == "path":
                caminhos.append(valor._var_value)
    return caminhos


def roteador(caminho_com_busca: str):
    """RouterData como o Reflex 0.10 monta a partir do router_data enviado pelo navegador."""
    from urllib.parse import parse_qsl, urlsplit

    from reflex.istate.data import RouterData

    partes = urlsplit(caminho_com_busca)
    dados = {"pathname": partes.path, "asPath": caminho_com_busca, "headers": {"origin": "http://localhost:3000"}}
    consulta = dict(parse_qsl(partes.query))
    if consulta:
        dados["query"] = consulta
    return RouterData.from_router_data(dados)


class EstadoFormularioFalso:
    def __init__(self, caminho_com_busca: str, token: str = "", autenticado: bool = False):
        self.router = roteador(caminho_com_busca)
        self.token = token
        self.autenticado = autenticado
        self.erro_formulario = "mensagem anterior"
        self.enviando = True
        self.proximo = ""


class TestDestinoAposLogin(unittest.IsolatedAsyncioTestCase):
    async def test_visitante_em_conta_vai_para_a_url_exata(self):
        from revaulte.auth import AuthState

        estado = EstadoSessaoFalso("")
        eventos = await AuthState.exigir_login.fn(estado)
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/conta"])

    async def test_token_recusado_remove_cookie_e_vai_para_a_url_exata(self):
        from revaulte.auth import AuthState

        estado = EstadoSessaoFalso("token-de-teste")
        with patch("revaulte.auth.chamar_xano", AsyncMock(return_value=(401, None))):
            eventos = await AuthState.exigir_login.fn(estado)
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/conta"])
        self.assertIn("_remove_cookie", repr(eventos))

    async def test_visitante_em_admin_vai_para_a_url_exata(self):
        # Só a proteção já existente no AuthState; a página /admin não faz parte desta etapa.
        from revaulte.auth import AuthState

        estado = EstadoSessaoFalso("")
        eventos = await AuthState.exigir_admin.fn(estado)
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/admin"])

    def test_entrar_le_o_proximo_da_url_real(self):
        from revaulte.auth import AuthState

        for url, esperado in (("/entrar?proximo=/conta", "/conta"), ("/entrar?proximo=/admin", "/admin"),
                              ("/entrar?proximo=/veiculo/12", "/veiculo/12"), ("/entrar?proximo=%2Fconta", "/conta"),
                              ("/cadastro?proximo=/estoque", "/estoque"), ("/entrar", "/conta")):
            with self.subTest(url=url):
                estado = EstadoFormularioFalso(url)
                self.assertIsNone(AuthState.abrir_formulario.fn(estado))
                self.assertEqual(estado.proximo, esperado)
                self.assertEqual((estado.erro_formulario, estado.enviando), ("", False))

    def test_entrar_recusa_destinos_externos_ou_desconhecidos(self):
        from revaulte.auth import AuthState

        for valor in ("https://exemplo.com", "//exemplo.com", "/\\exemplo.com", "/conta/../admin", "/entrar",
                      "/cadastro", "/conta?x=1", "/conta#a", "javascript:alert(1)", "/veiculo/0", "/desconhecida"):
            with self.subTest(valor=valor):
                from urllib.parse import quote

                estado = EstadoFormularioFalso("/entrar?proximo=" + quote(valor, safe=""))
                AuthState.abrir_formulario.fn(estado)
                self.assertEqual(estado.proximo, "/conta")

    def test_usuario_ja_autenticado_vai_direto_ao_destino(self):
        from revaulte.auth import AuthState

        estado = EstadoFormularioFalso("/entrar?proximo=/conta", token="token-de-teste", autenticado=True)
        self.assertEqual(destinos_redirect(AuthState.abrir_formulario.fn(estado)), ["/conta"])
        estado = EstadoFormularioFalso("/entrar?proximo=https://exemplo.com", token="token-de-teste", autenticado=True)
        self.assertEqual(destinos_redirect(AuthState.abrir_formulario.fn(estado)), ["/conta"])

# ---------------------------------------------------------------------------
# Página /admin (tarefa 3.3, painel D1). Sem rede: chamar_xano simulado.
# ---------------------------------------------------------------------------

ADMIN_XANO = {"id": 2, "created_at": 1763500000000, "name": "Admin de Teste", "email": "admin@exemplo.com",
              "role": "admin"}
LISTA_XANO = [
    dict(ADMIN_XANO),
    {"id": 1, "created_at": 1763400000000, "name": "Cliente de Teste", "email": "cliente@exemplo.com",
     "role": "member", "cpf": CPF_TESTE, "phone": "11900000000", "birth_date": "1990-05-10",
     "address": "Rua de Teste, 100", "password": "hash-de-teste"},
]


def nomes_de_eventos(eventos) -> list[str]:
    """Nomes dos eventos devolvidos (handlers de estado e eventos internos do Reflex)."""
    nomes = []
    for evento in eventos if isinstance(eventos, list) else [eventos]:
        if evento is None:
            continue
        handler = getattr(evento, "handler", evento)
        nomes.append(getattr(getattr(handler, "fn", None), "__qualname__", repr(handler)))
    return nomes


class TestPaginaAdmin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from revaulte.components import pagina_admin

        cls.gerado = codigo(pagina_admin())

    def test_textos_em_portugues(self):
        from revaulte.components import MENSAGEM_ERRO_ACESSO, MENSAGEM_ERRO_USUARIOS, MENSAGEM_SEM_USUARIOS

        for texto in ("Área administrativa", "Usuários", "Verificando acesso…", "Carregando usuários…",
                      "Acesso restrito", "Esta área é exclusiva para administradores da Revaulte.",
                      "Ir para Minha conta", "Tentar novamente", MENSAGEM_ERRO_ACESSO, MENSAGEM_ERRO_USUARIOS,
                      MENSAGEM_SEM_USUARIOS):
            with self.subTest(texto=texto):
                self.assertIn(texto, self.gerado)

    def test_somente_as_cinco_colunas(self):
        cabecalhos = re.findall(r'jsx\("th",\{scope:"col"\},"([^"]+)"\)', self.gerado)
        self.assertEqual(cabecalhos, ["ID", "Data de cadastro", "Nome", "E-mail", "Perfil"])
        rotulos = re.findall(r'"data-label":"([^"]+)"', self.gerado)
        self.assertEqual(rotulos, ["ID", "Data de cadastro", "Nome", "E-mail", "Perfil"])
        for campo in ('["id"]', '["desde"]', '["nome"]', '["email"]', '["perfil"]'):
            with self.subTest(campo=campo):
                self.assertIn(campo, self.gerado)

    def test_nao_exibe_dados_sensiveis(self):
        for termo in ("cpf", "phone", "telefone", "birth", "nascimento", "address", "endereco", "password",
                      "senha", "hash", "token"):
            with self.subTest(termo=termo):
                self.assertNotIn(termo, self.gerado.lower())

    def test_lista_so_depois_do_perfil_confirmado(self):
        self.assertIn('situacao_protegida_rx_state_?.valueOf?.() === "ok"', self.gerado)
        posicao_ok = self.gerado.index('situacao_protegida_rx_state_?.valueOf?.() === "ok"')
        self.assertLess(posicao_ok, self.gerado.index('className:"admin-table"'))
        self.assertIn('situacao_rx_state_?.valueOf?.() === "lista"', self.gerado)
        self.assertIn('"aria-live":"polite"', self.gerado)

    def test_tentar_novamente(self):
        self.assertIn("admin_state.carregar_usuarios", self.gerado)
        self.assertIn("auth_state.exigir_admin", self.gerado)

    def test_sem_acoes_sobre_usuarios(self):
        # D1: nenhum botão por linha (editar, bloquear, trocar perfil).
        tabela = self.gerado[self.gerado.index('className:"admin-table"'):]
        tabela = tabela[: tabela.index('jsx("tbody"') + 800]
        self.assertNotIn('jsx("button"', tabela)
        self.assertNotIn("onClick", tabela)

    def test_rota_registrada_com_protecao(self):
        from revaulte.revaulte import app

        self.assertIn("admin", app._unevaluated_pages)
        on_load = repr(app._unevaluated_pages["admin"].on_load)
        self.assertIn("exigir_admin", on_load)
        self.assertIn("fechar_menu", on_load)

    def test_estilos_responsivos(self):
        css = (Path(__file__).resolve().parents[1] / "assets" / "styles.css").read_text(encoding="utf-8")
        for seletor in (".admin-panel", ".admin-table", ".admin-table th,", ".admin-table td::before"):
            with self.subTest(seletor=seletor):
                self.assertIn(seletor, css)
        self.assertIn("content: attr(data-label);", css)
        self.assertRegex(css, r"@media \(max-width: 760px\) \{\s*\.admin-table,")


class EstadoAdminFalso:
    def __init__(self, auth):
        self.auth = auth
        self.situacao = "lista"
        self.usuarios = ["lista anterior"]

    async def get_state(self, classe):
        return self.auth


class TestProtecaoDoAdmin(unittest.IsolatedAsyncioTestCase):
    async def exigir(self, token, resposta=None):
        from revaulte.auth import AuthState

        estado = EstadoSessaoFalso(token)
        chamada = AsyncMock(return_value=resposta)
        with patch("revaulte.auth.chamar_xano", chamada):
            eventos = await AuthState.exigir_admin.fn(estado)
        return estado, chamada, eventos

    async def test_visitante_vai_para_entrar_e_lista_e_limpa(self):
        estado, chamada, eventos = await self.exigir("")
        chamada.assert_not_called()
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/admin"])
        self.assertEqual(nomes_de_eventos(eventos)[0], "AdminState.limpar")

    async def test_token_recusado_limpa_sessao_e_lista(self):
        estado, _, eventos = await self.exigir("token-de-teste", (401, None))
        nomes = nomes_de_eventos(eventos)
        self.assertEqual(nomes[0], "AdminState.limpar")
        self.assertIn("_remove_cookie", nomes)
        self.assertEqual(destinos_redirect(eventos), ["/entrar?proximo=/admin"])
        self.assertEqual(estado.token, "")

    async def test_cliente_ve_acesso_restrito_sem_chamar_admin_users(self):
        corpo = dict(ADMIN_XANO, role="member")
        estado, chamada, eventos = await self.exigir("token-de-teste", (200, corpo))
        self.assertEqual(chamada.await_count, 1)
        self.assertTrue(chamada.await_args.args[1].endswith("/auth/me"))
        self.assertEqual(estado.situacao_protegida, "restrito")
        self.assertEqual(nomes_de_eventos(eventos), ["AdminState.limpar"])

    async def test_conta_sem_cargo_ve_acesso_restrito(self):
        estado, _, eventos = await self.exigir("token-de-teste", (200, dict(ADMIN_XANO, role=None)))
        self.assertEqual(estado.situacao_protegida, "restrito")
        self.assertEqual(nomes_de_eventos(eventos), ["AdminState.limpar"])

    async def test_falha_ao_conferir_a_sessao(self):
        for resposta in ((0, None), (429, None), (500, None)):
            with self.subTest(resposta=resposta):
                estado, _, eventos = await self.exigir("token-de-teste", resposta)
                self.assertEqual(estado.situacao_protegida, "erro")
                self.assertEqual(nomes_de_eventos(eventos), ["AdminState.limpar"])

    async def test_administrador_carrega_a_lista(self):
        estado, _, eventos = await self.exigir("token-de-teste", (200, ADMIN_XANO))
        self.assertEqual(estado.situacao_protegida, "ok")
        self.assertEqual(estado.usuario.rotulo_perfil, "Administrador")
        self.assertEqual(nomes_de_eventos(eventos), ["AdminState.carregar_usuarios"])

    def test_sair_tambem_apaga_a_lista(self):
        from revaulte.auth import AuthState

        nomes = nomes_de_eventos(AuthState.sair.fn(EstadoSessaoFalso("token-de-teste")))
        self.assertEqual(nomes[0], "AdminState.limpar")
        self.assertIn("_remove_cookie", nomes)

    def test_limpar(self):
        from revaulte.auth import AdminState

        estado = EstadoAdminFalso(None)
        AdminState.limpar.fn(estado)
        self.assertEqual((estado.situacao, estado.usuarios), ("carregando", []))


class TestListaDeUsuarios(unittest.IsolatedAsyncioTestCase):
    async def carregar(self, resposta):
        from revaulte.auth import AdminState

        auth = EstadoSessaoFalso("token-de-teste")
        estado = EstadoAdminFalso(auth)
        chamada = AsyncMock(return_value=resposta)
        passos = []
        with patch("revaulte.auth.chamar_xano", chamada):
            async for _ in AdminState.carregar_usuarios.fn(estado):
                passos.append((estado.situacao, list(estado.usuarios)))
        return estado, chamada, passos

    async def test_lista_com_os_cinco_campos(self):
        estado, chamada, passos = await self.carregar((200, LISTA_XANO))
        self.assertEqual(passos[0], ("carregando", []), "a lista anterior some durante o carregamento")
        metodo, url, token = chamada.await_args.args
        self.assertEqual((metodo, token), ("GET", "token-de-teste"))
        self.assertTrue(url.endswith("/users"))
        self.assertEqual(estado.situacao, "lista")
        self.assertEqual([dataclasses.asdict(linha) for linha in estado.usuarios], [
            {"id": 2, "nome": "Admin de Teste", "email": "admin@exemplo.com", "perfil": "Administrador",
             "desde": formatar_data(1763500000000)},
            {"id": 1, "nome": "Cliente de Teste", "email": "cliente@exemplo.com", "perfil": "Cliente",
             "desde": formatar_data(1763400000000)},
        ])
        texto = repr(estado.usuarios)
        for valor in (CPF_TESTE, "11900000000", "1990-05-10", "Rua de Teste", "hash-de-teste"):
            with self.subTest(valor=valor):
                self.assertNotIn(valor, texto)

    async def test_lista_vazia(self):
        estado, _, _ = await self.carregar((200, []))
        self.assertEqual((estado.situacao, estado.usuarios), ("lista", []))

    async def test_backend_recusa(self):
        for status in (401, 403):
            with self.subTest(status=status):
                estado, _, _ = await self.carregar((status, {"message": "forbidden"}))
                self.assertEqual((estado.situacao, estado.usuarios), ("restrito", []))

    async def test_falha_sem_dados_parciais(self):
        for resposta in ((0, None), (429, None), (500, {"message": "erro interno"}), (200, {"inesperado": 1}),
                         (200, None)):
            with self.subTest(resposta=resposta):
                estado, _, _ = await self.carregar(resposta)
                self.assertEqual((estado.situacao, estado.usuarios), ("erro", []))

if __name__ == "__main__":
    unittest.main()
