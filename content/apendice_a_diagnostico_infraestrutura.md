# Diagnóstico de Infraestrutura, Catálogo das 22 Anomalias do Data Parsing e Formatos Suportados

Este apêndice consolida o mapeamento técnico exaustivo das vulnerabilidades e heurísticas de programação defensiva identificadas na auditoria estática do código-fonte legado em linguagem Python responsável pelo módulo de *Data Parsing* do CorText Manager (`parser_science_se.py`), bem como a taxonomia completa de formatos de arquivos aceitos pelo analisador sintático nativo[cite: 166, 173]. Sob a ótica dos Estudos de Ciência e Tecnologia (STS) [@Latour1987; @Bowker1999], cada item documentado a seguir explicita o mecanismo pelo qual decisões internas de infraestrutura, tomadas originalmente para evitar travamentos visíveis do servidor compartilhado, atuam como uma caixa preta que pode introduzir vieses metodológicos ou suprimir inscrições concretas [@Abdo2021], justificando as diretrizes de intervenção do módulo preventivo (*Pre-Flight Data Profiler*) e do módulo reativo (*Log Explainer & RAG*)[cite: 166, 170].

## Catálogo das 22 Anomalias Arquiteturais Mapeadas no Código Legado

### 1. Codificação e Caracteres Especiais (A Perda Silenciosa UTF-8)

* **O Problema:** A rotina legada `utf_8_encoder` utiliza um bloco `try/except` de contenção ao tentar converter a codificação dos caracteres do arquivo bruto para o padrão UTF-8[cite: 166]. Ao deparar-se com uma falha de leitura de bytes, em vez de interromper o processo ou notificar a interface, o script executa o comando `yield('')` e emite apenas um registro de depuração (*debug*) que permanece oculto na interface web[cite: 166].
* **O Impacto:** Uma linha inteira de dados que contenha um caractere de idioma não suportado naquela codificação (como alfabetos asiáticos, cirílico ou acentuação em Windows-1252) é compulsoriamente convertida em um espaço em branco[cite: 166, 170]. O pesquisador submete um arquivo denso e recebe uma tabela incompleta ou oca ao final da importação, sem ser notificado sobre a perda sistemática de suas evidências empíricas[cite: 166].
* **A Solução via *Profiling*:** O módulo utiliza a biblioteca Pandas e verificadores de cadeias de bytes para detectar previamente a codificação estrutural de todo o arquivo bruto antes da ingestão, emitindo um alerta ativo ao usuário: *"O arquivo possui caracteres inválidos ou não-UTF-8 na linha X. Corrija a codificação original para evitar a deleção automática deste dado"*[cite: 166].

### 2. Tratamento de Exceções Silenciosas e Registros Vazios

* **O Problema:** Durante a execução do script primário e a criação das tabelas no banco de dados relacional SQLite (especificamente na chamada `fonctions.insert_notices`), exceções geradas por incompatibilidade de tipos de dados mascaram o rastro técnico real (*stack trace*)[cite: 166, 173]. Para forçar a parada ou continuidade nos blocos `except`, o código legado contém comandos deliberadamente inexistentes (como a *string* `dkjslq`), mensagens informais impressas apenas no terminal do servidor (como `shitty1`) e registros que não são repassados à interface gráfica do usuário[cite: 166, 173].
* **O Impacto:** O pesquisador depara-se frequentemente com a mensagem genérica e opaca `"No info in Logs"` (sem informação nos registros), o que inviabiliza qualquer diagnóstico autônomo ou ação corretiva imediata em sua pesquisa[cite: 166].
* **A Solução via RAG:** A execução é monitorada por uma camada de observabilidade que captura o *traceback* técnico real da exceção e o submete ao modelo de linguagem local via Ollama[cite: 166]. O modelo atua cruzando o código do erro com o manual da plataforma e com o histórico do fórum para traduzir a falha de infraestrutura em instruções claras para o pesquisador[cite: 166].

### 3. A Truncagem Silenciosa de Colunas em Arquivos CSV

* **O Problema:** O analisador tabular utiliza o comando de fatiamento imperativo `row=row[:nb_field]` para cortar abruptamente qualquer linha cujas células ultrapassem o número de colunas originalmente previsto no cabeçalho[cite: 166].
* **O Impacto:** Caso exista uma vírgula não escapada dentro de um campo de texto longo (como a transcrição de uma entrevista ou um resumo científico), o interpretador do Python entende que há uma coluna excedente[cite: 166]. Em vez de acusar um erro de formatação estrutural, o sistema deleta silenciosa e permanentemente todo o final do texto do usuário para forçar o encaixe no banco SQLite[cite: 166].
* **A Solução via *Profiling*:** O sistema valida preventivamente a consistência quantitativa dos separadores de cada linha em relação ao cabeçalho; ao detectar incompatibilidades, dispara um alerta obstativo sobre o risco iminente de truncamento antes que o analisador atue de forma destrutiva[cite: 166].

### 4. O Preenchimento Cego de Campos em Arquivos CSV

* **O Problema:** Em oposição direta à truncagem, caso uma linha possua menos colunas do que o cabeçalho exige (`len(row) < len(dico_tag_list)`), o script compensa a falha injetando campos vazios de maneira cega por meio de um laço `row.insert()`[cite: 166, 173].
* **O Impacto:** Os dados subsequentes da linha sofrem um deslocamento posicional em cascata[cite: 166]. Variáveis textuais e metadados essenciais desaparecem sob colunas de outra natureza taxonômica, corrompendo as consultas SQL e os cruzamentos futuros que o pesquisador realizar[cite: 166].
* **A Solução via *Profiling*:** Intervenção prévia por meio do motor da biblioteca Pandas (`ParserError`), gerando um relatório estrutural que aponta exatamente quais linhas apresentam escassez de delimitadores e evitando o desalinhamento do banco de dados[cite: 166].

### 5. O Falso Positivo do Detector CSV Sniffer (O Limite de 4 KB)

* **O Problema:** Para automatizar a detecção de separadores tabulares (vírgula, tabulação ou ponto e vírgula), o código utiliza a classe `csv.Sniffer`, mas restringe a leitura de amostragem do arquivo estritamente aos primeiros 4.094 bytes[cite: 166].
* **O Impacto:** O volume de 4.094 bytes equivale a cerca de 4.000 caracteres[cite: 166]. Se a primeira célula do arquivo CSV do usuário contiver um resumo científico extenso, o detector lê apenas essa célula, esgota seu limite de memória antes de encontrar o primeiro separador, infere a formatação erroneamente e compromete o fatiamento lógico de todo o corpus[cite: 166].
* **A Solução via *Profiling*:** O módulo abandona a limitação estática por bytes e realiza uma leitura estatística robusta das primeiras 100 linhas completas do arquivo; em caso de textos excessivamente longos que prejudiquem a inferência automática, orienta o usuário a declarar o separador manualmente na interface[cite: 166].

### 6. Caracteres Especiais Invisíveis (Separadores Secundários Multivalorados)

* **O Problema:** A arquitetura do CorText Manager exige que células contendo múltiplos valores (como uma lista de vários coautores ou instituições em um único artigo) sejam separadas por cadeias de caracteres idiossincráticas e rígidas, tais como `|%|` ou `***`[cite: 166, 173].
* **O Impacto:** O uso de separadores convencionais nos arquivos originais do pesquisador (como vírgulas ou pontos e vírgulas) confunde o script de ingestão[cite: 166]. O sistema passa a tratar cinco autores distintos como se fossem uma única entidade aglutinada, ou embaralha as hierarquias de coautoria na rede[cite: 166].
* **A Solução via *Profiling*:** O assistente realiza uma varredura nos campos textuais repetitivos para mapear os caracteres de separação mais frequentes na base bruta e fornece orientações visuais preventivas sobre como o sistema dividirá os valores internos das células[cite: 166].

### 7. Limpeza de Cadeias Textuais e Formatações Sujas (Factiva e XLSX)

* **O Problema:** Textos brutos provenientes de extrações web (*web scraping*), tais como exportações de notícias do portal Factiva convertidas em planilhas, frequentemente contêm resíduos de formatação CSS ou HTML infiltrados no texto (como a *string* `"sm-margin-TopNews"`)[cite: 166].
* **O Impacto:** A presença de marcações algorítmicas residuais no meio do texto interrompe os extratores semânticos do CorText Manager, impedindo o reconhecimento de entidades e resultando em falhas de processamento nas quais a criação dos nós (*nodes*) da rede metodológica é abortada[cite: 166].
* **A Solução via RAG:** Ao interceptar a quebra do processo, o modelo de linguagem diagnostica o travamento reconhecendo especificamente o padrão de código residual capturado no registro de erro e orienta o pesquisador a utilizar a função de localização e substituição (`replace()`) em um editor externo, traduzindo o problema técnico em uma tarefa operacional simples[cite: 166].

### 8. Intolerância a Nomes de Arquivos Acentuados (Lotes ZIP e PDFs)

* **O Problema:** No processamento de arquivos compactados (`.zip`) ou diretórios de PDFs iterados, caso exista acentuação ou caracteres não padronizados no nome original do documento (por exemplo, `SISTEMATIZACIÓN.pdf`), as funções estáticas de substituição de caminho (`.replace()`) nativas falham[cite: 166].
* **O Impacto:** O mapeamento do diretório do corpus é integralmente corrompido[cite: 166]. Como válvula de escape no bloco `except`, o desenvolvedor inseriu comandos propositalmente inválidos no script (invocando a variável inexistente `dkjslq`) para induzir a parada do servidor, mascarando para o usuário final o fato de que a plataforma não suporta nomes de arquivos acentuados[cite: 166, 173].
* **A Solução via *Profiling*:** O módulo varre a taxonomia de todos os arquivos contidos no lote de envio antes do processamento e emite o aviso: *"Detectamos caracteres acentuados ou especiais nos nomes dos arquivos. A plataforma exige nomes limpos alfanuméricos. Renomeie em lote antes de prosseguir para evitar falha do servidor"*[cite: 166].

### 9. O Processamento de Arquivos PDF e o Esgotamento Silencioso de Tempo

* **O Problema:** A rotina de extração textual de arquivos PDF baseia-se em uma verificação de diretório local (`if 'Users/jpcointet/' in os.getcwd():`)[cite: 166, 173]. Nos demais ambientes, o script dispara um subprocesso externo (`pdf2txt.py`) acompanhado de um laço `while` que tenta abrir o arquivo convertido 200 vezes com apenas um segundo de intervalo entre cada tentativa (`time.sleep(1)`)[cite: 166, 173].
* **O Impacto:** Arquivos PDF extensos, com alta densidade gráfica ou protegidos por criptografia demandam naturalmente mais de 200 segundos para serem convertidos[cite: 166]. Ao esgotar esse contador (`if h > 200`), o script encerra o laço de espera por esgotamento de tempo (*timeout*) e descarta o documento silenciosamente sem gerar avisos na tela, privando a análise daquele material[cite: 166, 173].
* **A Solução via RAG:** O assistente intercepta o registro de estafa do limite temporal diretamente nos *logs* de execução e intervém proativamente, sugerindo que o pesquisador utilize utilitários locais para converter seus PDFs pesados para o formato `.txt` antes do envio[cite: 166].

### 10. Amostragem Arbitrária de Esquemas JSON (O Limite de 100 Linhas)

* **O Problema:** Ao ingerir bases de dados semiestruturadas como arquivos JSON extraídos de redes sociais ou APIs web, o sistema precisa construir um mapa relacional de colunas[cite: 166]. Para inferir o cabeçalho, o código emprega um laço restritivo (`for notice in data[:100]:`), obrigando o analisador a inspecionar estritamente os primeiros 100 registros[cite: 166].
* **O Impacto:** Em extrações dinâmicas da web, a variabilidade de metadados entre documentos é elevada[cite: 166]. Se um cientista político submeter 50 mil registros de mídias sociais e, a partir do registro de número 101, surgir uma nova variável fundamental (como localização geográfica ou `retweet_status`), o sistema a ignorará até o final do processo e a métrica jamais existirá no banco SQLite[cite: 166].
* **A Solução via *Profiling*:** O módulo em Pandas elimina a trava numérica de 100 registros e executa a leitura integral e iterativa das chaves de toda a extensão do arquivo JSON, garantindo a completude e a integridade do esquema metodológico[cite: 166].

### 11. Exclusão Silenciosa de Duplicatas (O Caso Web of Science)

* **O Problema:** O analisador possui um mecanismo de deduplicação automático, forçado e irreversível: se a variável identificadora `notice_unique_id` do registro atual já tiver sido armazenada na lista em memória (`known_notices`), o documento presente é imediatamente descartado do fluxo de ingestão[cite: 166].
* **O Impacto:** Embora útil em condições normais, essa regra impõe um dano severo em bases da Web of Science (WOS/ISI) levemente corrompidas ou editadas manualmente[cite: 166]. Caso os identificadores únicos dos artigos venham em branco por falha de exportação, o CorText Manager assume erroneamente que todos os milhares de artigos subsequentes são cópias idênticas do primeiro registro vazio, deletando a base acadêmica inteira de forma silenciosa e entregando uma rede vazia[cite: 166].
* **A Solução via *Profiling*:** Contagem preventiva de integridade de chaves únicas, exibindo o alerta: *"Foram detectados X registros com identificadores duplicados ou em branco. O analisador os considerará cópias e os excluirá. Deseja revisar sua base para preservar a amostragem?"*[cite: 166].

### 12. Destruição de Cabeçalhos por Expressão Regular

* **O Problema:** Visando higienizar os nomes de tabelas e colunas para o banco SQLite, o código aplica uma expressão regular agressiva (`re.sub(r'\W+', '', field)`) que varre e remove qualquer caractere do título de uma coluna que não pertença estritamente ao alfabeto latino básico (ASCII) ou a algarismos numéricos[cite: 166].
* **O Impacto:** Essa restrição linguística penaliza pesquisas internacionais ou bases com metadados específicos[cite: 166]. Colunas redigidas em alfabeto cirílico, árabe, mandarim, ou contendo caracteres especiais e acentuações necessárias metodologicamente, são reduzidas a cadeias de caracteres vazias (`""`), desaparecendo da arquitetura de dados final[cite: 166].
* **A Solução via *Profiling*:** O módulo fornece um relatório prévio de mapeamento (*De-Para*), sinalizando quais colunas possuem caracteres incompatíveis e precisarão ser renomeadas pelo pesquisador para termos em alfabeto latino básico antes da submissão[cite: 166].

### 13. O Subprocesso Externo do Formato ISTEX via Contêiner Docker

* **O Problema:** A plataforma lista suporte nativo a arquivos do repositório acadêmico francês ISTEX, mas o script principal não possui um analisador interno para ele[cite: 166]. Em vez disso, o código Python delega o processamento a um contêiner virtualizado externo por meio do script `docker_wrapper.py`[cite: 166].
* **O Impacto:** Caso a base submetida seja volumosa, o ambiente virtual (Docker) frequentemente esgota a memória principal disponível no servidor e encerra a execução abruptamente[cite: 166]. A instrução `sys.exit()` finaliza a tarefa sem reportar a causa da falha à interface web do CorText Manager, mantendo a tela do pesquisador paralisada indefinidamente[cite: 166].
* **A Solução via RAG:** O modelo de linguagem é instruído sobre essa topologia de subprocessos; ao reconhecer nos registros o colapso de memória atrelado ao contêiner, fornece o diagnóstico: *"O ambiente isolado (Docker) responsável por processar o formato ISTEX esgotou sua memória. Divida sua base em partes menores para viabilizar a conclusão"*[cite: 166].

### 14. O "Ano Zero" Destrutivo na Conversão de Datas (LexisNexis)

* **O Problema:** O tratamento de datas oriundas de arquivos jornalísticos do formato LexisNexis altera a representação cronológica padrão[cite: 166]. O script não armazena apenas o ano civil da matéria, mas instaura uma constante matemática base (`d0 = datetime(1990,1,1)`) e converte as datas na quantidade de meses transcorridos desde esse "Ano Zero"[cite: 166].
* **O Impacto:** Matérias de imprensa publicadas até 1989 (anteriores a janeiro de 1990) resultam em cálculos de tempo com valores inteiros negativos[cite: 166]. Embora a tabela do banco SQLite aceite o número negativo na coluna, essa abstração provoca falhas matemáticas em algoritmos posteriores de fatiamento longitudinal, como o módulo *Period Slicer*[cite: 166].
* **A Solução via *Profiling*:** Uma varredura estatística de valores mínimos e máximos nas colunas temporais alerta o pesquisador sobre o conflito estrutural: *"As datas do seu corpus antecedem a configuração nativa de referência (1990) para este formato. O sistema gerará variáveis negativas que afetarão análises temporais futuras"*[cite: 166].

### 15. A Coerção Arbitrária do "Ano 1" em Registros Sem Data

* **O Problema:** Diante de bases nos formatos Excel (`.xls`) ou JSON que possuam falhas de preenchimento, caso o script não consiga identificar o campo de tempo cronológico de um registro, ele executa uma injeção de preenchimento artificial e arbitrário atribuindo a matriz `[['1']]`[cite: 166].
* **O Impacto:** Registros contemporâneos com data ausente recebem compulsoriamente o ano `"1 d.C."` como data de publicação[cite: 166]. Como consequência, o gráfico demográfico de evolução do campo científico estudado torna-se severamente distorcido (abrangendo dois milênios no eixo horizontal), inviabilizando o isolamento visual de períodos históricos na pesquisa[cite: 166].
* **A Solução via *Profiling*:** Detecção estrutural de datas nulas ou vazias, emitindo o aviso: *"Detectamos N registros sem datas válidas preenchidas. O analisador nativo atribuirá arbitrariamente o Ano 1. Deseja realizar o preenchimento prévio ou excluí-los?"*[cite: 166].

### 16. Tipagem Estrita e Espaços Marginais em Datas (Descarte por Outofscope)

* **O Problema:** A validação final de datas aplica uma coerção reversa estrita, verificando a condição `str(int(x)) != x`[cite: 166]. O código converte a *string* lida para um número inteiro e novamente para *string*, exigindo igualdade literal absoluta entre ambas[cite: 166].
* **O Impacto:** Um ano que contenha um simples espaço em branco invisível ao final na digitação da planilha original (por exemplo, `"1998 "`) converte-se com sucesso no inteiro `1998`, mas falha na comparação textual de retorno (`"1998" != "1998 "`)[cite: 166]. O código penaliza o registro atribuindo-lhe a marcação `outofscope` e descartando o documento da série histórica (`ignoring this record`)[cite: 166, 173].
* **A Solução via *Profiling*:** Aplicação automatizada de rotinas preventivas de higienização de cadeias de caracteres (`.strip()`), erradicando espaços marginais invisíveis nas variáveis cronológicas antes da submissão e prevenindo exclusões injustificadas[cite: 166].

### 17. Destruição de Citações e Notas entre Colchetes

* **O Problema:** A função interna denominada limpeza de marcações wiki apoia-se em uma expressão regular abrangente (`\[[^]]*\]`), cujo objetivo original era remover hiperlinks residuais[cite: 166].
* **O Impacto:** A aplicação indiscriminada dessa expressão regular resulta em perda qualitativa de metadados textuais[cite: 166]. Qualquer observação contextual redigida entre colchetes em transcrições de entrevistas qualitativas (como `[o entrevistado hesita]`), variáveis metodológicas (`[Grupo Controle]`) ou marcações numéricas de citações bibliográficas (`[14]`) são integralmente apagadas do corpus final[cite: 166].
* **A Solução via *Profiling*:** Verificação preventiva de padrões (*Regex Matching*) que exibe a recomendação: *"Detectamos o uso de colchetes [...] no corpo do texto. Sugerimos substituí-los por parênteses (...) nas suas transcrições originais para evitar a deleção permanente de notas durante o processamento"*[cite: 166].

### 18. A Conversão Semântica de Valores "NA" em "0"

* **O Problema:** Os processos iterativos destinados à extração de arquivos JSON e mensagens SMS possuem uma regra condicional estrita: `if y == 'NA': y='0'`[cite: 166].
* **O Impacto:** Células, atributos institucionais e colunas rotuladas originalmente como `"NA"` (*Not Available* ou Não Disponível) recebem compulsoriamente a *string* numérica `"0"`[cite: 166]. Nas fases posteriores de mapeamento visual de redes do CorText Manager, isso gera um nó artificial (*nó fantasma* de rótulo `"0"`) que conecta falsamente documentos, autores e instituições que partilham apenas a ausência daquela informação[cite: 166, 170].
* **A Solução via *Profiling*:** Mapeamento exato das ocorrências da *string* `"NA"` nas matrizes, orientando o usuário: *"O sistema converterá campos 'NA' na categoria de código zero. Recomendamos deixá-los integralmente em branco na planilha base para não enviesar a topologia da rede"*[cite: 166].

### 19. Raspagem Web Engessada e Frágil em Arquivos HTML (Factiva)

* **O Problema:** Para capturar metadados de autoria oriundos da plataforma de notícias Factiva em formato HTML, o analisador percorre a árvore do documento buscando a presença literal e estrita da cadeia `'div class="author">'`[cite: 166].
* **O Impacto:** Esse desenho pressupõe um leiaute externo inalterável[cite: 166]. Diante de qualquer atualização efetuada pela plataforma emissora (como a mudança para letra maiúscula, adição de classes CSS extras ou exportação com interface em outro idioma, conforme documentado no fórum oficial), o extrator falha silenciosamente e gera uma base de dados esvaziada de metadados de autoria[cite: 166, 173].
* **A Solução via *Profiling*:** Checagem sintática exploratória sobre a presença e sobrevivência das marcações HTML esperadas pelo extrator nativo, informando antecipadamente ao pesquisador o risco de geração de tabelas de autoria em branco[cite: 166].

### 20. Inchaço Artificial da Amostra (Clonagem Silenciosa de Linhas)

* **O Problema:** Infiltrada no laço condicional destinado à recepção de arquivos CSV encontra-se a verificação de um termo específico em língua francesa: `nombre_de_personnes_`[cite: 166]. Caso essa nomenclatura seja utilizada como título de uma coluna numérica (contendo, por exemplo, o valor `"50"`), ela aciona um laço `for` interno que reinscreve a mesma linha cinquenta vezes no banco de dados SQLite[cite: 166].
* **O Impacto:** Sem emitir notificações na interface alertando sobre tal multiplicação, esse gatilho legado clona artificialmente a ocorrência das palavras e metadados daquela linha, distorcendo as frequências estatísticas e os pesos das arestas submetidas pelo cientista[cite: 166].
* **A Solução via *Profiling*:** Inspeção e saneamento dos títulos de colunas no ato da verificação prévia, bloqueando gatilhos operacionais ocultos que alterem a proporção estatística da amostragem original sem confirmação explícita[cite: 166].

### 21. Planificação Estrutural de Documentos Densos (O Separador Artificial)

* **O Problema:** A conversão automatizada do conteúdo textual de documentos densos (`.pdf`, `.docx` ou `.txt`) subverte a segmentação orgânica de parágrafos quando o parâmetro específico não é acionado: o desenvolvedor instruiu a variável de divisão do Python a buscar um delimitador artificial inalcançável (a sequência `"djkqsjsdlmkq s dsq:kmmkdsq dklmqj klsq "`), inserida para impedir a quebra automática em subníveis[cite: 166].
* **O Impacto:** Ignorando a estrutura de capítulos e parágrafos de uma tese acadêmica ou livro, todo o documento é soldado em um único bloco monolítico de texto[cite: 166]. A riqueza relacional baseada na premissa de coocorrência de termos no mesmo parágrafo é perdida[cite: 166].
* **A Solução via *Profiling*:** O módulo de triagem detecta arquivos textuais extensos e adverte preventivamente sobre a limitação semântica: *"Aviso: As quebras metodológicas de parágrafos sofrerão achatamento estrutural. Considere subdividir o material ou ativar a opção de fatiamento por parágrafo antes da submissão"*[cite: 166].

### 22. Rigidez Hierárquica em Esquemas XML (PubMed) e Teto Volumétrico de 150 Mil Sentenças

* **O Problema:** Em bases médicas provenientes da PubMed em formato XML, o analisador engessa o desmembramento da matriz de autoria exigindo estritamente três subdivisões fixas de nomes (Nome, Sobrenome e Iniciais)[cite: 166]. Paralelamente, em corpora textuais processados por fragmentos, o código fixa um escopo estático de leitura de `10.000` laços englobando blocos fechados de `15` linhas (totalizando 150.000 sentenças)[cite: 166].
* **O Impacto:** A imposição dessas diretrizes apaga dados que divirjam da modelagem estrita: a presença de autores corporativos ou sem iniciais em arquivos XML provoca uma exceção de índice (`IndexError`) não exibida na tela que deleta a autoria em massa[cite: 166]. No aspecto volumétrico, arquivos extensos que ultrapassem 150.000 sentenças (como transcrições legislativas ou acervos históricos) têm o excedente de suas amostras cortado silenciosamente do montante submetido a estudo[cite: 166].
* **A Solução via *Profiling*:** Auditoria volumétrica antecipada para mitigar o truncamento dimensional (disparando alertas perante o teto arquitetural de 150.000 sentenças) combinada à validação prévia de completude das ramificações de autoria em esquemas XML[cite: 166].

## Taxonomia de Formatos de Dados Suportados pelo Analisador Nativo

Segundo a dissecação algorítmica do módulo de *Data Parsing* e a documentação oficial da plataforma [@CorText2026], o sistema CorText Manager prevê o recebimento via interface web e a atribuição de rotinas específicas de importação para cinco famílias estruturais de formatos científicos[cite: 166]:

a) formatos bibliométricos e acadêmicos: compreendem o formato `isi` (arquivo padrão de exportação em texto plano e matrizes do portal Web of Science); a família `ris (scopus)`, `ris (ebsco)` e `ris (standard)` (arquitetura de metadados bibliográficos padronizados por marcadores de duas letras mantidos por grandes consórcios editoriais, destacando-se as regras da Elsevier); e os esquemas `xmlpubmed`, `medline` e `xml (clinical trials)` (linguagens parametrizadas direcionadas especificamente às classificações sistêmicas de artigos e registros clínicos das ciências da saúde e biológicas)[cite: 166];
b) formatos de imprensa e raspagem web (*scraping*): englobam as variações `factiva`, `factiva with tags`, `factiva2` e `factivaxml` (estruturas originadas das frentes de indexação corporativa e jornalística controladas pela agência Dow Jones); o formato `europresse` (extração semântica exportável da base global de jornais integrados ao serviço Europresse); o padrão `reuters` (agrupamentos informativos da agência jornalística Reuters); e o formato `guardian` (mapeado pelas chaves abertas oriundas da API JSON do portal midiático *The Guardian*)[cite: 166];
c) formatos estruturados padrões: abrangem os dialetos `csv` e `robust csv` (conjuntos tabulares generalistas validados pelas classes de delimitadores e pelo `csv.Sniffer` nativo); o formato `xls` (planilhas extraídas do Microsoft Excel vinculadas diretamente à indexação pela biblioteca `xlrd`); a família `json`, `json (multiline)` e `jsons` (extrações semânticas aninhadas direcionadas a redes sociais e utilitários web como Spinn3r e Pytheas); o formato `tips` (campos e separadores voltados ao mapeamento analítico de patentes e propriedade industrial); e o padrão `SMS` (modelagem voltada ao processamento em cadeia de redes comunicativas móveis)[cite: 166];
d) formatos textuais livres e documentos: incluem as opções `txt` e `txt-paragraph` (leitura direta baseada em fatiamentos por sentenças ou pontuações orgânicas) e os formatos `pdf` e `docx` (submetidos a conversão forçada para texto plano via subprocessos externos encapsulados nas execuções do servidor)[cite: 166];
e) formatos tratados via serviços e contêineres externos: compreendem os padrões `istex` e `nbib` (cujo processamento é delegado a instâncias acessórias virtualizadas em contêineres Docker acionados pelo script principal)[cite: 166, 176].