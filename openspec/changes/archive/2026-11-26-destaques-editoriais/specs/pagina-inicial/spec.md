# Spec Delta

## MODIFIED Requirements

### Requirement: Veículos em destaque
A página inicial SHALL exibir, na seção “Veículos em destaque”, até três veículos no estado Disponível, obtidos do backend no carregamento da página e apresentados com as mesmas informações e selos dos cartões do catálogo. Os veículos de destaque editorial (identificadores 4, 5 e 6) SHALL ter prioridade, desde que estejam Disponíveis no catálogo público; as vagas restantes SHALL ser completadas com os veículos Disponíveis cadastrados mais recentemente. Veículos Vendidos MUST NOT aparecer nos destaques. A seção SHALL oferecer um link para o estoque completo.

#### Scenario: Destaques editoriais disponíveis
- **WHEN** os veículos 4, 5 e 6 estão Disponíveis e existem outros veículos Disponíveis cadastrados depois deles
- **THEN** a seção exibe exatamente os veículos 6, 5 e 4, do mais recente para o mais antigo, e nenhum dos mais novos

#### Scenario: Destaque editorial indisponível
- **WHEN** o veículo 5 está Vendido
- **THEN** a seção exibe os veículos 6 e 4 e completa a terceira vaga com o Disponível mais recente que não seja um destaque editorial

#### Scenario: Destaques editoriais ausentes
- **WHEN** nenhum dos veículos 4, 5 e 6 está no catálogo público
- **THEN** a seção exibe os três Disponíveis cadastrados mais recentemente

#### Scenario: Mais de três disponíveis
- **WHEN** existem cinco veículos Disponíveis no backend e nenhum deles é um destaque editorial
- **THEN** a seção exibe somente os três cadastrados mais recentemente, do mais recente para o mais antigo

#### Scenario: Vendido não é destaque
- **WHEN** o veículo cadastrado mais recentemente está no estado Vendido
- **THEN** ele não aparece nos destaques e a seção exibe os Disponíveis que seguem a regra de prioridade

#### Scenario: Menos de três disponíveis
- **WHEN** existem apenas dois veículos Disponíveis
- **THEN** a seção exibe esses dois veículos

#### Scenario: Nenhum disponível
- **WHEN** não há veículos Disponíveis
- **THEN** a seção exibe uma mensagem informando que não há destaques no momento e mantém o link para o estoque

#### Scenario: Falha ao obter os destaques
- **WHEN** a solicitação ao backend falha
- **THEN** a seção exibe uma mensagem de erro com a opção de tentar novamente, não exibe veículos fictícios, e o restante da página continua utilizável
