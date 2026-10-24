# Dicionário de Variáveis do Dataset Auditado do Fórum, Repositório Aberto e Dashboard Interativo

Com o objetivo de assegurar total transparência científica, auditabilidade estatística e reprodutibilidade dos resultados empíricos apresentados neste Trabalho de Conclusão de Curso (RNF04), todos os conjuntos de dados gerados pelo extrator determinístico `extract_forum.py`, bem como os códigos-fonte e o painel interativo de visualização, foram disponibilizados publicamente em repositórios abertos[cite: 169, 173].

## Dicionário de Atributos do Conjunto de Dados (`forum_topics.csv`)

O conjunto de dados tabular consolidado a partir da varredura integral das 34 páginas do fórum oficial de suporte do CorText Manager ($N = 298$ tópicos únicos, com paridade de 100% em relação aos arquivos `forum_topics_full.json` e `forum_corpus.md`) estrutura-se em 25 atributos métricos, temporais, textuais e taxonômicos, detalhados na Tabela 14[cite: 169].

| Ordem | Nome do Atributo no Dataset | Tipo de Dado | Descrição Operacional e Metodológica da Variável |
| :---: | :--- | :---: | :--- |
| 01 | `id` | Inteiro | Identificador numérico único sequencial atribuído ao tópico auditado (1 a 298). |
| 02 | `page` | Inteiro | Número da página da listagem oficial do fórum (1 a 34) onde o tópico foi coletado. |
| 03 | `title` | Texto (*String*) | Título original completo da dúvida publicada pelo usuário no fórum. |
| 04 | `url` | Texto (*URL*) | Endereço eletrônico permanente (*permalink*) da discussão no portal `docs.cortext.net`. |
| 05 | `status` | Categórico | Estado formal do chamado no sistema *DW Question & Answer* (`Open`, `Answered`, `Resolved`, `Closed`, `Pending`). |
| 06 | `is_resolved` | Booleano | Indicador lógico (`True`/`False`) que atesta se o chamado possui marcação formal de resolvido (`Resolved`). |
| 07 | `is_answered` | Booleano | Indicador lógico (`True`/`False`) que registra se o tópico recebeu ao menos uma resposta pública. |
| 08 | `category` | Categórico | Categoria oficial atribuída pelo autor no momento de abertura do chamado (ex.: `Data processing`, `Network mapping`). |
| 09 | `author_name` | Texto (*String*) | Nome de exibição pública do pesquisador ou usuário que abriu o tópico de dúvida. |
| 10 | `author_user` | Texto (*String*) | Identificador único de usuário (*username* ou *slug*) do autor da pergunta na plataforma. |
| 11 | `time_ago` | Texto (*String*) | Registro textual relativo de tempo exibido na interface web no momento da coleta. |
| 12 | `date_published` | Data/Hora (ISO) | Data e hora exatas de publicação original da dúvida (padrão ISO 8601 extraído via marcação JSON-LD Schema). |
| 13 | `date_modified` | Data/Hora (ISO) | Data e hora exatas da última modificação ou interação registrada no tópico (padrão ISO 8601). |
| 14 | `views_count` | Inteiro | Quantidade acumulada de visualizações orgânicas da discussão pela comunidade global. |
| 15 | `answers_count` | Inteiro | Número total de respostas publicadas dentro do fio de discussão do tópico. |
| 16 | `votes_count` | Inteiro | Saldo de votos de relevância atribuídos pela comunidade ao tópico no sistema *DW Q&A*. |
| 17 | `question_length_chars` | Inteiro | Extensão total do texto da pergunta inicial medida em quantidade de caracteres. |
| 18 | `question_length_words` | Inteiro | Extensão total do texto da pergunta inicial medida em quantidade de palavras (utilizada nos testes de Kruskal-Wallis e Mann-Whitney). |
| 19 | `tags` | Texto (*Lista*) | Rótulos e palavras-chave (*tags*) indexados pelo autor ao tópico para classificação temática. |
| 20 | `has_staff_answer` | Booleano | Indicador lógico (`True`/`False`) que comprova se houve intervenção manual da equipe técnica oficial (*Staff* do CorText). |
| 21 | `first_answer_author` | Texto (*String*) | Nome do autor responsável pela primeira resposta de suporte fornecida no chamado. |
| 22 | `answers_authors` | Texto (*Lista*) | Lista consolidada de todos os participantes e engenheiros que responderam ao tópico. |
| 23 | `is_parsing_related` | Booleano | Classificador mestre (`True`/`False`) que indica se o tópico envolve problemas de *Data Parsing* (Direto ou Derivado, $N = 198$). |
| 24 | `parsing_type` | Categórico | Classificação analítica do escopo: `Parsing Direto`, `Parsing Indireto / Derivado` ou `Não Relacionado`. |
| 25 | `parsing_cause` | Categórico | Critério heurístico ou formato bruto específico que motivou a falha (CSV, ZIP, WOS, Scopus, RIS, Factiva, Encoding, Rede Vazia). |

*Fonte: Elaborado pelo autor a partir do dataset auditado `forum_topics.csv` (2026).*

## Recursos Complementares, Código-Fonte e Painel Interativo

Os artefatos computacionais, bases de dados brutas e enriquecidas, scripts de extração e visualização interativa desenvolvidos nesta pesquisa encontram-se permanentemente acessíveis por meio dos seguintes endereços eletrônicos oficiais[cite: 169]:

a) Painel Interativo de Auditoria Estatística do Fórum (implantado em nuvem via *Streamlit Community Cloud*): disponível em `https://cortext-forum-analysis.streamlit.app/`[cite: 169];
b) Repositório Oficial do Código-Fonte, Extrator (`extract_forum.py`) e Conjuntos de Dados Auditados (`forum_topics.csv`, `forum_topics_full.json` e `forum_corpus.md`): disponível em `https://github.com/Wellington-Miguel/cortext-forum-analysis`[cite: 169].