# Revaulte — frontend em Reflex

Aplicativo web da Revaulte, desenvolvido em [Reflex](https://reflex.dev) (Python). A versão anterior em HTML, CSS e JavaScript puro fica em `../frontend-html/` apenas como referência.

## Requisitos

- Python 3.11 ou superior (o projeto usa Python 3.12, instalado pelo Homebrew no macOS: `brew install python@3.12`). No Windows, siga `../docs/colaboracao.md`.
- Acesso à internet na primeira execução: o Reflex baixa automaticamente as ferramentas de frontend que usa (Bun e pacotes JavaScript) para a pasta `.web/`.

## Instalação

Dentro desta pasta (`frontend/`):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução local

```bash
source .venv/bin/activate
reflex run
```

O app abre em `http://localhost:3000/`, na página inicial (`/`). As demais páginas públicas são `/estoque`, `/usados`, `/modificados` e `/veiculo/<id>`; o endereço antigo `/catalogo` redireciona para `/estoque`. Se a porta estiver ocupada, o Reflex usa a próxima disponível e mostra o endereço no terminal.

Páginas de conta (Change `contas-acesso`):

| Página | Acesso |
| --- | --- |
| `/entrar` | login com e-mail e senha |
| `/cadastro` | cadastro de Cliente |
| `/conta` | Minha conta (exige login) |
| `/admin` | lista de usuários (exige perfil Administrador, conferido no backend) |

## Endereços do backend (Xano)

Os endereços padrão estão em `revaulte/config.py` e são públicos. Cada um pode ser substituído por uma variável de ambiente antes do `reflex run`:

| Variável | Grupo de API | Padrão |
| --- | --- | --- |
| `REVAULTE_CATALOG_API_URL` | Catálogo | `https://x8ki-letl-twmt.n7.xano.io/api:ghostpay-catalog` |
| `REVAULTE_AUTH_API_URL` | Cadastro, login e `auth/me` | `https://x8ki-letl-twmt.n7.xano.io/api:shCFXLjC` |
| `REVAULTE_ADMIN_API_URL` | Área administrativa | `https://x8ki-letl-twmt.n7.xano.io/api:revaulte-admin` |
| `REVAULTE_ANUNCIOS_API_URL` | Anúncios dos Clientes (exige sessão) | `https://x8ki-letl-twmt.n7.xano.io/api:revaulte-anuncios` |

O token de sessão fica só no cookie `revaulte_sessao` do navegador (validade de 24 h) e nunca é gravado em arquivo. O plano gratuito do Xano aceita 10 requisições a cada 20 s; acima disso, o site mostra a mensagem genérica de erro.

## Imagens de terceiros

Fotos do carrossel da página inicial, todas obtidas no Pexels e marcadas como gratuitas:

| Arquivo | Foto | Autor |
| --- | --- | --- |
| `assets/hero-esportivo.jpg` | https://www.pexels.com/photo/red-car-driving-on-road-along-fence-3466513/ | Abdulwahab Alawadhi |
| `assets/hero-modificado.jpg` | https://www.pexels.com/photo/modified-audi-s4-9661333/ | Erik Mclean |
| `assets/hero-classico.jpg` | https://www.pexels.com/photo/vintage-red-sports-car-by-scenic-roadside-38058755/ | Seppo Vänni |
| `assets/banner-estoque.jpg` | https://www.pexels.com/photo/sleek-white-sports-car-in-dark-garage-setting-33268786/ | Quentin Martinez |
| `assets/banner-usados.jpg` | https://www.pexels.com/photo/side-view-of-a-vintage-car-11503885/ | Jvxhn Visuals |
| `assets/banner-modificados.jpg` | https://www.pexels.com/photo/side-view-of-a-sports-car-in-a-car-park-22039985/ | Erik Mclean |

Licença do Pexels (https://www.pexels.com/license/): uso gratuito, inclusive em sites, sem atribuição obrigatória; não é permitido vender cópias inalteradas, usar as fotos como marca nem sugerir endosso de pessoas ou marcas retratadas. Os créditos acima são registrados por cortesia. As fotos foram reduzidas para até 1920 px de largura.

## Testes

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## Arquivos que não são versionados

`.venv/`, `.web/`, `.states/` e `__pycache__/` são gerados localmente e estão no `.gitignore` da raiz do repositório. Nenhum token, senha ou credencial deve ser colocado nos arquivos desta pasta.
