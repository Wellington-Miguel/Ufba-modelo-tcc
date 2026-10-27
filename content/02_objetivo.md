# Objetivos

## Objetivo Geral

Desenvolver, documentar e avaliar um protótipo de Assistente de Observabilidade Sociotécnica focado na etapa de *Data Parsing* da plataforma CorText Manager, integrando validação algorítmica preventiva de matrizes de dados (*Data Profiling*) e um modelo de Recuperação Aumentada por Geração (RAG) para traduzir falhas técnicas e registros de erro (*logs*) em diagnósticos metodologicamente compreensíveis.

## Objetivos Específicos

Para alcançar o propósito geral estabelecido e responder à questão de pesquisa formulada, foram definidos cinco objetivos específicos sequenciais e verificáveis:

a) caracterizar o problema de pesquisa mapeando quantitativa e qualitativamente as falhas mais recorrentes de importação de corpora, utilizando a extração automatizada das discussões do fórum oficial de suporte, a análise estática do script legado de *Data Parsing* e interações com a comunidade de usuários;
b) mapear, extrair (*web scraping*) e vetorizar a base de conhecimento técnica presente no fórum histórico de dúvidas e na documentação oficial da plataforma (*CorTexT Manager Comprehensive Documentation and User Guide*), armazenando-a em um Banco de Dados Vetorial operando localmente;
c) construir um módulo determinístico de *Data Profiling* em linguagem Python, capaz de auditar estruturalmente arquivos brutos (nos formatos CSV, RIS, JSON e texto plano) e bancos de dados SQLite para detectar preventivamente anomalias de codificação no padrão *8-bit Unicode Transformation Format* (UTF-8), escassez de delimitadores e inconsistências estruturais;
d) implementar e parametrizar um modelo de linguagem local (orquestrado via Ollama) integrado à arquitetura RAG para interpretar registros de erro (*logs* e *tracebacks*) e gerar diagnósticos acionáveis em linguagem natural;
e) homologar e avaliar o protótipo por meio de técnicas de Engenharia do Caos, simulando o processamento de matrizes de dados corrompidas e falhas historicamente documentadas para mensurar a precisão dos diagnósticos gerados pelo sistema proposto.

## Justificativa

No âmbito acadêmico e profissional, a justificativa para a realização desta pesquisa apoia-se nas severas barreiras documentadas no fórum oficial de suporte da plataforma CorText Manager [@CorText2026]. Apesar do sucesso de adoção da ferramenta e de sua capacidade de processar volumetrias massivas, a etapa inicial de preparação, estruturação e importação de dados (*Data Parsing*), essencial para a criação do banco de dados relacional SQLite, apresenta alta incidência de falhas acompanhadas por registros de erro opacos ou mensagens genéricas de sistema. Há relatos críticos e recorrentes de usuários que não conseguem processar arquivos textuais em codificação UTF-8, que esbarram em falhas sintáticas ao submeter bases bibliométricas no formato RIS provenientes da Scopus, ou que sofrem perdas silenciosas de dados, tais como tabelas de endereços ou redes inteiras que resultam vazias após a conclusão do processamento [@CorText2026].

Para dimensionar empiricamente a magnitude e a recorrência desse gargalo no ecossistema da plataforma, realizou-se uma auditoria quantitativa censitária no fórum oficial de perguntas e respostas da comunidade (`https://docs.cortext.net/forum/`) por meio do extrator determinístico customizado `extract_forum.py`, utilizando recursos de coleta assíncrona [@Crawl4AI2026]. A varredura auditou integralmente as 34 páginas do acervo histórico de discussões públicas, consolidando um corpus de 298 tópicos únicos e mapeando variáveis de autoria, tempo de resolução, métricas textuais e formatos de entrada.

A análise da distribuição temática oficial demonstra que a categoria *Data processing* reúne diretamente 84 tópicos, o que corresponde a 28,2% do acervo. Contudo, a inspeção epistêmica e semântica das discussões revelou que a categorização oficial subdimensiona a crise de preparação de dados: outros 114 tópicos (38,3%), protocolados formalmente pelos usuários em categorias de etapas posteriores (como *Network mapping* ou *Topic modeling*), decorrem exclusivamente de inconsistências ocultas originadas na fase de *Data Parsing*. Dessa forma, a fricção na importação e estruturação de dados atinge, na realidade, 198 tópicos, englobando 66,4% de toda a demanda histórica de suporte do ecossistema, conforme sintetizado na Tabela 1 e ilustrado visualmente na Figura 1.

| Escopo de Análise / Categoria | Volume de Tópicos Únicos | Proporção Relativa (%) | Foco Principal de Suporte e Fricção Identificada |
| :--- | :---: | :---: | :--- |
| *Parsing* Direto (*Data processing*) | 84 tópicos | 28,2% | Importação direta de corpora, falhas de *parsing*, erros em arquivos CSV, ZIP, WOS, Scopus e RIS, codificação e delimitadores. |
| *Parsing* Indireto / Derivado | 114 tópicos | 38,3% | Falhas propagadas para outras etapas (como redes vazias *network empty* e indexação corrompida) decorrentes de erros de *parsing* não detectados na entrada. |
| Não Relacionado a *Parsing* | 100 tópicos | 33,6% | Dúvidas puramente metodológicas e parametrização avançada de algoritmos analíticos. |
| Total do Acervo Auditado | 298 tópicos | 100,0% | Panorama completo do acervo histórico auditado do fórum oficial. |

*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

![Decomposição analítica do acervo do fórum CorText Manager demonstrando o escopo expandido de Data Parsing (66,4% de fricção total)](images/figura1_decomposicao.png)
*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

Os dados empíricos apresentados na Tabela 1 e na Figura 1 comprovam que dois terços de toda a demanda de suporte da comunidade estão vinculados à preparação e ingestão de dados. Adicionalmente, a auditoria revelou que 81,0% dos chamados na categoria *Data processing* (68 de 84 tópicos) exigiram intervenção manual direta da equipe técnica mantenedora, fenômeno caracterizado nesta pesquisa como *Staff as Human Parser*. Essa dependência evidencia um expressivo gargalo operacional para contornar falhas de formatação em um ecossistema que acumula mais de 791 mil visualizações orgânicas [@CorText2026].

Além do volume global de chamados, a análise longitudinal ao longo de doze anos de operação (2014 a 2026), apresentada na Figura 2, demonstra que a incidência de problemas de preparação de dados não decorre de defeitos efêmeros ou versões isoladas do software, mas representa uma barreira estrutural persistente na utilização da ferramenta.

![Persistência longitudinal da fricção em Data Parsing no fórum oficial do CorText Manager (2014 a 2026)](images/figura6_persistencia.png)
*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

Paralelamente, a análise do engajamento público reforça a criticidade do problema. Ao isolar os dez tópicos mais visualizados de toda a história do fórum CorText Manager, constata-se que 90% das discussões com maior acesso orgânico da comunidade tratam direta ou indiretamente de falhas em *Data Parsing* e interpretação de registros de erro, restando apenas um chamado referente à indisponibilidade temporária do painel web. A Tabela 2 apresenta o mapeamento consolidado dos dez tópicos de maior engajamento no fórum oficial.

| ID | Título da Discussão no Fórum Oficial | Visualizações | Categoria Oficial | Relação com *Parsing* | Causa Raiz / Síntese do Atrito Reportado |
| :---: | :--- | :---: | :--- | :--- | :--- |
| #292 | *Cortext seems to be down. Dashboard is not loading.* | 4.208 | *Something else* | Não Relacionado | Instabilidade temporária no servidor e falha de carregamento da interface do painel. |
| #280 | *Web of Science (WOS) Corpus \textbar{} Expert query \textbar{} SQL* | 3.033 | *Data processing* | *Parsing* Direto | Consultas complexas e erros de sintaxe SQL e filtros na importação de corpora WOS. |
| #269 | *troubles parsing json files from ISTEX* | 2.984 | *Data processing* | *Parsing* Direto | Incompatibilidade na estrutura JSON aninhada exportada da plataforma ISTEX. |
| #267 | *How to avoid error message when parsing a zip folder...* | 2.958 | *Data processing* | *Parsing* Direto | Estruturas de arquivos ZIP aninhadas ou com subpastas internas incompatíveis. |
| #247 | *Problem with log files* | 2.625 | *Something else* | *Parsing* Indireto | Dificuldade de interpretação de erros em scripts e registros (*logs*) de processamento. |
| #208 | *Parsing a modified .RIS (Scopus) database* | 2.093 | *Data processing* | *Parsing* Direto | Alteração manual de marcadores (*tags*) e formatos em arquivos RIS exportados da Scopus. |
| #203 | *Un paquet de 500 notices WoS produit une table address vide* | 2.031 | *Data processing* | *Parsing* Direto | Falha silenciosa de extração do campo de endereços em lotes da Web of Science. |
| #202 | *Trouble parsing a PDF corpus* | 2.028 | *Data processing* | *Parsing* Direto | Erros na extração de texto e estruturação de arquivos em *Portable Document Format* (PDF). |
| #200 | *Importing ISI files into CorText* | 2.012 | *Data processing* | *Parsing* Direto | Incompatibilidade na exportação de registros em texto plano (*Institute for Scientific Information* ou ISI). |
| #144 | *Impossible de parser un corpus istex* | 1.512 | *Data processing* | *Parsing* Direto | Erros de codificação (*encoding*) e sintaxe em arquivos brutos provenientes do ISTEX. |

*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

Sob a ótica da contribuição e da relevância social, o tema insere-se diretamente no empoderamento metodológico da comunidade de pesquisadores das ciências sociais e humanidades. Sob o enquadramento teórico dos Estudos de Ciência e Tecnologia (STS), notadamente a partir de @Latour1987 e de @Bowker1999, uma falha técnica oculta na etapa de ingestão não representa um mero erro sintático de código, mas sim o apagamento silencioso de atores e inscrições concretas da rede da pesquisa [@Abdo2021]. Ao integrar métodos determinísticos de Qualidade de Dados [@Wang1996] e um modelo RAG [@Lewis2020] para atuar como tradutor técnico e pedagógico, a ferramenta proposta promove a abertura seletiva da "caixa preta" da infraestrutura de entrada, devolvendo a agência metodológica ao pesquisador sem interferir na interpretação sociológica dos dados.

## Delimitação do Escopo

O desenvolvimento metodológico deste estudo assume como verdadeiras três premissas fundamentais que guiam a viabilidade técnica da investigação. A primeira premissa estabelece que a etapa de importação de dados constitui, de fato, uma barreira frequente para usuários da plataforma, justificando a adoção de sistemas automatizados de apoio diagnóstico. A segunda premissa postula que a base de conhecimento pública do CorText Manager, composta pela documentação oficial e pelas resoluções históricas no fórum, possui densidade informacional relevante para ancorar a recuperação vetorial de um modelo RAG com eficácia. A terceira premissa assume que os rastros de exceção (*tracebacks*) produzidos no ambiente local de testes a partir do script de *parsing* são estruturalmente análogos aos gerados no servidor de produção da plataforma.

A partir dessas premissas, a investigação estrutura-se para testar empiricamente duas hipóteses de pesquisa. A primeira hipótese, denominada Hipótese de *Profiling* (H1), sustenta que a aplicação de rotinas prévias de verificação estrutural e de formatação (*Data Profiling*) reduz significativamente a submissão de arquivos propensos a falhas silenciosas de truncamento ou inferência errônea de delimitadores pelo analisador nativo, interceptando pelo menos 80% das anomalias em amostras de teste historicamente incompatíveis. A segunda hipótese, denominada Hipótese de Diagnóstico via IA (H2), postula que um modelo de linguagem atuando sob a arquitetura RAG, ancorado exclusivamente no fórum e no manual oficial do CorText Manager, produz diagnósticos metodologicamente mais precisos, acionáveis e livres de alucinações frente a registros de erro de sistema do que um modelo de linguagem genérico (*vanilla*) desprovido de contexto específico.

Compreendendo a amplitude arquitetural da plataforma CorText Manager e visando assegurar a exequibilidade e o rigor científico do projeto, estabelecem-se três limites estritos de escopo para o protótipo:

a) restrição exclusiva ao módulo de entrada (*Data Parsing*): o assistente atuará unicamente na etapa de preparação, ingestão e padronização metodológica dos arquivos brutos e na auditoria imediata do banco SQLite resultante, não oferecendo suporte ou diagnósticos para a parametrização de módulos analíticos posteriores, tais como *Network Mapping*, *Topic Modeling*, *Distant Reading* ou *Demography*;
b) neutralidade epistemológica na camada de engenharia de dados: a ferramenta operará estritamente em nível de infraestrutura de dados (*Data Engineering*), não realizando análises sociológicas, sumarizações de artigos ou interpretações qualitativas sobre o conteúdo semântico dos textos submetidos pelos pesquisadores;
c) desacoplamento arquitetural como microsserviço auxiliar: o protótipo não visa reescrever, refatorar ou substituir o código-fonte nativo de *parsing* nos servidores de produção do CorText Manager, mas sim operar como um microsserviço independente e complementar de curadoria prévia e auditoria de registros de erro.