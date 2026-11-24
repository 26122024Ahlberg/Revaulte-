# Endereço base da API do catálogo (tarefa 8.1).
# É um endereço público: não inclua tokens, chaves ou credenciais neste arquivo.
import os

# Grupo de API público "Catalog" no Xano (o mesmo usado por frontend-html/js/config.js).
CATALOG_API_URL_PADRAO = "https://x8ki-letl-twmt.n7.xano.io/api:ghostpay-catalog"


def catalog_api_url() -> str:
    """Endereço base do catálogo, lido de REVAULTE_CATALOG_API_URL ou do valor padrão.

    A barra final é removida para que os caminhos possam ser acrescentados como "/vehicles".
    """
    url = os.environ.get("REVAULTE_CATALOG_API_URL", "").strip()
    return (url or CATALOG_API_URL_PADRAO).rstrip("/")


# Grupos de API de contas (Change contas-acesso). Também são endereços públicos:
# o token do usuário nunca é gravado em arquivo, só enviado no cabeçalho de cada requisição.
AUTH_API_URL_PADRAO = "https://x8ki-letl-twmt.n7.xano.io/api:shCFXLjC"
ADMIN_API_URL_PADRAO = "https://x8ki-letl-twmt.n7.xano.io/api:revaulte-admin"
# Grupo de anúncios dos Clientes (Change anuncios-cliente); todos os endpoints exigem token.
ANUNCIOS_API_URL_PADRAO = "https://x8ki-letl-twmt.n7.xano.io/api:revaulte-anuncios"
# Grupo de favoritos dos Clientes (Change favoritos); todos os endpoints exigem token.
FAVORITOS_API_URL_PADRAO = "https://x8ki-letl-twmt.n7.xano.io/api:revaulte-favoritos"


def _url(variavel: str, padrao: str) -> str:
    return (os.environ.get(variavel, "").strip() or padrao).rstrip("/")


def auth_api_url() -> str:
    """Grupo "Authentication" (cadastro, login e auth/me); REVAULTE_AUTH_API_URL substitui o padrão."""
    return _url("REVAULTE_AUTH_API_URL", AUTH_API_URL_PADRAO)


def admin_api_url() -> str:
    """Grupo "Admin"; REVAULTE_ADMIN_API_URL substitui o padrão."""
    return _url("REVAULTE_ADMIN_API_URL", ADMIN_API_URL_PADRAO)


def anuncios_api_url() -> str:
    """Grupo "Anuncios" (enviar e consultar os próprios anúncios); REVAULTE_ANUNCIOS_API_URL substitui o padrão."""
    return _url("REVAULTE_ANUNCIOS_API_URL", ANUNCIOS_API_URL_PADRAO)


def favoritos_api_url() -> str:
    """Grupo "Favoritos" (favoritar, remover e listar); REVAULTE_FAVORITOS_API_URL substitui o padrão."""
    return _url("REVAULTE_FAVORITOS_API_URL", FAVORITOS_API_URL_PADRAO)
