# Resultados e Discussão

## Resultados Obtidos

A apresentação dos resultados desta investigação estrutura-se em duas partes complementares, alinhadas aos objetivos específicos do trabalho. A primeira parte expõe os resultados empíricos e estatísticos consolidados a partir da auditoria censitária do fórum oficial de suporte do CorText Manager (`https://docs.cortext.net/forum/`), cumprindo o primeiro objetivo específico de caracterizar quantitativa e qualitativamente as fricções de importação de dados [@CorText2026]. A segunda parte destina-se aos resultados experimentais da avaliação do protótipo do Assistente de Observabilidade Sociotécnica perante o *Corpus de Caos* e o Teste A/B do módulo de Recuperação Aumentada por Geração (RAG).

### Mapeamento da Fricção por Formato de Entrada e Sobrecarga do Suporte Humano

Conforme demonstrado na caracterização inicial do problema, a auditoria dos 298 tópicos únicos do fórum oficial revelou que a fricção na etapa de *Data Parsing* afeta diretamente ou por derivação 66,4% de todo o acervo (198 chamados, divididos entre 84 tópicos de *Parsing* Direto na categoria *Data processing* e 114 tópicos de *Parsing* Derivado protocolados em etapas posteriores) [@CorText2026]. Ao isolar os 84 tópicos específicos da categoria oficial *Data processing*, identificou-se a distribuição empírica dos formatos científicos brutos que mais geram atrito na ingestão. O levantamento comprova que a manipulação de arquivos tabulares delimitados (CSV, com 25 ocorrências ou 29,8%) e pastas compactadas (ZIP, com 24 ocorrências ou 28,6%), seguida pelas exportações de bases bibliométricas líderes como Web of Science (19 ocorrências ou 22,6%), Scopus (11 ocorrências ou 13,1%), formato RIS (11 ocorrências ou 13,1%) e Factiva (4 ocorrências ou 4,8%), concentra quase a totalidade dos incidentes reportados, conforme ilustrado na Figura 6.

![Frequência de formatos brutos problemáticos identificados nos chamados de preparação de dados (N = 84)](images/figura2_ranking_formatos.png)
*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

A ausência de explicabilidade técnica nas mensagens de erro geradas durante a falha de ingestão desses formatos produz uma dependência direta e contínua do suporte humano prestado pelos mantenedores e desenvolvedores da plataforma [@CorText2026]. O cruzamento das variáveis de autoria de resposta (`has_staff_answer`) revelou que as dúvidas de *Data processing* demandam uma taxa de intervenção manual da equipe técnica (*Staff as Human Parser*) de 81,0% (68 de 84 tópicos), superando a taxa de atendimento manual observada nas demais categorias metodológicas da plataforma (77,1%, ou 165 de 214 tópicos), conforme demonstrado na Figura 7.

![Taxa de intervenção manual da equipe técnica do CorText Manager (Staff) por categoria de problema](images/figura3_dependencia_staff.png)
*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

Paralelamente, a inspeção dos estados formais de conclusão dos tópicos na categoria *Data processing* (gerenciados pelo sistema *DW Question & Answer* do WordPress) evidencia que exatamente metade do acervo permanece formalmente em aberto, refletindo a dificuldade operacional do usuário comum em confirmar o fechamento de suas dúvidas ou validar se a correção manual sugerida restaurou a integridade do seu banco SQLite. A Figura 8 e a Tabela 12 apresentam a distribuição detalhada dos chamados por status operacional.

![Proporção dos status registrados para os chamados da categoria oficial Data processing (N = 84)](images/figura4_status_chamados.png)
*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

| Status Formal (DW Q&A) | Ocorrências Absolutas e Relativas | Significado Operacional no Ecossistema de Suporte |
| :--- | :---: | :--- |
| *Open* (Aberto) | 42 (50,0%) | Chamado publicado e visível na comunidade, permanecendo sem marcação de conclusão formal pelo autor. |
| *Answered* (Respondido) | 26 (31,0%) | Chamado que recebeu respostas da equipe técnica ou da comunidade, mas aguarda confirmação definitiva de resolução. |
| *Resolved* (Resolvido) | 12 (14,3%) | Tópico validado formalmente com solução definitiva confirmada pelo autor da pergunta ou pela equipe técnica. |
| *Closed* (Fechado) | 3 (3,6%) | Tópico trancado administrativamente por duplicação ou encerramento direto pela moderação. |
| *Pending* (Pendente) | 1 (1,2%) | Chamado retido na fila de moderação antispam do WordPress antes de circular publicamente. |

*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

### O Custo Cognitivo da Opacidade: Evidências Estatísticas Textuais

Para mensurar quantitativamente o esforço cognitivo despendido pelos pesquisadores na formulação de seus pedidos de socorro técnico, analisou-se a extensão textual (quantidade de palavras por pergunta, atributo `question_length_words`) em todo o acervo do fórum ($N = 298$). A hipótese empírica testada estabelece que, quanto mais opaco, silencioso e tardio é o erro originado no *Data Parsing*, maior é o volume de texto explicativo, registros crípticos e fragmentos de tabelas que o usuário se vê compelido a redigir e colar no chamado para tentar se fazer compreender pela equipe de suporte. A Figura 9 e a Tabela 13 sintetizam a dispersão textual observada nos três grupos analíticos.

![Dispersão da quantidade de palavras por dúvida conforme o escopo analítico de Data Parsing (Teste de Kruskal-Wallis H = 15,92, p < 0,001)](images/figura5_dispersao_kruskal.png)
*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

| Escopo Metodológico da Dúvida | Amostra ($N$) | Mediana (Palavras) | Média (Palavras) | Terceiro Quartil ($Q_3$) | Valor Máximo Observado |
| :--- | :---: | :---: | :---: | :---: | :--- |
| 1. *Parsing* Indireto / Derivado | 114 | 95,0 pal. | 129,6 pal. | 163,0 pal. | 1.118 pal. (Tópico #2) |
| 2. *Parsing* Direto (*Data processing*) | 84 | 81,5 pal. | 93,8 pal. | 117,0 pal. | 387 pal. (Tópico #280) |
| 3. Não Relacionado a *Parsing* | 100 | 68,5 pal. | 90,6 pal. | 108,0 pal. | 765 pal. (Tópico #109) |

*Fonte: Elaborado pelo autor a partir dos dados auditados do fórum oficial (2026).*

Considerando a assimetria positiva das distribuições de contagem de palavras, aplicaram-se testes de hipótese não paramétricos sobre as amostras [@Kruskal1952; @Mann1947]. No Teste de Kruskal-Wallis para comparação simultânea dos três grupos, obteve-se a estatística $H = 15,923$, com valor de probabilidade $p = 0,00035$ ($p < 0,001$), rejeitando-se categoricamente a hipótese nula com 99,9% de confiança e comprovando a existência de diferença estatisticamente altamente significante entre as extensões textuais dos três escopos [@Kruskal1952]. Complementarmente, na aplicação do Teste de Mann-Whitney contrastando o conjunto total de problemas de *Data Parsing* (Direto somado ao Indireto, $N = 198$) contra os demais temas metodológicos ($N = 100$), obteve-se $Z = 3,380$ ($p = 0,0007 < 0,001$), confirmando que chamados envolvendo falhas de ingestão e formatação exigem significativamente mais palavras e esforço descritivo por parte do pesquisador [@Mann1947].

### Resultados da Engenharia do Caos, do Teste A/B e da Avaliação de Usabilidade

> **[ESPAÇO RESERVADO — RESULTADOS DOS TESTES DO PROTÓTIPO (ENGENHARIA DO CAOS, TESTE A/B E OFICINA UFBA)]:**
> *Inserir aqui, imediatamente após a execução da bateria de testes descrita na Seção 5.4:*
> *1. **Resultados da Engenharia do Caos (Validação de H1):** O percentual exato da Taxa de Detecção Preventiva ($TDP$) obtido pelo módulo `data_quality_profiler.py` sobre os 22 casos da Tabela 11 (meta $\ge 80\%$) e o tempo médio de execução em milissegundos;*
> *2. **Resultados do Teste A/B no Ollama (Validação de H2):** A tabela comparativa com a pontuação média (0 a 6 pontos) obtida pelo Assistente com RAG Local versus o LLM Vanilla nos 20 casos do fórum, destacando a redução na taxa de alucinação de interface;*
> *3. **Resultados da Oficina na UFBA:** O resumo quantitativo e qualitativo das respostas dos participantes ($N = X$) ao questionário de usabilidade.*

## Análise e Discussão

Os resultados empíricos auferidos na auditoria do fórum validam integralmente os pressupostos teóricos mobilizados a partir dos Estudos de Ciência e Tecnologia (STS) e da Engenharia de Qualidade de Dados. A constatação estatística de que o grupo de *Parsing* Indireto apresenta a maior mediana (95,0 palavras), a maior média (129,6 palavras) e o maior terceiro quartil (163,0 palavras) de todo o ecossistema ($p < 0,001$) [@Kruskal1952] materializa empiricamente o conceito de fricção de dados de @Edwards2010 e o princípio da ruptura infraestrutural de @Bowker1999. Quando o analisador sintático nativo silencia exceções ou aplica truncamentos defensivos sem notificar o usuário, o erro não desaparece: ele contamina o banco relacional SQLite e eclode tardiamente na forma de artefatos vazios.

O caso mais emblemático desse fenômeno em todo o acervo histórico é o Tópico #2, que registra o valor máximo absoluto de 1.118 palavras em uma única pergunta e pertence justamente ao grupo de *Parsing* Derivado [@CorText2026]. Nesse chamado, o pesquisador relatou que o algoritmo de mapeamento de redes falhou exibindo a mensagem `'network you produced is empty'`. Impedido pela opacidade da caixa preta [@Latour1987] de compreender que a causa raiz residia em delimitadores corrompidos na etapa inicial de importação do CSV, o usuário viu-se forçado a colar tabelas inteiras, scripts e centenas de linhas de dados brutos no fórum na tentativa de obter auxílio. De maneira convergente, a taxa de 81,0% de intervenção manual da equipe técnica nos chamados de *Data processing* comprova que, na ausência de um módulo preventivo de *Data Profiling* [@Wang1996; @Naumann2014] e de um tradutor de registros ancorado em RAG [@Lewis2020], o trabalho invisível de curadoria (*data janitor work*) descrito por @DIgnazio2020 sobrecarrega severamente os próprios engenheiros mantenedores da plataforma (como evidenciado nas interações em que desenvolvedores precisam solicitar acesso manual aos projetos privados dos usuários diante de *logs* vazios) [@CorText2026].

> **[ESPAÇO RESERVADO — DISCUSSÃO DOS RESULTADOS DO PROTÓTIPO]:**
> *Inserir aqui, após o preenchimento dos resultados da Engenharia do Caos e do Teste A/B, um a dois parágrafos discutindo como o desempenho obtido pelo Pre-Flight Data Profiler e pelo Log Explainer & RAG confirma as hipóteses H1 e H2 e protege a rastreabilidade das inscrições concretas postulada por @Abdo2021.*

## Limitações Encontradas

A condução desta pesquisa e o desenvolvimento do protótipo apresentaram limitações de natureza arquitetural, computacional e metodológica que devem ser registradas com transparência científica:

a) operação desacoplada da interface nativa de produção: em virtude da delimitação de escopo e do requisito de não intrusão no código-fonte de produção em PHP e JavaScript do servidor oficial do CorText Manager (RNF02), o assistente opera como uma aplicação companheira (*companion app*) externa em Streamlit; embora a memória de sessão unifique o estágio de *Data Profiling* e o estágio de RAG, o usuário ainda precisa realizar a transição manual de tela e colar a mensagem de erro ou *traceback* quando ocorre uma falha remota no servidor oficial;
b) restrições de hardware local e janela de contexto em modelos compactos: a adoção estrita de Modelos de Linguagem de Grande Escala executados localmente via Ollama (RNF01), utilizando modelos compactos de pesos abertos (de 3,8 bilhões a 8 bilhões de parâmetros) para viabilizar a execução em computadores pessoais sem unidades de processamento gráfico dedicadas de alto custo, impõe limites de janela de contexto e maior latência de geração em comparação a modelos proprietários massivos em nuvem;
c) cobertura circunscrita às heurísticas de entrada (*Data Parsing*): conforme definido no escopo do projeto, a base de regras determinísticas do *Pre-Flight Data Profiler* limita-se às 22 anomalias mapeadas no script de ingestão e à verificação básica de matrizes vazias no banco SQLite recém-criado, não auditando distorções matemáticas ou escolhas inadequadas de hiperparâmetros cometidas pelo pesquisador em módulos analíticos avançados posteriores (como métricas de modularidade de Louvain ou algoritmos de modelagem de tópicos).

> **[ESPAÇO RESERVADO OPCIONAL — LIMITAÇÕES ADICIONAIS DOS TESTES]:**
> *Caso surjam limitações específicas durante a bateria final de testes ou durante a oficina prática com usuários na UFBA (ex.: falsos positivos em dialetos CSV raros ou tamanho amostral de participantes), acrescentar um parágrafo final nesta subseção.*