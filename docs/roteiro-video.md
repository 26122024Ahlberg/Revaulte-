# Revaulte — Roteiro do vídeo (5 minutos)

Duração total: 5:00. Gravar a tela do navegador em 1280 px, com o site rodando localmente (`reflex run`). Use somente as contas fictícias do roteiro de testes (`docs/testes-contas-acesso.md`), criadas e apagadas com autorização da equipe.

## Antes de gravar

- [ ] `reflex run` em `frontend/` sem erros; site em `http://localhost:3000/`.
- [ ] Janela anônima/InPrivate (sem sessão anterior).
- [ ] Contas fictícias prontas: Cliente C (`cliente.teste@example.com`) e Administrador A (`admin.teste@example.com`, `role = admin` no painel do Xano).
- [ ] Nenhuma aba com o painel do Xano, terminal com token ou arquivo com senha visível na gravação.
- [ ] Senhas digitadas fora do enquadramento ou com o campo de senha oculto (o site já mostra `••••`).
- [ ] Evitar muitas ações seguidas: o Xano aceita 10 requisições a cada 20 s.

## Roteiro

| Tempo | Tela | O que mostrar | Fala sugerida |
| --- | --- | --- | --- |
| 0:00–0:30 | Home `/` | Carrossel, destaques, menu | “Esta é a Revaulte, um marketplace de veículos clássicos, esportivos e modificados, desenvolvido pelo grupo GhostPay com Reflex no frontend e Xano no backend.” |
| 0:30–1:15 | `/estoque` → `/modificados` | Pesquisa por texto, filtro de condição, cartões com selos | “O visitante navega pelo catálogo sem conta: pesquisa, filtra por condição e modificação e vê os selos de vendido e modificado.” |
| 1:15–2:00 | `/veiculo/<id>` de um modificado | Ficha, configuração original × modificações, anunciante, simulador | “Na página do veículo, a Revaulte separa a configuração original das modificações. O simulador é informativo, com taxa ilustrativa, e não é proposta de crédito.” |
| 2:00–2:15 | Menu ☰ | Entrar, Cadastrar e os três “Em breve” | “Para o visitante, o menu oferece entrar ou criar conta; funções futuras aparecem como ‘Em breve’.” |
| 2:15–2:50 | `/cadastro` | Um erro de validação (senha `abcdefgh`) e depois o cadastro válido da conta C | “O cadastro valida CPF, telefone, data e senha forte, com mensagens em português, antes de enviar ao backend.” |
| 2:50–3:15 | `/conta` | Nome, e-mail, perfil Cliente; menu com Minha conta e Sair | “Depois do cadastro, a pessoa já está autenticada. Minha conta mostra só nome, e-mail e perfil — nenhum dado sensível.” |
| 3:15–3:35 | `/admin` com a conta C | “Acesso restrito” | “Um Cliente não acessa a área administrativa. A permissão é conferida no backend, não só escondida na tela.” |
| 3:35–3:50 | Sair → `/conta` | Volta à home; `/conta` leva ao login com `?proximo=/conta` | “Ao sair, a sessão é apagada. Páginas protegidas levam ao login e voltam à página pedida.” |
| 3:50–4:30 | `/entrar?proximo=/admin` com a conta A | Lista de usuários (ID, data, nome, e-mail, perfil); menu com Painel administrativo | “O Administrador vê a lista de usuários, sem CPF, telefone, endereço ou senha. O primeiro Administrador é definido pela equipe no painel do Xano.” |
| 4:30–4:50 | Celular (375 px) | Menu ☰ com Navegação e Minha conta; lista do admin em blocos | “O site é responsivo: em telas pequenas, o menu reúne a navegação e a lista vira blocos, sem rolagem lateral.” |
| 4:50–5:00 | Home | Encerramento | “Tudo foi especificado com OpenSpec e testado com testes automáticos. Obrigado!” |

## Depois de gravar

- [ ] Assistir ao vídeo e conferir que nenhuma senha, token, CPF ou e-mail real aparece.
- [ ] Excluir as contas fictícias no painel do Xano (etapa 9 do roteiro de testes).
