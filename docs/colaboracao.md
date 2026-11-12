# Revaulte — Guia de colaboração

## 1. Preparar um PC Windows

Instale, nesta ordem:

1. **Git for Windows** — https://git-scm.com/download/win (opções padrão).
2. **Python 3.12** — https://www.python.org/downloads/ — marque **“Add python.exe to PATH”** na primeira tela do instalador.
3. **Visual Studio Code** (recomendado) — https://code.visualstudio.com/

Confira no PowerShell:

```powershell
git --version
py -3.12 --version
```

Configure seu nome e e-mail no Git (os seus, não os de outro integrante) e a conversão de fim de linha:

```powershell
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
git config --global core.autocrlf true
```

## 2. Clonar o repositório

```powershell
cd $HOME\Documents
git clone https://github.com/26122024Ahlberg/Revaulte-.git Revaulte
cd Revaulte
```

O repositório é privado ou público conforme a configuração do GitHub; se for privado, o dono precisa adicionar o integrante como colaborador (GitHub → Settings → Collaborators) antes do clone.

## 3. Instalar e executar o frontend Reflex

```powershell
cd frontend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
reflex run
```

- Se o PowerShell recusar o `Activate.ps1`, execute uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente de novo (ou use o Prompt de Comando com `.venv\Scripts\activate.bat`).
- Na primeira execução o Reflex baixa o Bun e os pacotes JavaScript para `frontend/.web/` (precisa de internet e pode demorar alguns minutos).
- O site abre em http://localhost:3000/.
- Para parar, use `Ctrl+C` no terminal. Nas próximas vezes basta ativar o ambiente (`.\.venv\Scripts\Activate.ps1`) e rodar `reflex run`.

Testes automatizados:

```powershell
python -m unittest discover -s tests -v
```

## 4. O que não vai para o Git

`.venv/`, `.web/`, `.states/`, `__pycache__/`, `.env` e credenciais estão no `.gitignore`. Nunca coloque tokens, senhas ou credenciais do Xano em arquivos do projeto.

O **Xano CLI** e o **Xano Developer MCP** são opcionais para quem só mexe no frontend. Quem precisar deles faz o próprio login (`xano auth`); as credenciais ficam na pasta do usuário, fora do repositório. Envios ao Xano seguem o processo do projeto: cópia de segurança, prévia `--dry-run` e autorização do grupo, sem `--force` nem `--delete` automáticos.

## 5. Fluxo com branches

A `main` guarda somente versões revisadas e funcionando. Ninguém faz commit direto na `main`.

1. Atualize a `main` local antes de começar:
   ```powershell
   git switch main
   git pull
   ```
2. Crie uma branch para a tarefa, com o nome da Change do OpenSpec:
   ```powershell
   git switch -c feat/contas-acesso
   ```
   Prefixos: `feat/` (funcionalidade), `fix/` (correção), `docs/` (documentação).
3. Faça commits pequenos na branch e envie:
   ```powershell
   git add <arquivos>
   git commit -m "feat: descrição curta"
   git push -u origin feat/contas-acesso
   ```
4. Abra um **Pull Request** para a `main` no GitHub. Outro integrante revisa, confere que os testes passam e aprova o merge.
5. Depois do merge, volte à `main`, rode `git pull` e apague a branch local (`git branch -d feat/contas-acesso`).

Se a `main` andou enquanto você trabalhava, traga as mudanças para sua branch com `git pull origin main` (merge) e resolva conflitos localmente. Não use `git push --force` em branches compartilhadas.

### Divisão para evitar conflitos

Cada integrante trabalha em Changes diferentes do OpenSpec. Os arquivos mais disputados são `frontend/revaulte/components.py`, `frontend/revaulte/state.py` e `frontend/assets/styles.css`: combinem antes quem mexe neles, ou criem módulos novos (por exemplo, `frontend/revaulte/auth.py`) para funcionalidades novas.

### Proteção da `main` (configurar uma vez no GitHub)

GitHub → repositório → **Settings → Branches → Add branch ruleset** (ou “Branch protection rule”) para `main`:

- exigir Pull Request antes do merge, com ao menos 1 aprovação;
- bloquear force push e exclusão da branch.
