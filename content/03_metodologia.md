# Metodologia

Este capítulo descreve os procedimentos metodológicos empregados para construir a arquitetura do repositório, o esquema de dados para metadados e o mecanismo de compilação automatizada.

## Arquitetura do Repositório e Fluxo de Trabalho

A estrutura proposta organiza os artefatos do projeto em pastas com responsabilidades bem definidas, eliminando a poluição do diretório raiz e facilitando a manutenção contínua pelo estudante.

A Figura 1 ilustra o fluxo de dados entre o autor, a inteligência artificial generativa (LLM), os arquivos em Markdown e o pipeline de compilação.

![Fluxo de trabalho modular para elaboração de TCC com LLM e abnTeX2](images/figura1.png){#fig:fluxo_tcc}
*Fonte: Elaborado pelo autor (2026).*

O fluxo operacional obedece às seguintes etapas:

1. **Definição de Escopo**: O autor estrutura o sumário provisório do trabalho com base no Quadro Metodológico da UFBA [@EDUFBA2019, p. 37];
2. **Geração e Refinamento por LLM**: Para cada seção, solicita-se à LLM o desenvolvimento conceitual, recebendo a saída em formato Markdown com marcadores de citação;
3. **Depósito Modular**: Os arquivos são salvos na pasta `content/`, nomeados sequencialmente (ex: `01_introducao.md`, `02_revisao.md`);
4. **Alocação de Mídias e Referências**: Figuras são armazenadas em `images/` e entradas bibliográficas são registradas em `references.bib`;
5. **Compilação**: O script `build.py` converte os arquivos para LaTeX e compila o PDF final ou gera o pacote para envio ao Overleaf.

## Esquema de Metadados (`metadata.yaml`)

Para desacoplar as informações institucionais do código tipográfico, todos os dados de autoria, banca examinadora, resumos e siglas residem no arquivo `metadata.yaml`. 

A parametrização dos elementos pré-textuais permite a geração automática da referência bibliográfica no topo do resumo, conforme exigência do Manual EDUFBA [@EDUFBA2019, p. 56]:

$$R_{tcc} = \text{SOBRENOME}, \text{ P. } \text{Título do Trabalho}. \text{ Ano. f. Grau -- Unidade, UFBA, Cidade, Ano.}$$

## Tratamento de Citações e Equações

O pipeline de conversão oferece suporte a dois modos complementares de citação:

- **Sistema Autor-Data em Parênteses**: A marcação `[@EDUFBA2019, p. 41]` é mapeada para `\cite[p.~41]{EDUFBA2019}`, resultando em "(LUBISCO; VIEIRA, 2019, p. 41)";
- **Sistema Autor-Data no Fluxo da Sentença**: A marcação `@EDUFBA2019` é mapeada para `\citeonline{EDUFBA2019}`, produzindo "Lubisco e Vieira (2019)".

Equações matemáticas podem ser inseridas no formato inline utilizando cifrões simples `$f(x) = \sum_{i=1}^n x_i$` ou em blocos destacados com cifrões duplos:

$$f(x) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)$$

O compilador atribui automaticamente a numeração arábica alinhada à direita, em estrita conformidade com a ABNT.
