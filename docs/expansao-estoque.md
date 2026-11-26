# Revaulte — Expansão do estoque demonstrativo (24/11/2026)

Seis veículos **demonstrativos** acrescentados ao catálogo para a entrega de 27/11/2026, sem alterar os seis originais, o anúncio 7 (Rascunho), contas, anunciantes ou favoritos. Nenhum código nem esquema mudou por causa dos dados: eles vivem só na tabela `vehicle` do Xano. A única mudança de código ligada à expansão é a regra de destaques da Home (Change `destaques-editoriais`).

## Veículos cadastrados

Inseridos pelo usuário, por importação de CSV no painel do Xano, em 24/11/2026. Ids atribuídos pelo Xano e confirmados por leitura: 8 a 13. Todos com `status = available`, `condition = used`, sem anunciante (a ficha mostra “Contato não disponível”). `created_at` é a data real da importação.

| Id | Veículo | Ano | Categorias onde aparece | Motorização (fato do modelo) | km e preço |
| --- | --- | --- | --- | --- | --- |
| 8 | Ford Mustang Mach 1 | 1970 | Estoque, Usados | V8 351 pol³ (5,8 L) | 64.000 km, R$ 420.000 (demonstrativos) |
| 9 | Puma GTB S2 | 1980 | Estoque, Usados | Chevrolet 4.1, 6 cilindros em linha | 47.000 km, R$ 285.000 |
| 10 | Dodge Charger R/T | 1975 | Estoque, Usados | V8 318 pol³ (5,2 L) | 71.000 km, R$ 320.000 |
| 11 | Chevrolet Opala Comodoro | 1978 | Estoque, Usados, Modificados | 4.1, 6 cilindros em linha, com turbo (preparação demonstrativa) | 98.000 km, R$ 139.900 |
| 12 | Volkswagen Brasília LS | 1977 | Estoque, Usados, Modificados | AP 1.8 a água no lugar do motor a ar (troca demonstrativa) | 61.000 km, R$ 49.900 |
| 13 | Volkswagen Passat GTS Pointer | 1987 | Estoque, Usados, Modificados | AP 1.8 com turbo e intercooler (preparação demonstrativa) | 112.000 km, R$ 59.900 |

“Clássicos” não é uma categoria do site: o catálogo é derivado de `condition` (Usados), `is_modified` (Modificados) e `status`.

## Modificações: decisão final (24/11/2026)

**Nenhum veículo tem modificações detalhadas cadastradas.** A tabela `vehicle_modification` continua **vazia** (verificado por leitura em 24/11/2026). Os veículos modificados (2, 3, 4, 5, 11, 12 e 13) seguem identificados como Modificados por `is_modified = true`, com os demais dados gerais (marca, modelo, versão, ano, preço e imagem) preservados. As nove modificações demonstrativas que haviam sido preparadas (ids 11, 12 e 13) **não foram importadas** e o CSV correspondente não será usado.

Para os veículos 2 a 5, o único dado registrado sobre preparação é a marcação de modificado e o nome da versão (por exemplo “GTI Turbo”); nada além disso está comprovado, e nenhuma especificação foi inventada.

Consequência na ficha: a página dos veículos modificados mostra a seção “Modificações e preparação” com a mensagem “Veículo modificado/preparado. Os detalhes das modificações não foram informados.” Ocultar essa seção seria uma melhoria possível, mas **não foi implementada**: a spec `detalhes-veiculo` (cenário “Veículo modificado sem detalhes”) exige a mensagem e o teste `test_detalhes.py` a confere; ocultar exigiria alterar a spec e o teste.

**Sem teste real:** os cenários de modificações agrupadas por área, com registros reais, continuam sem verificação no navegador (não há registros em `vehicle_modification`). Em 26/11/2026 esse cenário foi retirado formalmente do escopo de verificação de `detalhes-veiculo` (tarefa 3.1), registrado como não testado.

## O que é demonstrativo

Quilometragem, preço e a preparação descrita na motorização dos veículos 11 a 13 são ilustrativos. Não há histórico, proprietário, documentação, anunciante nem contato inventados. A descrição de cada veículo começa com “Anúncio demonstrativo da Revaulte (projeto acadêmico)…” e traz o crédito da imagem.

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

As seis imagens foram baixadas e vistas: correspondem aos modelos. Ressalvas: algumas fotos mostram placas, pessoas ao fundo ou adesivos de evento; as dos veículos preparados mostram carros de série (imagem ilustrativa). Se uma URL deixar de responder, o site troca a capa pela imagem provisória sozinho. A imagem do veículo 5 não foi alterada.

## Ordem na Home

Os veículos novos têm o `created_at` **real** da importação (sem datas artificiais). Para os originais 4, 5 e 6 continuarem em destaque, a Home usa destaques editoriais (Change `destaques-editoriais`): `IDS_DESTAQUES = (4, 5, 6)` em `frontend/revaulte/state.py` têm prioridade quando estão Disponíveis, e as vagas restantes são completadas com os Disponíveis mais recentes. A ordem de exibição é 6, 5 e 4. O Estoque não mudou: continua do mais novo para o mais antigo, então os novos aparecem primeiro nele. Verificado por simulação com o catálogo público real (12 veículos): destaques 6, 5 e 4.

## Como foi feita a inserção

1. **Backup** com `xano workspace pull --records` antes de qualquer envio (`~/xano-backups/2026-11-24-antes-expansao-estoque`).
2. **Tentativa pela CLI (fase 1):** `xano workspace push --records` com registros **sem `id`** terminou com “Pushed 1 documents”, mas **não inseriu nenhum veículo**. O resumo `UPSERT vehicle (6 records)` da CLI é calculado localmente e o “documents” conta documentos, não registros; o Xano não confirma a importação de registros sem id. O banco permaneceu idêntico ao backup (diagnóstico por leitura), sem duplicação. Não repetir esse envio.
3. **Importação por CSV no painel** (Database → `vehicle` → Importar), sem mapear `id`, em duas etapas (1 veículo e depois 5), cada uma verificada por leitura (`csv_etapa1_verificar.py` e `fase1_verificar.py`).
4. **Verificação por leitura (24/11/2026):** 13 registros em `vehicle` (ids 1 a 7 inalterados e os 6 novos íntegros, todos `available`; o 7 segue `draft`), `GET /vehicles` com 12 ids (1 a 6 e 8 a 13), `/vehicles/7` com 404, `vehicle_modification` vazia.

Os scripts de apoio ficam fora do repositório, em `~/xano-backups/2026-11-24-antes-expansao-estoque/`.

**Reversão:** remover os veículos 8 a 13 pelo painel (ou restaurar a partir do backup).

## Verificação no navegador (26/11/2026)

Verificação automatizada em Edge sem janela, como visitante, em `localhost:3001` (roteiro e capturas temporários, não versionados).

- Home com os destaques 6, 5 e 4; `/estoque` e `/usados` com 12 veículos e `/modificados` com 7, sem imagens quebradas.
- Fichas de `/veiculo/8` a `/veiculo/13` abertas a 1280 px, sem erros; a mensagem de detalhes não informados foi conferida nos veículos 2 e 11.
- Sem rolagem horizontal a 375 e 560 px na Home, no Estoque, em Usados, em Modificados e nas fichas 1, 7 e 11; as demais fichas **não foram conferidas** em tela estreita.
- Console sem erros e nenhuma requisição do navegador ao Xano.
