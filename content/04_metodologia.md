# Metodologia

## Classificação da Pesquisa

A presente investigação classifica-se, quanto à sua natureza, como uma pesquisa aplicada e tecnológica em Sistemas de Informação e Ciência da Computação, uma vez que objetiva gerar conhecimento voltado à solução prática de um gargalo operacional real vivenciado pela comunidade científica usuária da plataforma CorText Manager. Quanto à sua abordagem, o estudo caracteriza-se como quali-quantitativo (ou de métodos mistos). A dimensão quantitativa manifesta-se na auditoria estatística censitária do acervo histórico do fórum de suporte, na mensuração não paramétrica do esforço cognitivo dos usuários [@Kruskal1952; @Mann1947] e na aferição objetiva das taxas de detecção preventiva do módulo de *Data Profiling*. Por sua vez, a dimensão qualitativa expressa-se na análise epistemológica das heurísticas do código-fonte sob a lente dos Estudos de Ciência e Tecnologia [@Latour1987; @Bowker1999] e na avaliação da clareza pedagógica dos diagnósticos gerados pelo modelo de Recuperação Aumentada por Geração (RAG).

No que tange aos seus objetivos metodológicos, a pesquisa combina um caráter exploratório e descritivo, empregado no mapeamento inédito das 22 anomalias arquiteturais do analisador sintático (*parser*) e na catalogação empírica dos chamados da comunidade, a um delineamento experimental. O caráter experimental concretiza-se no desenvolvimento iterativo de um protótipo de software de código aberto e na sua validação controlada mediante técnicas de Engenharia do Caos e testes comparativos (Teste A/B), assegurando reprodutibilidade científica e independência operacional em relação aos servidores de produção da plataforma francesa.

## Etapas do Projeto

Para garantir o cumprimento integral dos objetivos específicos estabelecidos, o percurso metodológico foi estruturado em seis etapas sequenciais e interdependentes, que articulam as quatro fases macroestruturais de construção e avaliação do artefato tecnológico.

> **[ESPAÇO RESERVADO OPCIONAL — DIAGRAMA DO FLUXO METODOLÓGICO]:**
> *Caso deseje inserir uma ilustração síntese das seis etapas metodológicas, salvar a imagem como `images/fluxo_metodologico.png` e descomentar as duas linhas abaixo:*
> `![Fluxograma das seis etapas metodológicas da pesquisa](images/fluxo_metodologico.png)`
> `*Fonte: Elaborado pelo autor (2026).*`

### Etapa 1: Revisão Bibliográfica e Análise Arquitetural do Código Legado

A etapa inicial compreendeu a consolidação do referencial teórico interdisciplinar, articulando os Estudos de Ciência e Tecnologia (STS) [@Latour1987; @Bowker1999; @Edwards2010; @Abdo2021] às dimensões formais de Qualidade de Dados [@Wang1996; @Naumann2014] e Observabilidade de Sistemas [@Majors2022]. Paralelamente, realizou-se a inspeção estática e o mapeamento profundo do código-fonte em linguagem Python responsável pela rotina de *Data Parsing* do CorText Manager. Essa dissecação algorítmica visou rastrear o fluxo de ingestão dos documentos desde a leitura em disco até a consolidação das tabelas no banco relacional SQLite, permitindo identificar as decisões de programação defensiva, os blocos de silenciamento de exceções (`try/except`), os limites estáticos de memória e as expressões regulares destrutivas que originam a perda silenciosa de inscrições científicas.

### Etapa 2: Engenharia de Extração e Auditoria Empírica do Fórum Oficial

Com o propósito de fundamentar empiricamente a barreira de preparação de dados e construir a memória técnica do assistente, desenvolveu-se uma infraestrutura determinística de extração completa (*web scraping*) do fórum oficial de suporte da plataforma (`https://docs.cortext.net/forum/`) [@CorText2026; @Crawl4AI2026]. A coleta e a estruturação dos dados foram operacionalizadas por meio do script customizado `extract_forum.py`, arquitetado em três fases estritamente auditáveis que garantiram a cobertura de 100% do acervo público (298 tópicos únicos distribuídos em 34 páginas), conforme detalhado na Tabela 5.

| Fase Metodológica | Mecanismo Técnico Empregado | Garantia de Integridade e Cobertura |
| :--- | :--- | :--- |
| Fase 1: Varredura Sequencial | Iteração sequencial estrita da listagem oficial: páginas `/page/1/` a `/page/34/`. | Cobertura total de 298 tópicos únicos: páginas 1 a 33 (9 tópicos cada) e página 34 (1 tópico), com zero filtros e zero duplicatas. |
| Fase 2: Extração Profunda | Requisições assíncronas concorrentes via biblioteca `aiohttp` com semáforo controlado e novas tentativas (*retries*) automáticas. | Captura de marcações semânticas JSON-LD Schema do WordPress (datas exatas em ISO 8601), dúvida na íntegra e vetor completo de respostas. |
| Fase 3: Enriquecimento | Detecção de autores oficiais do projeto (insígnias de *Staff* do CorText) e cálculo automatizado de métricas textuais. | Paridade de 100%: sincronização simultânea nos arquivos `forum_topics_full.json`, `forum_topics.csv` e `forum_corpus.md`. |

*Fonte: Elaborado pelo autor (2026).*

Durante a auditoria epistêmica e semântica dos 298 tópicos extraídos, constatou-se que a categorização nativa do fórum (que registra 84 tópicos na categoria *Data processing*, ou 28,2% do total) subdimensiona a crise de preparação de dados. Quando o usuário comete um equívoco de formatação na entrada (como um delimitador incorreto em CSV ou marcadores de autoria não padronizados), a falha frequentemente não interrompe o *parser* de imediato, mas gera um banco SQLite estruturalmente inconsistente cujo erro só eclode tardiamente em módulos analíticos subsequentes, tais como *Network mapping* ou *Topic modeling*.

Para capturar esse fenômeno com rigor metodológico, estabeleceram-se três critérios heurísticos de elegibilidade que permitiram identificar 114 tópicos adicionais (38,3% do acervo) protocolados em outras categorias, mas decorrentes exclusivamente de falhas na etapa de *Data Parsing* (denominados *Parsing* Derivado ou Indireto), totalizando 198 chamados afetados (66,4% do fórum). A Tabela 6 apresenta as regras heurísticas aplicadas nessa classificação.

| Critério Analítico de Elegibilidade | Tópicos Afetados | Evidência Heurística e Regras Aplicadas na Classificação |
| :--- | :---: | :--- |
| Critério 1: Manipulação de Formato Bruto Heterogêneo | 62 tópicos (54,4% dos derivados) | Tópicos alocados em outras categorias que contêm menção explícita a arquivos e dialetos externos (CSV, ZIP, Scopus, WOS, RIS, Factiva, PubMed, Excel), lidando com problemas de separadores ou marcadores bibliográficos. |
| Critério 2: Indexação, *Parsing* e Codificação em Outras Etapas | 50 tópicos (43,9% dos derivados) | Discussões mencionando expressamente ferramentas de estruturação preliminar (*Corpus Terms Indexer*, *Corpus List Indexer*, *upload*, *encoding* UTF-8, *subcorpus*) durante a execução de etapas de mineração de texto ou redes. |
| Critério 3: Sintomas Patognomônicos de Corpus Vazio ou Corrompido | 2 tópicos (1,8% dos derivados) | Chamados reportando o sintoma clássico de ingestão quebrada: geração de redes vazias (`network you produced is empty` ou `reseau vide`) e ausência de registros (*logs*) devido a colunas obrigatórias vazias. |

*Fonte: Elaborado pelo autor (2026).*

### Etapa 3: Construção e Vetorização da Base de Conhecimento Local

Concluída a extração e a higienização do corpus histórico do fórum (`forum_corpus.md`), esta etapa dedica-se à agregação da documentação técnica oficial da plataforma (*CorTexT Manager Comprehensive Documentation and User Guide*). O material unificado passa por rotinas de limpeza sintática, segmentação em blocos semânticos (*chunking*) que preservam o par pergunta-resposta validado pela equipe técnica (*Staff*), e conversão em representações numéricas multidimensionais (*embeddings*). Os vetores gerados são indexados e armazenados em um Banco de Dados Vetorial operando localmente, assegurando recuperação semântica de baixa latência sem dependência de serviços externos em nuvem.

### Etapa 4: Desenvolvimento do Módulo Pre-Flight Data Profiler e Early-Warning Parser

Esta etapa concentra-se na engenharia do primeiro estágio do assistente: a elaboração de rotinas determinísticas em linguagem Python, utilizando a biblioteca Pandas e expressões regulares, para inspecionar preventivamente as matrizes brutas de entrada (CSV, RIS, JSON, XML, HTML e lotes ZIP) antes da submissão ao CorText Manager. O módulo verifica a conformidade de codificação UTF-8, a simetria de delimitadores, a integridade de chaves únicas e a sobrevivência de metadados. Adicionalmente, desenvolve-se o validador pós-ingestão (*Early-Warning Parser*) para auditar a estrutura das tabelas do banco SQLite (`.db`) recém-gerado, prevenindo a submissão de matrizes de adjacência zeradas aos algoritmos de rede.

### Etapa 5: Integração do Módulo Log Explainer e Arquitetura RAG via Ollama

No segundo estágio arquitetural, realiza-se a implantação e a parametrização de um Modelo de Linguagem de Grande Escala (LLM) de pesos abertos (*open-weights*), executado localmente por meio da plataforma Ollama. Implementa-se a engenharia de comandos (*prompt engineering*) restritiva do sistema RAG, responsável por interceptar o rastro técnico da exceção (*stack trace* ou *log* de erro), acoplá-lo automaticamente ao resumo estrutural do arquivo coletado pelo *Data Profiler* no estágio preventivo e consultar os casos análogos no Banco de Dados Vetorial. Dessa forma, o modelo sintetiza narrativas de diagnóstico e instruções de correção acionáveis na interface da aplicação companheira (*companion app*).

### Etapa 6: Homologação via Engenharia do Caos, Avaliação e Documentação

A etapa final compreende a execução do protocolo experimental de validação do protótipo. Conduz-se a bateria de testes de Engenharia do Caos mediante a submissão deliberada de 22 arquivos sinteticamente corrompidos (*Corpus de Caos*) para aferir a taxa de interceptação preventiva do *Profiler* (validação da Hipótese H1), seguida pelo Teste A/B comparativo entre o assistente com RAG local e o mesmo LLM em configuração genérica (*vanilla*) frente a erros reais do fórum (validação da Hipótese H2). Concluem-se os trabalhos com a avaliação de usabilidade junto a usuários locais, a documentação exaustiva dos scripts segundo as convenções do repositório oficial e a consolidação desta monografia.

## Ferramentas e Tecnologias

A seleção do arcabouço tecnológico deste projeto foi orientada pelos princípios de software livre, reprodutibilidade científica, soberania computacional e custo financeiro zero de execução. As ferramentas adotadas dividem-se em quatro camadas funcionais:

a) linguagem de programação e manipulação de dados: utiliza-se o Python (versão 3.10 ou superior) como linguagem nuclear de desenvolvimento, garantindo compatibilidade direta com o ecossistema nativo do CorText Manager; para as rotinas determinísticas do *Pre-Flight Data Profiler*, empregam-se as bibliotecas Pandas (inspeção matricial, validação de tipos e detecção de `ParserError`), `sqlite3` (auditoria de esquemas e tabelas relacionais do arquivo `.db`), `re` (avaliação preventiva de expressões regulares), `zipfile` (varredura de caminhos e nomes acentuados em arquivos compactados) e `chardet` / `codecs` (verificação estrita de cadeias de bytes UTF-8 e Windows-1252);
b) extração assíncrona e auditoria estatística: para a construção do extrator `extract_forum.py` e coleta da base de conhecimento, utilizaram-se a biblioteca assíncrona `aiohttp` (gerenciamento de concorrência com semáforos e *retries*), o arcabouço de raspagem web amigável a modelos de linguagem Crawl4AI (v0.9.x) [@Crawl4AI2026] e extratores de marcação estruturada JSON-LD Schema; para os testes estatísticos não paramétricos de Kruskal-Wallis e Mann-Whitney sobre a dispersão textual do fórum, empregaram-se as bibliotecas `scipy.stats`, `numpy` e `matplotlib` / `seaborn` [@Kruskal1952; @Mann1947];
c) inteligência artificial local e banco de dados vetorial: a orquestração local dos modelos de linguagem fundacionais é realizada por meio da plataforma Ollama, permitindo a execução em infraestrutura local (*on-premises*) de modelos compactos de pesos abertos, tais como Llama 3 (8B), Mistral (7B) ou Phi-3 Mini (3.8B), sem envio de dados sensíveis à nuvem; o armazenamento dos *embeddings* documentais e a busca por similaridade de cosseno do módulo RAG são gerenciados localmente via banco vetorial ChromaDB (ou FAISS) integrado a pipelines de orquestração em Python;
d) interface de usuário e reprodutibilidade: a camada visual da aplicação companheira (*companion app*) e o painel público de exploração dos dados auditados do fórum foram desenvolvidos com o *framework* Streamlit, proporcionando uma interface web reativa de arrastar e soltar (*Drag and Drop*), enquanto o controle de versão e a disponibilização aberta dos conjuntos de dados e códigos-fonte são mantidos na plataforma GitHub.

## Interação com Equipe Técnica e Usuários

Embora a arquitetura de validação do protótipo tenha sido desenhada para operar com total autonomia técnica por meio do *Corpus de Caos* e dos dados históricos extraídos do fórum oficial (uma vez que o código-fonte do *Data Parsing*, o esquema SQLite e a documentação integral já se encontram disponíveis localmente), o projeto estabelece três frentes de articulação sociotécnica com a comunidade e com os mantenedores da plataforma CorText Manager:

a) incorporação da memória empírica da equipe técnica (*Staff*): ao indexar as respostas oficiais fornecidas pelos engenheiros e desenvolvedores do CorText Manager ao longo de doze anos de operação do fórum (onde o *Staff* interveio manualmente em 81,0% dos tópicos de *Data processing*), o assistente incorpora diretamente a práxis de resolução de problemas da equipe mantenedora como fonte primária de verdade (*ground truth*) para o modelo RAG;
b) observação e aplicação de questionário com usuários na UFBA: prevê-se a condução de uma atividade prática com estudantes e pesquisadores da Universidade Federal da Bahia (UFBA) durante sessões de introdução ao uso da plataforma CorText Manager; os participantes utilizarão o protótipo do Assistente de Observabilidade Sociotécnica para diagnosticar bases de dados com anomalias de formatação e responderão a um questionário curto estruturado, visando colher percepções reais sobre as barreiras iniciais de importação e sobre a clareza pedagógica das instruções geradas pela ferramenta;
c) preparação para integração aberta (*Pull Request*): todo o desenvolvimento modular do assistente segue as convenções de diretório, configuração de parâmetros (`.yaml`) e documentação (`README.md`) adotadas no repositório oficial do CorText Manager, permitindo que o artefato final seja formalmente apresentado à equipe técnica da plataforma como uma contribuição de código aberto (*Pull Request* ou ferramenta auxiliar integrada à documentação).

> **[ESPAÇO RESERVADO — A PREENCHER APÓS A EXECUÇÃO DA OFICINA UFBA E CONTATO COM EQUIPE CORTEXT]:**
> *Inserir aqui, após a aplicação prática do protótipo, um parágrafo relatando: (1) a data de realização da oficina introdutória na UFBA e o número total de estudantes/pesquisadores participantes ($N = X$); (2) o resumo da percepção colhida no questionário curto sobre a utilidade do assistente; e (3) o registro de submissão do Pull Request ou comunicação técnica realizada com os mantenedores do CorText Manager.*

## Cronograma

O planejamento temporal do projeto foi distribuído ao longo de seis meses de execução, correlacionando diretamente as seis etapas metodológicas descritas na Seção 4.2 aos marcos de entrega da monografia e do software, conforme apresentado na Tabela 7.

| Atividades / Etapas Metodológicas | Mês 1 | Mês 2 | Mês 3 | Mês 4 | Mês 5 | Mês 6 | Status Atual |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Etapa 1: Revisão Bibliográfica (STS, Qualidade de Dados e RAG) e Análise do Código Legado | X | X | | | | | Concluído |
| Etapa 2: Engenharia de Extração (`extract_forum.py`) e Auditoria Estatística do Fórum Oficial | | X | X | | | | Concluído |
| Etapa 3: Construção, Limpeza e Vetorização da Base de Conhecimento Local (Fórum + Guia Oficial) | | | X | X | | | Em execução |
| Etapa 4: Desenvolvimento do Módulo *Pre-Flight Data Profiler* e *Early-Warning Parser* (Python/Pandas) | | | | X | X | | Planejado |
| Etapa 5: Integração do Módulo *Log Explainer & RAG* via Ollama e Interface *Companion App* | | | | X | X | | Planejado |
| Etapa 6: Testes via Engenharia do Caos, Teste A/B, Avaliação na UFBA e Redação Final do TCC | | | | | X | X | Em execução |

*Fonte: Elaborado pelo autor (2026).*