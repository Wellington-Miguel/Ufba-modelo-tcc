# Introdução

A produção de um Trabalho de Conclusão de Curso (TCC) representa uma etapa determinante na formação acadêmica do estudante de graduação, congregando competências de investigação, síntese bibliográfica e aplicação prática do método científico. No âmbito da Universidade Federal da Bahia (UFBA), os trabalhos acadêmicos devem atender aos critérios estabelecidos no Manual de Estilo Acadêmico da EDUFBA [@EDUFBA2019], o qual harmoniza as diretrizes da Associação Brasileira de Normas Técnicas, em especial as normas ABNT NBR 14724 [@NBR14724:2011] e ABNT NBR 6023 [@NBR6023:2018].

Nos últimos anos, a emergência de modelos avançados de inteligência artificial generativa, especialmente os Modelos de Linguagem de Grande Porte (LLMs), inaugurou novas formas de cocriação e assistência à redação científica [@Brown2020]. Não obstante, a utilização dessas tecnologias apresenta desafios quanto à manutenção da coerência global em textos extensos e à formatação automatizada segundo padrões institucionais específicos.

## Contextualização e Motivação

Quando se redige um trabalho acadêmico de grande porte com auxílio de uma LLM, um problema recorrente decorre do tamanho da janela de contexto e da tendência do modelo em dispersar argumentos ou truncar respostas longas. Para contornar essa restrição, a estratégia recomendada consiste em trabalhar em blocos modulares independentes, submetendo e refinando capítulos e seções sequencialmente.

Contudo, a conversão manual desses blocos em Markdown para a sintaxe do LaTeX ou do abnTeX2 costuma ser laboriosa e propensa a erros de formatação. Como destacam Lubisco e Vieira [@EDUFBA2019, p. 29], o rigor formal não deve ser um obstáculo à produção intelectual, mas um facilitador da comunicação científica:

> A urgência na mudança desse estado de coisas se faz sentir, já que o uso de metodologias mais dinâmicas de ensino sugere a necessidade de que o estudante – quer de graduação, quer de pós-graduação – seja capacitado a transitar de forma autônoma no universo informacional, buscando, selecionando e sistematizando as informações de sua área de interesse. [@EDUFBA2019, p. 29]

Dessa forma, surge a oportunidade de conceber um ecossistema no qual o pesquisador escreva em Markdown de forma modular e um compilador cuide de toda a conformidade formal da UFBA.

## Problema de Pesquisa

Diante do cenário exposto, formula-se a seguinte questão norteadora: *Como viabilizar um fluxo de escrita acadêmica modular assistido por inteligência artificial que mantenha a coerência temática e garanta automaticamente a conformidade com as normas ABNT adotadas pela UFBA?*

## Objetivos

### Objetivo Geral

Desenvolver e estruturar uma base de projeto reprodutível para trabalhos de conclusão de curso na UFBA, baseada em escrita modular em Markdown e compilação automatizada para abnTeX2.

### Objetivos Específicos

- Mapear os requisitos de apresentação gráfica, numeração progressiva e elementos pré-textuais da 6ª edição do Manual da EDUFBA [@EDUFBA2019];
- Projetar uma estrutura de pastas e metadados (`metadata.yaml`) que centralize as informações institucionais do trabalho;
- Desenvolver um pipeline de compilação em Python capaz de converter blocos em Markdown, tabelas, figuras e citações para código LaTeX padronizado;
- Validar o fluxo de trabalho simulando a integração com saídas fornecidas por LLMs.

## Organização do Trabalho

O presente documento encontra-se estruturado em cinco capítulos principais. Este primeiro capítulo contextualizou a problemática e delimitou os objetivos da pesquisa. O [Capítulo 2](#sec:revisao_de_literatura) aborda a fundamentação teórica, discutindo a arquitetura de modelos de linguagem e os requisitos normativos da ABNT/UFBA. O [Capítulo 3](#sec:metodologia) descreve a metodologia e a arquitetura do compilador desenvolvido. O [Capítulo 4](#sec:resultados_e_discussao) apresenta os resultados obtidos e a validação do pipeline. Por fim, o [Capítulo 5](#sec:conclusao) sintetiza as conclusões e aponta direções para trabalhos futuros.
