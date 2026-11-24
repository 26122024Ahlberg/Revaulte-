# Revaulte — Expansão do estoque demonstrativo (24/11/2026)

Seis veículos **demonstrativos** acrescentados ao catálogo para a entrega de 27/11/2026, sem alterar os seis originais, o anúncio 7 (Rascunho), contas, anunciantes ou favoritos. Nenhum código nem esquema muda: os dados vivem só na tabela `vehicle` (e em `vehicle_modification`) do Xano.

## Veículos

Todos com `status = available`, `condition = used`, sem anunciante (`seller_id = 0`, como os originais 2 a 6; a ficha mostra “Contato não disponível”). Ids 8 a 13.

| Id | Veículo | Ano | Categorias onde aparece | Motorização (fato do modelo) | km e preço |
| --- | --- | --- | --- | --- | --- |
| 8 | Ford Mustang Mach 1 | 1970 | Estoque, Usados | V8 351 pol³ (5,8 L) | 64.000 km, R$ 420.000 (demonstrativos) |
| 9 | Puma GTB S2 | 1980 | Estoque, Usados | Chevrolet 4.1, 6 cilindros em linha | 47.000 km, R$ 285.000 |
| 10 | Dodge Charger R/T | 1975 | Estoque, Usados | V8 318 pol³ (5,2 L) | 71.000 km, R$ 320.000 |
| 11 | Chevrolet Opala Comodoro | 1978 | Estoque, Usados, Modificados | 4.1, 6 cilindros em linha, com turbo (preparação demonstrativa) | 98.000 km, R$ 139.900 |
| 12 | Volkswagen Brasília LS | 1977 | Estoque, Usados, Modificados | AP 1.8 a água no lugar do motor a ar (troca demonstrativa) | 61.000 km, R$ 49.900 |
| 13 | Volkswagen Passat GTS Pointer | 1987 | Estoque, Usados, Modificados | AP 1.8 com turbo e intercooler (preparação demonstrativa) | 112.000 km, R$ 59.900 |

Os ids 11 a 13 têm 3 modificações cada em `vehicle_modification` (9 no total), todas marcadas como demonstrativas. “Clássicos” não é uma categoria do site: o catálogo é derivado de `condition` (Usados), `is_modified` (Modificados) e `status`.

## O que é demonstrativo

Quilometragem, preço e preparações são ilustrativos. Não há histórico, proprietário, documentação, anunciante nem contato inventados. A descrição de cada veículo começa com “Anúncio demonstrativo da Revaulte (projeto acadêmico)…” e traz o crédito da imagem.

## Imagens

Wikimedia Commons, cada URL verificada em 24/11/2026 com HTTP 200 e `image/jpeg`; créditos e licenças constam na descrição de cada veículo.

| Id | Arquivo | Licença |
| --- | --- | --- |
| 8 | 1970 Ford Mustang Mach 1 (24388702362).jpg | CC BY 2.0 |
| 9 | 1980 Puma GTB S2 in black.jpg | Domínio público |
| 10 | 1975 Dodge Charger RT.jpg | CC BY 3.0 |
| 11 | Chevrolet Opala Comodoro 1978.jpg | CC BY-SA 4.0 |
| 12 | Brasilia Dacon.jpg | Domínio público |
| 13 | Passat GTS Pointer 1987.jpg | CC BY 4.0 |

As fotos dos veículos modificados mostram carros de série (imagem ilustrativa). Se uma URL deixar de responder, o site troca a capa pela imagem provisória sozinho. A imagem do veículo 5 não foi alterada.

## Ordem na Home

Os veículos novos entram com o `created_at` **real** do momento da inserção (sem datas artificiais). Para os originais 4, 5 e 6 continuarem em destaque, a Home passou a usar destaques editoriais (Change `destaques-editoriais`): `IDS_DESTAQUES = (4, 5, 6)` em `frontend/revaulte/state.py` têm prioridade quando estão Disponíveis, e as vagas restantes são completadas com os Disponíveis mais recentes. A ordem de exibição continua 6, 5 e 4. O Estoque não mudou: continua do mais novo para o mais antigo, então os novos aparecem primeiro nele.

## Publicação controlada, em duas fases, com ids automáticos

Os registros entram **sem `id`** (o Xano atribui pela própria sequência, sem risco de colisão com a criação de anúncios) e sem `created_at` artificial. Scripts de apoio ficam fora do repositório, em `~/xano-backups/2026-11-24-antes-expansao-estoque/`; eles só leem o Xano e fazem prévias protegidas, e o envio real é sempre feito pelo usuário, com confirmação interativa, sem `--sync`, `--delete`, `--force` nem `--truncate`.

1. **Backup** com `xano workspace pull --records` (feito em 24/11/2026).
2. **Fase 1** (`fase1_preparar.py`): confirma que o banco está idêntico ao backup (ids 1 a 7), que `vehicle_modification` está vazia e que nenhum dos seis veículos já existe; gera `push-fase1/` com só os 6 veículos e mostra a prévia `UPSERT vehicle (6 records)`. O envio roda dentro de uma transação (padrão da CLI): ou entram os 6 ou nenhum. Depois, `fase1_verificar.py` confere campos, imagens, `created_at` real e ids 1 a 7 inalterados e só então libera a fase 2 (grava `fase1_ok.json`).
3. **Fase 2** (`fase2_preparar.py`): usa os ids realmente atribuídos, recusa-se a rodar sem a fase 1 íntegra ou se já houver modificações, e gera `push-fase2/` com as 9 modificações (`UPSERT vehicle_modification (9 records)`).
4. **Verificação final** (`final_verificar.py`): `GET /vehicles` com os 12 ids públicos (1 a 6 e os 6 novos), `/vehicles/7` com 404, ids 1 a 7 inalterados, 3 modificações em cada veículo preparado, imagens com HTTP 200 e destaques da Home iguais a 6, 5 e 4.

**Duplicação:** sem `id`, repetir a fase 1 duplicaria os veículos. Os scripts recusam qualquer nova tentativa se já existirem veículos novos ou `fase1_ok.json`; antes de repetir qualquer envio, leia a tabela.

**Reversão:** remover os 6 veículos novos e suas 9 modificações (ou restaurar a partir do backup).

## Conferência das imagens (24/11/2026)

As seis imagens foram baixadas e vistas: correspondem aos modelos (Puma GTB S2 preto, Brasília LS bege, Charger R/T amarelo, Mustang Mach 1 laranja, Passat GTS Pointer verde e Opala coupé azul). Licenças: domínio público (Puma e Brasília), CC BY 2.0 e 3.0 e 4.0 (Mustang, Charger e Passat) e CC BY-SA 4.0 (Opala), todas livres para uso e exibição com crédito, que consta na descrição do veículo. Ressalvas: algumas fotos mostram placas, pessoas ao fundo ou adesivos de evento; são fotos públicas do Commons, mas vale trocar alguma se isso incomodar na demonstração.
