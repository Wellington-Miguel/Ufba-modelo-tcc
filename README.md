# Framework para TCC UFBA (Markdown + LLM + abnTeX2)

Este repositório fornece uma infraestrutura moderna, ágil e reprodutível para a elaboração de **Trabalhos de Conclusão de Curso (TCC)**, **Dissertações** e **Teses** na **Universidade Federal da Bahia (UFBA)**.

Ele foi especialmente projetado para quem utiliza **Modelos de Linguagem (LLMs)** como ChatGPT, Claude ou Gemini para auxiliar na escrita científica, resolvendo a perda de contexto e a dificuldade de manter textos longos coerentes e diagramados nas normas da ABNT.

O projeto é baseado nas diretrizes oficiais do **Manual de Estilo Acadêmico da EDUFBA (6ª edição revista e ampliada, 2019)** e nas normas ABNT aplicáveis (NBR 14724, NBR 6023, NBR 10520, NBR 6024, NBR 6028).

---

## 📁 Estrutura do Repositório

```text
tcc-ufba/
├── content/                     # Blocos modulares em Markdown (escrita do trabalho)
│   ├── 01_introducao.md         # Capítulo 1: Introdução, objetivos e justificativa
│   ├── 02_revisao.md            # Capítulo 2: Revisão de literatura / Fundamentação
│   ├── 03_metodologia.md        # Capítulo 3: Metodologia e materiais
│   ├── 04_resultados.md         # Capítulo 4: Resultados e discussão
│   ├── 05_conclusao.md          # Capítulo 5: Considerações finais e trabalhos futuros
│   ├── apendice_a_modelo.md     # (Opcional) Apêndices elaborados pelo próprio autor
│   └── anexo_a_documento.md     # (Opcional) Anexos de documentos externos
├── images/                      # Pasta central de figuras e ilustrações
│   └── figura1.png              # Exemplos de imagens usadas no texto
├── metadata.yaml                # Metadados: título, autor, banca, resumo, siglas
├── references.bib               # Base de referências no formato BibTeX
├── build.py                     # Compilador inteligente em Python (MD -> LaTeX / PDF / Overleaf)
├── build.ps1                    # Script PowerShell para execução rápida no Windows
├── Makefile                     # Automação via make (Linux, Mac, WSL)
├── UFBA.sty                     # Pacote LaTeX customizado para a UFBA (Manual EDUFBA 2019)
├── abntex2.cls                  # Classe abnTeX2 oficial para documentos ABNT
├── logo_ufba.png                # Brasão oficial da UFBA em alta resolução (PNG)
├── logo_ufba.eps                # Brasão oficial da UFBA em vetor EPS
└── legacy_backup/               # Backup dos arquivos de exemplo do modelo legado
```

---

## 🤖 Como Trabalhar com a LLM em Blocos Modulares

### O Problema que o Framework Resolve
Ao pedir para uma LLM escrever um TCC inteiro de uma vez, ocorrem três problemas graves:
1. O texto fica superficial devido ao limite de saída da IA;
2. Há perda de coerência e esquecimento de partes anteriores (*lost-in-the-middle*);
3. O código LaTeX gerado por LLMs frequentemente contém erros de sintaxe ou comandos incompatíveis com o `abntex2`.

### A Solução deste Framework
1. **Escreva em Markdown**: A LLM gera Markdown com perfeição, sem alucinar comandos complexos do LaTeX;
2. **Trabalhe em Blocos**: Peça seção por seção (ex: primeiro o referencial teórico de um tema, depois a metodologia, etc.);
3. **Salve direto em `content/`**: Cole o texto gerado no arquivo correspondente (ou crie novos, como `02_1_conceitos.md`);
4. **Compile em 1 clique**: O script `build.py` converte tudo automaticamente para o `abntex2` da UFBA!

---

### 📋 Prompt Recomendado para Enviar à sua LLM

Copie e cole o seguinte comando como **Prompt de Sistema** ou no início da conversa com a sua LLM:

> "Você é um assistente especializado em redação acadêmica de nível superior para a Universidade Federal da Bahia (UFBA).
> Estamos escrevendo meu TCC em blocos modulares. Por favor, siga rigorosamente estas regras:
> 1. Responda estritamente em **Markdown**;
> 2. Use títulos de seções iniciando em nível 2 (`## Título da Seção`) ou nível 3 (`### Subseção`);
> 3. **Não numere os títulos manualmente** (ex: escreva `## Contextualização` e NUNCA `## 1.1 Contextualização`), pois o compilador numera automaticamente;
> 4. Use citações no formato BibTeX: `[@Chave2020]` para citações entre parênteses ou `Segundo @Chave2020` para citações no fluxo da frase;
> 5. Para **citações diretas longas** (mais de 3 linhas), use o bloco de citação `> texto da citação (AUTOR, ano, p. xx)`;
> 6. Para **figuras**, use `![Título da Figura](images/nome_do_arquivo.png)` seguido na linha seguinte por `*Fonte: Elaborado pelo autor (2026).*`;
> 7. Para **equações**, use `$f(x)$` para termos inline ou `$$ ... $$` para equações em bloco;
> 8. Mantenha linguagem acadêmica formal, impessoal e fundamentada."

---

## ✍️ Sintaxes Suportadas em Markdown

| Elemento | Sintaxe em Markdown | Resultado no LaTeX / ABNT |
| :--- | :--- | :--- |
| **Capítulo** | `# Título do Capítulo` | `\chapter{Título do Capítulo}` (Maiúsculo, negrito) |
| **Seção Secundária** | `## Seção Secundária` | `\section{Seção Secundária}` (Maiúsculo, redondo) |
| **Seção Terciária** | `### Seção Terciária` | `\subsection{Seção Terciária}` (Minúsculo, negrito) |
| **Citação Autor-Data** | `[@EDUFBA2019, p. 45]` | `\cite[p.~45]{EDUFBA2019}` $\rightarrow$ (LUBISCO; VIEIRA, 2019, p. 45) |
| **Citação no Texto** | `Segundo @Severino2016` | `Segundo \citeonline{Severino2016}` $\rightarrow$ Segundo Severino (2016) |
| **Citação Longa (> 3 linhas)** | `> Texto com mais de três linhas...` | `\begin{citacao} ... \end{citacao}` (Recuo 4cm, fonte 10/11, simples) |
| **Figura com Fonte** | `![Legenda](images/fig.png)`<br>`*Fonte: Autor (2026).*` | `\begin{figure}` com `\caption` em cima e `\legend{Fonte: ...}` embaixo |
| **Tabela** | Tabela em pipes (`\| Col \| ...`) | `\begin{table}` com linhas padronizadas e fonte |
| **Equação em Bloco** | `$$ E = mc^2 $$` | `\begin{equation} E = mc^2 \end{equation}` numerada à direita |
| **Referência Cruzada** | `Veja o [Capítulo 2](#sec:revisao)` | `Veja o \autoref{sec:revisao}` |

---

## ⚙️ Configuração dos Metadados (`metadata.yaml`)

Edite o arquivo `metadata.yaml` para configurar os dados da sua pesquisa:
- **Título e Subtítulo**: Título principal e subtítulo opcional;
- **Autor e Instituição**: Seu nome, Instituto/Faculdade, Colegiado/Programa e Curso;
- **Orientador(a) e Coorientador(a)**: Nome e gênero (`M` ou `F`) para ajustar automaticamente os rótulos;
- **Banca Examinadora**: Lista de professores para a Folha de Aprovação;
- **Dedicatória, Agradecimentos e Epígrafe**: Textos pré-textuais opcionais;
- **Resumo e Abstract**: Textos do resumo (150 a 500 palavras) e palavras-chave.
  - *Diferencial UFBA*: O sistema gera **automaticamente** a referência do próprio trabalho no cabeçalho do Resumo e Abstract conforme a NBR 6028 e o Manual EDUFBA (p. 56 e 64);
- **Siglas**: Dicionário de abreviaturas que é ordenado **alfabeticamente de forma automática**.

---

## 🚀 Como Compilar

Você tem total flexibilidade para compilar localmente ou no Overleaf.

### Opção 1: Overleaf (Zero Instalação - Mais Rápido)
Se você não deseja instalar compiladores LaTeX pesados no seu computador:
1. No terminal, execute:
   ```bash
   python build.py --zip
   ```
   *(ou `.\build.ps1 -Zip` no PowerShell, ou `make zip`)*
2. Um arquivo chamado **`tcc-ufba-overleaf.zip`** será gerado na pasta do projeto;
3. Acesse [Overleaf.com](https://www.overleaf.com/) (gratuito) e clique em **Novo Projeto** $\rightarrow$ **Carregar Projeto**;
4. Envie o arquivo `.zip` e clique em **Recompilar**. O PDF será gerado com perfeição!

---

### Opção 2: Compilação Local no Windows
Para compilar diretamente no seu Windows gerando `tcc.pdf` sem depender da internet:
1. Instale o MiKTeX pelo terminal (se ainda não tiver):
   ```powershell
   winget install MiKTeX.MiKTeX
   ```
2. Após reiniciar o terminal, basta rodar:
   ```powershell
   .\build.ps1
   ```
   *(ou `python build.py`)*
3. O arquivo `tcc.pdf` será gerado automaticamente.

---

### Opção 3: Gerar apenas o LaTeX (`main.tex`)
Para inspecionar o código LaTeX gerado antes de compilar:
```bash
python build.py --tex
```

### Limpeza de Arquivos Temporários
Para remover arquivos auxiliares (`.aux`, `.log`, `.toc`, etc.):
```bash
python build.py --clean
```

---

## 📚 Conformidade com o Manual EDUFBA (6ª edição, 2019)

| Regra do Manual EDUFBA | Onde está no Manual | Implementação no Framework |
| :--- | :--- | :--- |
| **Margens** | Quadro 5, p. 85 | Sup. 3cm, Esq. 3cm, Inf. 2cm, Dir. 2cm |
| **Recuo de Parágrafo** | Quadro 6, p. 85 | 1,0 cm na primeira linha; espaçamento 6pt entre parágrafos |
| **Espaçamento Entrelinhas** | Quadro 7, p. 86 | 1,5 no texto; Simples em citações longas, notas, referências e resumo |
| **Citações Longas (> 3 linhas)** | Item 4.2 b, p. 76 | Recuo de 4,0 cm da margem esquerda, fonte menor (11pt), sem aspas |
| **Referência no Resumo** | Item 3.2.1.8, p. 56 | Cabeçalho automático com a referência da monografia antes do texto |
| **Numeração Progressiva** | Item 7.1, p. 89-90 | 1 CAPÍTULO (negrito caixa alta), 1.1 SEÇÃO (redondo caixa alta), 1.1.1 Subseção (negrito) |
| **Ilustrações e Tabelas** | Itens 7.2 e 7.3, p. 90-93 | Título e número no topo; indicação de Fonte e notas no rodapé |
| **Referências** | NBR 6023:2018, p. 60 | Alinhadas à margem esquerda, espaçamento simples, ordenação alfabética |

---

## 💡 Dicas de Produtividade
- Para adicionar um novo capítulo, basta criar um arquivo como `content/06_discussao.md`. O script detecta a ordem alfabética dos nomes e insere no texto.
- Para adicionar apêndices (documentos feitos por você), crie `content/apendice_a_roteiro.md`.
- Para adicionar anexos (documentos externos), crie `content/anexo_a_estatuto.md`.
- Para adicionar figuras, salve o arquivo PNG ou JPG em `images/` e referencie no Markdown como `![Título da imagem](images/sua_foto.png)`.
