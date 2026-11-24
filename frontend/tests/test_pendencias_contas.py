# Testes das correções finais de contas-acesso (tarefas 2.3, 2.4, 2.13 e 3.6). Leem somente
# arquivos locais de xano/ e usam respostas simuladas; não chamam o Xano.
# Execução, dentro de frontend/: python -m unittest discover -s tests
import re
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

XANO = Path(__file__).resolve().parents[2] / "xano"

# Endpoints que podem existir sem `auth` (tarefa 2.4): cadastro, login, catálogo público e os três
# do Quick Start já desativados (respondem 404 sem consultar nada).
SEM_AUTH_PERMITIDOS = {
    "api/authentication/auth/login_POST.xs": "login",
    "api/authentication/auth/signup_POST.xs": "cadastro",
    "api/catalog/vehicles_GET.xs": "catálogo",
    "api/catalog/vehicles_vehicle_id_GET.xs": "catálogo",
    "api/authentication/message/send_welcome_email_POST.xs": "desativado",
    "api/authentication/reset/request_reset_link_GET.xs": "desativado",
    "api/authentication/reset/magic_link_login_POST.xs": "desativado",
}
DESATIVADOS = [c for c, motivo in SEM_AUTH_PERMITIDOS.items() if motivo == "desativado"]


def sem_comentarios(texto: str) -> str:
    return "\n".join(l for l in texto.splitlines() if not l.strip().startswith("//"))


def endpoints() -> dict[str, str]:
    saida = {}
    for arquivo in sorted((XANO / "api").rglob("*.xs")):
        texto = sem_comentarios(arquivo.read_text(encoding="utf-8"))
        if re.search(r"^query\b", texto, re.M):  # exclui os arquivos de api_group
            saida[arquivo.relative_to(XANO).as_posix()] = texto
    return saida


def endpoints_sem_auth(mapa: dict[str, str]) -> set[str]:
    return {c for c, t in mapa.items() if not re.search(r'^\s*auth\s*=\s*"user"', t, re.M)}


class TestEndpointsSemAutenticacao(unittest.TestCase):
    def test_somente_a_lista_permitida_fica_sem_auth(self):
        mapa = endpoints()
        self.assertGreater(len(mapa), 10)
        self.assertEqual(endpoints_sem_auth(mapa), set(SEM_AUTH_PERMITIDOS))

    def test_detecta_endpoint_novo_sem_auth(self):
        mapa = dict(endpoints())
        mapa["api/anuncios/novo_GET.xs"] = 'query novo verb=GET {\n  api_group = "Anuncios"\n  stack {\n  }\n}'
        self.assertIn("api/anuncios/novo_GET.xs", endpoints_sem_auth(mapa) - set(SEM_AUTH_PERMITIDOS))

    def test_detecta_endpoint_protegido_que_perdeu_o_auth(self):
        mapa = dict(endpoints())
        caminho = "api/favoritos/favoritos_GET.xs"
        mapa[caminho] = mapa[caminho].replace('auth = "user"', "")
        self.assertIn(caminho, endpoints_sem_auth(mapa) - set(SEM_AUTH_PERMITIDOS))

    def test_desativados_nao_tocam_banco_nem_sessao(self):
        mapa = endpoints()
        for caminho in DESATIVADOS:
            texto = mapa[caminho]
            with self.subTest(caminho):
                self.assertIn("precondition (false)", texto)
                for proibido in ("db.", "function.run", "security.create_auth_token", "email."):
                    self.assertNotIn(proibido, texto)


class TestMyEventsMinimo(unittest.TestCase):
    def setUp(self):
        self.texto = endpoints()["api/event_logs/logs/user/my_events_GET.xs"]

    def test_so_eventos_da_propria_conta(self):
        self.assertIn('auth = "user"', self.texto)
        self.assertIn("$db.event_log.user_id == $auth.id", self.texto)
        entrada = re.search(r"input \{(.*?)\}", self.texto, re.S).group(1)
        self.assertEqual(entrada.strip(), "")

    def test_saida_minima_sem_user_id_nem_metadata(self):
        saida = re.search(r"output = \[(.*?)\]", self.texto, re.S).group(1)
        self.assertEqual(re.findall(r'"(\w+)"', saida), ["id", "created_at", "action"])

    def test_resposta_continua_sendo_lista(self):
        self.assertIn('return = {type: "list"}', self.texto)
        self.assertIn("response = $user_events", self.texto)
        self.assertNotIn("paging", self.texto)

    def test_identidade_preservada(self):
        self.assertIn('query "logs/user/my_events" verb=GET', self.texto)
        self.assertIn('guid = "-iyXujeFKm9_O0k4fzsZ2DxVTe4"', self.texto)

    def test_event_log_nunca_recebe_dados_pessoais(self):
        for caminho, texto in endpoints().items():
            for m in re.finditer(r"metadata\s*:\s*([^\n]+)", texto):
                with self.subTest(caminho=caminho):
                    # `{}` literal; na mesma linha pode vir o `}` que fecha o bloco `input = {...}`.
                    self.assertRegex(m.group(1).strip(), r"^\{\}\}?$")


class TestDataDeNascimentoLimites(unittest.TestCase):
    """O backend compara com a data de hoje em Brasília (UTC−03:00), como o frontend."""

    def modelo_backend(self, nascimento: str, agora_utc: datetime) -> bool:
        hoje_brasilia = (agora_utc - timedelta(hours=3)).date()
        data = date.fromisoformat(nascimento)
        return date(1900, 1, 1) <= data < hoje_brasilia

    def test_regra_do_backend_no_arquivo(self):
        texto = endpoints()["api/authentication/auth/signup_POST.xs"]
        self.assertIn('now|format_timestamp:"Y-m-d":"America/Sao_Paulo"|to_timestamp:"UTC"', texto)
        self.assertIn(
            'precondition ($nascimento < $hoje_brasilia && $nascimento >= ("1900-01-01"|to_timestamp:"UTC"))', texto
        )
        self.assertNotIn("$nascimento < now", texto)

    def test_limites_iguais_no_frontend_e_no_modelo_do_backend(self):
        from revaulte.auth import FUSO, ler_data_nascimento

        # Instantes UTC ao redor da meia-noite de Brasília (03:00 UTC).
        for agora_utc in (datetime(2026, 11, 24, 2, 59, tzinfo=timezone.utc),
                          datetime(2026, 11, 24, 3, 0, tzinfo=timezone.utc),
                          datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc),
                          datetime(2026, 11, 25, 1, 0, tzinfo=timezone.utc)):
            hoje = agora_utc.astimezone(FUSO).date()
            for texto in ("1899-12-31", "1900-01-01", "2000-02-29", (hoje - timedelta(days=1)).isoformat(),
                          hoje.isoformat(), (hoje + timedelta(days=1)).isoformat()):
                with self.subTest(agora=agora_utc.isoformat(), nascimento=texto):
                    frontend = ler_data_nascimento(texto, hoje) is not None
                    self.assertEqual(frontend, self.modelo_backend(texto, agora_utc))

    def test_data_de_hoje_e_recusada_e_ontem_e_aceita(self):
        from revaulte.auth import ler_data_nascimento

        hoje = date(2026, 11, 24)
        self.assertIsNone(ler_data_nascimento("2026-11-24", hoje))
        self.assertEqual(ler_data_nascimento("2026-11-23", hoje), date(2026, 11, 23))
        self.assertIsNone(ler_data_nascimento("1899-12-31", hoje))
        self.assertEqual(ler_data_nascimento("1900-01-01", hoje), date(1900, 1, 1))


class TestLimiteDeRequisicoes(unittest.TestCase):
    def test_429_tem_mensagem_propria_no_cadastro(self):
        from revaulte.auth import ERRO_GENERICO, ERRO_MUITAS_TENTATIVAS, mensagem_erro_cadastro

        self.assertEqual(mensagem_erro_cadastro(429, {"code": "ERROR_CODE_TOO_MANY_REQUESTS"}), ERRO_MUITAS_TENTATIVAS)
        self.assertEqual(mensagem_erro_cadastro(429, None), ERRO_MUITAS_TENTATIVAS)
        self.assertEqual(mensagem_erro_cadastro(500, None), ERRO_GENERICO)
        self.assertEqual(mensagem_erro_cadastro(0, None), ERRO_GENERICO)

    def test_mensagem_igual_a_dos_anuncios_e_favoritos(self):
        from revaulte.anuncios import ERRO_MUITAS_TENTATIVAS as anuncios
        from revaulte.auth import ERRO_MUITAS_TENTATIVAS as auth
        from revaulte.favoritos import ERRO_MUITAS_TENTATIVAS as favoritos

        self.assertEqual(auth, anuncios)
        self.assertEqual(auth, favoritos)
