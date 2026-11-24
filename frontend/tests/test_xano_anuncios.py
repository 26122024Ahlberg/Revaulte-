# Testes estáticos dos arquivos XanoScript de anúncios (Change anuncios-cliente, tarefa 2.4).
# Leem somente os arquivos locais em xano/; não chamam o Xano.
# Execução, dentro de frontend/: python -m unittest discover -s tests -v
import re
import unittest
from pathlib import Path

XANO = Path(__file__).resolve().parents[2] / "xano"
PASTA_ANUNCIOS = XANO / "api" / "anuncios"
ENDPOINTS = ("anuncios_POST.xs", "anuncios_GET.xs", "anuncios_vehicle_id_GET.xs")

# Nunca podem sair nas respostas de anúncios (spec "Respostas privadas sem dados internos").
CAMPOS_PROIBIDOS_SAIDA = (
    "user_id", "seller_id", "whatsapp", "contact_authorized", "contact_authorized_at",
    "email", "password", "cpf", "phone", "birth_date", "address", "cover_image_url",
)
# Nunca podem ser recebidos do navegador (spec "Vínculo definido pela sessão").
CAMPOS_PROIBIDOS_ENTRADA = ("status", "seller_id", "user_id", "cover_image_url", "id", "created_at")


def sem_comentarios(texto: str) -> str:
    return "\n".join(linha for linha in texto.splitlines() if not linha.strip().startswith("//"))


def ler(caminho: Path) -> str:
    return sem_comentarios(caminho.read_text(encoding="utf-8"))


def bloco(texto: str, abertura: str) -> str:
    """Conteúdo de um bloco { ... } iniciado por `abertura`, com chaves aninhadas."""
    inicio = texto.index(abertura) + len(abertura)
    nivel = 1
    for posicao in range(inicio, len(texto)):
        if texto[posicao] == "{":
            nivel += 1
        elif texto[posicao] == "}":
            nivel -= 1
            if nivel == 0:
                return texto[inicio:posicao]
    raise ValueError(f"bloco sem fechamento: {abertura}")


def campos_de_saida(texto: str) -> list[str]:
    """Nomes listados nos `output = [...]` do arquivo, exceto os das consultas internas ao registro
    seller_account (usadas só para decidir o anunciante; o teste test_registro_nunca_na_resposta
    garante que nunca chegam a um `response`)."""
    while "db.query seller_account {" in texto:
        interno = "db.query seller_account {" + bloco(texto, "db.query seller_account {") + "}"
        texto = texto.replace(interno, "", 1)
    campos = []
    for lista in re.findall(r"output = \[(.*?)\]", texto, re.S):
        campos += re.findall(r'"([a-z_]+)"', lista)
    return campos


def campos_de_entrada(texto: str) -> list[str]:
    """Nomes declarados no bloco input (tipo, ? opcional, nome)."""
    entrada = bloco(texto, "input {")
    return re.findall(r"^\s*[a-z]+\??\s+([a-z_]+)\??", entrada, re.M)


def problemas_endpoint(texto: str) -> list[str]:
    """Regras de segurança comuns aos endpoints de anúncios; lista vazia quando tudo está certo."""
    problemas = []
    if 'auth = "user"' not in texto:
        problemas.append("sem auth = \"user\"")
    if 'api_group = "Anuncios"' not in texto:
        problemas.append("fora do grupo Anuncios")
    pilha = bloco(texto, "stack {").lstrip()
    if not pilha.startswith('function.run "Quick Start/enforce_role"'):
        problemas.append("enforce_role não é a primeira etapa")
    if 'required_role: "member"' not in texto or "user_id: $auth.id" not in texto:
        problemas.append("enforce_role sem $auth.id ou sem perfil member")
    for campo in campos_de_saida(texto):
        if campo in CAMPOS_PROIBIDOS_SAIDA:
            problemas.append(f"campo proibido na saída: {campo}")
    for campo in campos_de_entrada(texto):
        if campo in CAMPOS_PROIBIDOS_ENTRADA:
            problemas.append(f"campo proibido na entrada: {campo}")
    return problemas


# Entradas em que false ou 0 são valores válidos: só aceitam comparação estrita com null (!== / ===).
CAMPOS_FALSE_OU_ZERO_VALIDOS = ("is_modified", "mileage")


def problemas_null_frouxo(texto: str) -> list[str]:
    """Campos de CAMPOS_FALSE_OU_ZERO_VALIDOS comparados com null por != ou == (frouxos)."""
    return [
        campo for campo in CAMPOS_FALSE_OU_ZERO_VALIDOS
        if re.search(rf"\$input\.{campo}\s*(!=|==)(?!=)\s*null", texto)
    ]


class TestRegrasComunsDosEndpoints(unittest.TestCase):
    def test_grupo_restrito(self):
        grupo = ler(PASTA_ANUNCIOS / "anuncios.xs")
        self.assertIn("api_group Anuncios", grupo)
        self.assertIn('canonical = "revaulte-anuncios"', grupo)
        self.assertIn("swagger = {active: false}", grupo)

    def test_somente_os_endpoints_previstos(self):
        arquivos = sorted(p.name for p in PASTA_ANUNCIOS.glob("*.xs"))
        self.assertEqual(arquivos, sorted(("anuncios.xs", *ENDPOINTS)))

    def test_endpoints_sem_problemas(self):
        for nome in ENDPOINTS:
            with self.subTest(arquivo=nome):
                self.assertEqual(problemas_endpoint(ler(PASTA_ANUNCIOS / nome)), [])

    def test_registro_nunca_na_resposta(self):
        for nome in ENDPOINTS:
            texto = ler(PASTA_ANUNCIOS / nome)
            resposta = texto[texto.index("  response = "):]
            with self.subTest(arquivo=nome):
                for variavel in ("$registro", "$registro_previo", "$novo_registro", "$seller_id"):
                    self.assertNotIn(variavel, resposta)

    def test_verificacao_detecta_endpoint_sem_auth(self):
        # Cópia em memória sem o auth: a verificação precisa apontar o problema.
        for nome in ENDPOINTS:
            copia = ler(PASTA_ANUNCIOS / nome).replace('auth = "user"', "")
            with self.subTest(arquivo=nome):
                self.assertIn('sem auth = "user"', problemas_endpoint(copia))

    def test_verificacao_detecta_enforce_role_fora_do_inicio(self):
        copia = ler(PASTA_ANUNCIOS / "anuncios_GET.xs").replace(
            "stack {", "stack {\n    var $x {\n      value = 1\n    }\n", 1
        )
        self.assertIn("enforce_role não é a primeira etapa", problemas_endpoint(copia))

    def test_verificacao_detecta_campo_proibido(self):
        copia = ler(PASTA_ANUNCIOS / "anuncios_GET.xs").replace('"status"', '"seller_id"')
        self.assertIn("campo proibido na saída: seller_id", problemas_endpoint(copia))
        copia = ler(PASTA_ANUNCIOS / "anuncios_POST.xs").replace("bool? is_modified?", "text? status?")
        self.assertIn("campo proibido na entrada: status", problemas_endpoint(copia))

    def test_dono_somente_pelo_token(self):
        for nome in ENDPOINTS:
            texto = ler(PASTA_ANUNCIOS / nome)
            with self.subTest(arquivo=nome):
                self.assertIn("$db.seller_account.user_id == $auth.id", texto)
                self.assertNotIn("$input.user_id", texto)
                self.assertNotIn("$input.seller_id", texto)
                self.assertNotIn("$input.status", texto)


class TestCriacaoDeAnuncio(unittest.TestCase):
    def setUp(self):
        self.texto = ler(PASTA_ANUNCIOS / "anuncios_POST.xs")
        self.transacao = bloco(self.texto, "db.transaction {")

    def test_rascunho_explicito(self):
        dados = bloco(self.texto, "db.add vehicle {")
        self.assertRegex(dados, r'status\s*:\s*"draft"')
        self.assertRegex(dados, r"is_modified\s*:\s*\$input\.is_modified")
        self.assertRegex(dados, r"seller_id\s*:\s*\$seller_id")

    def test_novo_anunciante_sem_contato_e_sem_conta_na_tabela_seller(self):
        dados = bloco(self.texto, "db.add seller {")
        self.assertRegex(dados, r"contact_authorized\s*:\s*false")
        self.assertRegex(dados, r"whatsapp\s*:\s*null")
        self.assertNotIn("contact_authorized_at", dados)
        # O vínculo com a conta fica só em seller_account (opção A, 23/11/2026).
        self.assertNotIn("user_id", dados)

    def test_registro_da_conta_pelo_token(self):
        dados = bloco(self.texto, "db.add seller_account {")
        self.assertRegex(dados, r"user_id\s*:\s*\$auth\.id")
        self.assertRegex(dados, r"seller_id\s*:\s*\$novo_anunciante\.id")

    def test_nenhum_registro_apagado_ou_alterado(self):
        # R1 (23/11/2026): o endpoint só insere; nenhuma remoção de duplicados.
        for operacao in ("db.del", "db.edit", "db.patch", "db.add_or_edit", "db.bulk", "db.truncate"):
            with self.subTest(operacao=operacao):
                self.assertNotIn(operacao, self.texto)
        self.assertEqual(self.texto.count("db.add "), 3)

    def test_sem_redis(self):
        # Opção A (23/11/2026): Data Caching via Redis não faz parte do plano Free.
        for nome in ("anuncios.xs", *ENDPOINTS):
            with self.subTest(arquivo=nome):
                self.assertNotIn("redis.", ler(PASTA_ANUNCIOS / nome))

    def test_leitura_e_gravacao_na_mesma_transacao(self):
        self.assertNotIn("isolation", self.transacao)  # não aceito pelo validador do Xano
        for trecho in (
            'return = {type: "count"}', "db.query seller_account {", "db.add seller {",
            "db.add seller_account {", "db.add vehicle {",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.transacao)
        # Fora da transação só fica a consulta prévia (sem gravação).
        fora = self.texto.replace(self.transacao, "")
        self.assertNotIn("db.add ", fora)

    def test_anunciante_criado_e_registrado_juntos(self):
        # O anunciante só é criado junto com o registro único; senão, reutiliza o registrado.
        criacao = bloco(self.transacao, "if ($registro == null) {")
        self.assertLess(criacao.index("db.add seller {"), criacao.index("db.add seller_account {"))
        self.assertIn("value = $novo_anunciante.id", criacao)
        reutilizacao = bloco(self.transacao, "else {")
        self.assertIn("value = $registro.seller_id", reutilizacao)
        self.assertNotIn("db.add", reutilizacao)
        # O veículo é gravado depois do registro, já com o anunciante decidido.
        self.assertLess(self.transacao.index("db.add seller_account {"), self.transacao.index("db.add vehicle {"))

    def test_limite_de_20_rascunhos(self):
        contagem = bloco(self.transacao, "db.query vehicle {")
        self.assertIn("where: $db.vehicle.seller_id == $db.seller_account.seller_id", contagem)
        self.assertIn('$db.seller_account.user_id == $auth.id && $db.vehicle.status == "draft"', contagem)
        self.assertIn("precondition ($rascunhos < 20)", self.transacao)
        self.assertIn('error = "draft_limit_reached"', self.transacao)
        self.assertLess(self.transacao.index("precondition ($rascunhos < 20)"), self.transacao.index("db.add "))

    def test_validacao_antes_de_gravar(self):
        primeira_gravacao = self.texto.index("db.add")
        for codigo in (
            "invalid_brand", "invalid_model", "invalid_version", "invalid_year", "invalid_condition",
            "invalid_mileage", "invalid_price", "invalid_is_modified", "invalid_color", "invalid_engine",
            "invalid_transmission", "invalid_description", "invalid_display_name",
        ):
            with self.subTest(codigo=codigo):
                self.assertIn(f'error = "{codigo}"', self.texto)
                self.assertLess(self.texto.index(f'error = "{codigo}"'), primeira_gravacao)

    def test_regressao_comparacao_estrita_com_null(self):
        # Falha real da tarefa 3.4 (23/11/2026): "!= null" é frouxa no XanoScript e trata false e 0
        # como null, recusando is_modified false (invalid_is_modified) e quilometragem 0.
        self.assertIn("precondition ($input.is_modified !== null) {", self.texto)
        self.assertIn("precondition ($input.mileage !== null && $input.mileage >= 0", self.texto)
        self.assertEqual(problemas_null_frouxo(self.texto), [])

    def test_regressao_detecta_comparacao_frouxa(self):
        # Cópias em memória com o defeito original: a verificação precisa apontar cada uma.
        for estrita, campo in (
            ("$input.is_modified !== null", "is_modified"),
            ("$input.mileage !== null", "mileage"),
        ):
            with self.subTest(campo=campo):
                copia = self.texto.replace(estrita, estrita.replace("!==", "!="))
                self.assertEqual(problemas_null_frouxo(copia), [campo])

    def test_nome_exigido_so_sem_registro(self):
        previo = self.texto[: self.texto.index("db.transaction {")]
        self.assertIn("db.query seller_account {", previo)
        self.assertIn("if ($registro_previo == null) {", previo)
        self.assertLess(previo.index("if ($registro_previo == null) {"), previo.index('error = "invalid_display_name"'))

    def test_limites_do_design(self):
        for trecho in (
            "($input.brand|strlen) <= 40", "($input.model|strlen) <= 60", "($input.version|strlen) <= 80",
            "$input.year >= 1886", "$input.year <= $ano_maximo",
            '$input.condition == "new" || $input.condition == "used"',
            "$input.mileage >= 0 && $input.mileage <= 2000000",
            "$input.price > 0 && $input.price <= 100000000", "($input.price|round:2) == $input.price",
            "($input.description|strlen) <= 2000", "($input.display_name|strlen) >= 2",
            "($input.display_name|strlen) <= 60",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.texto)

    def test_resposta_minima(self):
        self.assertIn("response = {id: $veiculo.id, status: $veiculo.status}", self.texto)

    def test_sem_log_de_eventos(self):
        for nome in ENDPOINTS:
            with self.subTest(arquivo=nome):
                self.assertNotIn("log_event", ler(PASTA_ANUNCIOS / nome))


class TestConsultaDosProprios(unittest.TestCase):
    def test_lista_junta_registro_da_conta(self):
        texto = ler(PASTA_ANUNCIOS / "anuncios_GET.xs")
        self.assertEqual(texto.count('type : "inner"'), 2)
        self.assertIn("where: $db.vehicle.seller_id == $db.seller_account.seller_id", texto)
        self.assertIn("where: $db.seller.id == $db.seller_account.seller_id", texto)
        self.assertEqual(texto.count("where = $db.seller_account.user_id == $auth.id"), 2)
        self.assertIn('sort = {vehicle.created_at: "desc"}', texto)
        self.assertIn("response = {anunciante: $anunciante, anuncios: $anuncios}", texto)
        self.assertIn('output = ["display_name"]', texto)

    def test_ficha_404_unico(self):
        texto = ler(PASTA_ANUNCIOS / "anuncios_vehicle_id_GET.xs")
        self.assertIn("where: $db.vehicle.seller_id == $db.seller_account.seller_id", texto)
        self.assertIn("$db.vehicle.id == $input.vehicle_id && $db.seller_account.user_id == $auth.id", texto)
        self.assertIn('error_type = "notfound"', texto)
        # Um único precondition: nada diferencia "inexistente" de "de outra conta".
        self.assertEqual(texto.count("precondition"), 1)

    def test_vinculo_antigo_nao_usado(self):
        for nome in ENDPOINTS:
            with self.subTest(arquivo=nome):
                self.assertNotIn("$db.seller.user_id", ler(PASTA_ANUNCIOS / nome))


class TestTabelas(unittest.TestCase):
    def test_seller_account_com_indices_unicos(self):
        texto = ler(XANO / "table" / "seller_account.xs").replace("\r\n", "\n")
        self.assertIn("table seller_account {", texto)
        # Campos obrigatórios: nunca nulos, então o índice único não depende do tratamento de vazios.
        self.assertIn('int user_id {\n      table = "user"\n    }', texto)
        self.assertIn('int seller_id {\n      table = "seller"\n    }', texto)
        self.assertNotIn("user_id?", texto)
        self.assertNotIn("seller_id?", texto)
        self.assertIn('{type: "btree|unique", field: [{name: "user_id"}]}', texto)
        self.assertIn('{type: "btree|unique", field: [{name: "seller_id"}]}', texto)

    def test_seller_sem_alteracao(self):
        # A tabela do anunciante do Opala não muda nesta Change.
        texto = ler(XANO / "table" / "seller.xs")
        self.assertNotIn("user_id", texto)
        self.assertIn('{type: "primary", field: [{name: "id"}]}', texto)


class TestCatalogoPublicoInalterado(unittest.TestCase):
    """Os endpoints públicos continuam com a lista permitida e sem dados do vínculo novo."""

    def test_listagem_publica(self):
        texto = ler(XANO / "api" / "catalog" / "vehicles_GET.xs")
        self.assertNotIn("auth =", texto)
        self.assertIn('$db.vehicle.status == "available" || $db.vehicle.status == "sold"', texto)
        self.assertNotIn("user_id", texto)
        self.assertNotIn("seller_account", texto)

    def test_detalhe_publico(self):
        texto = ler(XANO / "api" / "catalog" / "vehicles_vehicle_id_GET.xs")
        self.assertNotIn("auth =", texto)
        self.assertIn('($db.vehicle.status == "available" || $db.vehicle.status == "sold")', texto)
        self.assertIn('output = ["display_name", "whatsapp", "contact_authorized"]', texto)
        self.assertNotIn("user_id", texto)
        self.assertNotIn("seller_account", texto)


if __name__ == "__main__":
    unittest.main()
