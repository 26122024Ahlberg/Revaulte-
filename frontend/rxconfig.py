import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="revaulte",
    # Servidor de desenvolvimento acessível somente pela própria máquina.
    backend_host="127.0.0.1",
    # Não envia dados de uso ao Reflex.
    telemetry_enabled=False,
    # O mapa do site não é necessário enquanto houver uma única página.
    disable_plugins=[SitemapPlugin],
)
