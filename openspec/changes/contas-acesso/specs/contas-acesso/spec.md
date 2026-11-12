# Spec Delta

## Purpose

Permite que visitantes criem uma conta de Cliente, entrem e saiam da Revaulte, e restringe páginas e endpoints conforme o perfil de acesso (Cliente ou Administrador).

## ADDED Requirements

### Requirement: Cadastro de Cliente
O site SHALL oferecer a página `/cadastro` com nome, CPF, e-mail, telefone, data de nascimento, endereço, senha e confirmação de senha, todos obrigatórios. O backend SHALL criar a conta sempre com o perfil Cliente, recusar e-mail ou CPF já cadastrados e armazenar a senha somente como hash. Após o cadastro, o usuário SHALL ficar autenticado.

#### Scenario: Cadastro válido
- **WHEN** o visitante preenche todos os campos com dados válidos e envia
- **THEN** a conta é criada com perfil Cliente, o usuário fica autenticado e é levado a “Minha conta”

#### Scenario: E-mail ou CPF já cadastrado
- **WHEN** o visitante envia um e-mail ou CPF que já pertence a outra conta
- **THEN** a conta não é criada e o formulário informa qual dado já está cadastrado

#### Scenario: Dados inválidos
- **WHEN** o CPF é inválido, a senha tem menos de 8 caracteres ou não tem letra e número, as senhas não coincidem ou algum campo está vazio
- **THEN** o formulário informa o problema em português e nada é enviado ao backend

### Requirement: Login e saída
O site SHALL oferecer a página `/entrar` com e-mail e senha. Credenciais inválidas SHALL gerar a mesma mensagem, sem revelar se o e-mail existe. A sessão SHALL durar no máximo 24 horas, e “Sair” SHALL encerrá-la no navegador.

#### Scenario: Login válido
- **WHEN** o usuário informa e-mail e senha corretos
- **THEN** fica autenticado e é levado à página de origem ou a “Minha conta”

#### Scenario: Credenciais inválidas
- **WHEN** o e-mail não existe ou a senha está errada
- **THEN** o site exibe “E-mail ou senha incorretos.” e o usuário continua sem sessão

#### Scenario: Sair
- **WHEN** o usuário autenticado aciona “Sair”
- **THEN** a sessão é removida do navegador e o menu volta a oferecer “Entrar / Cadastrar”

### Requirement: Páginas protegidas
`/conta` SHALL exigir sessão válida, confirmada no backend a cada abertura. `/admin` SHALL exigir sessão de Administrador. Sessão ausente, inválida ou expirada SHALL levar ao login.

#### Scenario: Visitante abre página protegida
- **WHEN** um visitante sem sessão abre `/conta` ou `/admin`
- **THEN** é levado a `/entrar` e, após o login, volta à página pedida

#### Scenario: Cliente abre a área administrativa
- **WHEN** um Cliente autenticado abre `/admin`
- **THEN** vê “Acesso restrito” e nenhum dado administrativo é carregado

#### Scenario: Sessão expirada
- **WHEN** o token guardado não é mais aceito pelo backend
- **THEN** a sessão é removida e o usuário é tratado como visitante

### Requirement: Minha conta
A página `/conta` SHALL exibir nome, e-mail e perfil do próprio usuário. Ela MUST NOT exibir senha nem hash.

#### Scenario: Cliente abre Minha conta
- **WHEN** um usuário autenticado abre `/conta`
- **THEN** vê o próprio nome, e-mail e perfil, e a opção “Sair”

### Requirement: Autorização administrativa no backend
Endpoints administrativos SHALL verificar no backend que o token pertence a um Administrador, respondendo 401 sem token e 403 para Cliente. A lista de usuários SHALL conter somente identificador, nome, e-mail, perfil e data de cadastro.

#### Scenario: Administrador lista usuários
- **WHEN** um Administrador abre `/admin`
- **THEN** vê a lista de usuários sem CPF, telefone, data de nascimento, endereço ou senha

#### Scenario: Cliente chama o endpoint administrativo
- **WHEN** o endpoint `GET /admin/users` é chamado com token de Cliente
- **THEN** responde 403 e nenhum dado é devolvido

### Requirement: Menu da conta
O painel “Minha conta” SHALL mostrar “Entrar / Cadastrar” ao visitante; ao usuário autenticado, “Minha conta” e “Sair”; ao Administrador, também “Painel administrativo”. Itens ainda não implementados SHALL continuar como “Em breve”.

#### Scenario: Administrador abre o menu
- **WHEN** um Administrador autenticado abre o menu
- **THEN** vê “Minha conta”, “Painel administrativo” e “Sair”

### Requirement: Dados pessoais fora dos logs
Cadastro, login e consulta da própria conta MUST NOT gravar senha, hash, CPF, telefone, data de nascimento ou endereço no registro de eventos.

#### Scenario: Login registrado
- **WHEN** um usuário faz login
- **THEN** o evento é registrado sem dados pessoais no campo `metadata`
