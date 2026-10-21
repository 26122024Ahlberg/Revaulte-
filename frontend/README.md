# Revaulte — frontend em Reflex

Aplicativo web da Revaulte, desenvolvido em [Reflex](https://reflex.dev) (Python). A versão anterior em HTML, CSS e JavaScript puro fica em `../frontend-html/` apenas como referência.

## Requisitos

- Python 3.11 ou superior (o projeto usa Python 3.12, instalado pelo Homebrew: `brew install python@3.12`).
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

O app abre em `http://localhost:3000/` (a raiz redireciona para `/catalogo`). Se a porta estiver ocupada, o Reflex usa a próxima disponível e mostra o endereço no terminal.

## Imagens de terceiros

Fotos do carrossel da página inicial, todas obtidas no Pexels e marcadas como gratuitas:

| Arquivo | Foto | Autor |
| --- | --- | --- |
| `assets/hero-esportivo.jpg` | https://www.pexels.com/photo/red-car-driving-on-road-along-fence-3466513/ | Abdulwahab Alawadhi |
| `assets/hero-modificado.jpg` | https://www.pexels.com/photo/modified-audi-s4-9661333/ | Erik Mclean |
| `assets/hero-classico.jpg` | https://www.pexels.com/photo/vintage-red-sports-car-by-scenic-roadside-38058755/ | Seppo Vänni |

Licença do Pexels (https://www.pexels.com/license/): uso gratuito, inclusive em sites, sem atribuição obrigatória; não é permitido vender cópias inalteradas, usar as fotos como marca nem sugerir endosso de pessoas ou marcas retratadas. Os créditos acima são registrados por cortesia. As fotos foram reduzidas para até 1920 px de largura.

## Testes

```bash
source .venv/bin/activate
python -m unittest discover -s tests -v
```

## Arquivos que não são versionados

`.venv/`, `.web/`, `.states/` e `__pycache__/` são gerados localmente e estão no `.gitignore` da raiz do repositório. Nenhum token, senha ou credencial deve ser colocado nos arquivos desta pasta.
