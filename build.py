#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BUILD SCRIPT: TCC UFBA (Markdown -> abnTeX2 -> PDF / Overleaf)
Conforme o Manual de Estilo Acadêmico da EDUFBA (6ª edição, 2019)
================================================================================
"""

import os
import sys
import re
import glob
import shutil
import zipfile
import subprocess
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def carregar_metadados(arquivo_yaml="metadata.yaml"):
    """Carrega metadados do arquivo YAML com tratamento de fallbacks."""
    if not os.path.exists(arquivo_yaml):
        print(f"[AVISO] Arquivo {arquivo_yaml} não encontrado. Usando padrões.")
        return {}

    if yaml is not None:
        with open(arquivo_yaml, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    else:
        # Fallback simples se PyYAML não estiver disponível
        print("[INFO] PyYAML não encontrado, utilizando parser básico.")
        meta = {}
        with open(arquivo_yaml, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
        return meta


def formatar_nome_referencia(nome_completo):
    """
    Formata o nome do autor para citação em referência ABNT.
    Ex: 'João Carlos da Silva' -> 'SILVA, J. C. da'
    """
    if not nome_completo:
        return "AUTOR, A."
    partes = nome_completo.strip().split()
    if len(partes) == 1:
        return partes[0].upper()
    
    sobrenome = partes[-1].upper()
    prenomes = partes[:-1]
    
    particulas = {"da", "de", "do", "das", "dos", "e"}
    iniciais = []
    for p in prenomes:
        if p.lower() in particulas:
            iniciais.append(p.lower())
        else:
            iniciais.append(f"{p[0].upper()}.")
    return f"{sobrenome}, {' '.join(iniciais)}"


def gerar_slug(texto):
    """Gera um identificador para label a partir de um título."""
    texto = texto.lower()
    subs = {
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a',
        'é': 'e', 'ê': 'e',
        'í': 'i',
        'ó': 'o', 'ô': 'o', 'õ': 'o',
        'ú': 'u', 'ü': 'u',
        'ç': 'c'
    }
    for orig, rep in subs.items():
        texto = texto.replace(orig, rep)
    texto = re.sub(r'[^a-z0-9_]+', '_', texto)
    return texto.strip('_')[:40]


class MarkdownToLatex:
    """Conversor robusto de blocos em Markdown para LaTeX no padrão abnTeX2/UFBA."""

    def __init__(self):
        self.figure_counter = 0
        self.table_counter = 0

    def escapar_caracteres_especiais(self, texto):
        """Escapa caracteres especiais do LaTeX fora de ambientes matemáticos e comandos."""
        partes = re.split(r'(\$.*?\$|\\begin\{.*?\}|\\end\{.*?\}|\\[a-zA-Z]+(?:\{.*?\})*)', texto)
        resultado = []
        for i, parte in enumerate(partes):
            if i % 2 == 1:
                # É código LaTeX ou math, não alterar
                resultado.append(parte)
            else:
                # Escapar %, &, _, # se não estiverem já precedidos de barra invertida
                p = re.sub(r'(?<!\\)%', r'\%', parte)
                p = re.sub(r'(?<!\\)&', r'\&', p)
                p = re.sub(r'(?<!\\)_', r'\_', p)
                p = re.sub(r'(?<!\\)#', r'\#', p)
                resultado.append(p)
        return "".join(resultado)

    def converter_formatacao_inline(self, linha):
        """Converte negrito, itálico, código, links e citações em uma linha."""
        # Math blocks protection
        math_tokens = []
        def salvar_math(match):
            math_tokens.append(match.group(0))
            return f"@@MATH_{len(math_tokens)-1}@@"

        linha = re.sub(r'\$.*?\$', salvar_math, linha)

        # Citações estilo Pandoc: [@Chave, p. 12] -> \cite[p.~12]{Chave}
        def repl_cite(match):
            corpo = match.group(1).strip()
            # Multiplas citações separadas por ponto e vírgula
            if ';' in corpo:
                itens = [c.strip().lstrip('@') for c in corpo.split(';')]
                return f"\\cite{{{', '.join(itens)}}}"
            # Citação única com página
            if ',' in corpo:
                partes = corpo.split(',', 1)
                chave = partes[0].strip().lstrip('@')
                pag = partes[1].strip()
                return f"\\cite[{pag}]{{{chave}}}"
            return f"\\cite{{{corpo.lstrip('@')}}}"

        linha = re.sub(r'\[(@[a-zA-Z0-9_\-:\.,\s;]+)\]', repl_cite, linha)

        # Citação no fluxo do texto: @Chave -> \citeonline{Chave}
        linha = re.sub(r'(?<![\\@\w])@([a-zA-Z0-9_\-:]+)', r'\\citeonline{\1}', linha)

        # Links Markdown com referência cruzada: [Texto](#sec:slug) -> \autoref{sec:slug}
        linha = re.sub(r'\[([^\]]+)\]\(#(sec:[^\)]+)\)', r'\\autoref{\2}', linha)
        linha = re.sub(r'\[([^\]]+)\]\(#(fig:[^\)]+)\)', r'\\autoref{\2}', linha)
        linha = re.sub(r'\[([^\]]+)\]\(#(tab:[^\)]+)\)', r'\\autoref{\2}', linha)

        # Links Markdown normais: [Texto](http...) -> \href{url}{Texto}
        linha = re.sub(r'\[([^\]]+)\]\((https?:\/\/[^\)]+)\)', r'\\href{\2}{\1}', linha)

        # Negrito: **texto** ou __texto__ -> \textbf{texto}
        linha = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', linha)
        linha = re.sub(r'__(.+?)__', r'\\textbf{\1}', linha)

        # Itálico: *texto* ou _texto_ -> \textit{texto}
        linha = re.sub(r'\*(.+?)\*', r'\\textit{\1}', linha)
        linha = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\\textit{\1}', linha)

        # Inline code: `codigo` -> \texttt{codigo}
        linha = re.sub(r'`([^`]+)`', r'\\texttt{\1}', linha)

        # Restaura math
        for idx, token in enumerate(math_tokens):
            linha = linha.replace(f"@@MATH_{idx}@@", token)

        return linha

    def converter(self, md_texto):
        """Converte o texto Markdown completo de um capítulo para código LaTeX."""
        linhas = md_texto.splitlines()
        latex_saida = []
        i = 0
        total_linhas = len(linhas)

        em_bloco_codigo = False
        linguagem_codigo = "text"
        bloco_codigo_buffer = []

        em_citacao_longa = False
        citacao_buffer = []

        em_lista_ul = False
        em_lista_ol = False

        while i < total_linhas:
            linha_raw = linhas[i]
            linha = linha_raw.strip()

            # --- 1. Blocos de Código (```) ---
            if linha.startswith("```"):
                if not em_bloco_codigo:
                    em_bloco_codigo = True
                    lang = linha.lstrip("`").strip()
                    linguagem_codigo = lang if lang else "text"
                    bloco_codigo_buffer = []
                else:
                    em_bloco_codigo = False
                    latex_saida.append(f"\\begin{{lstlisting}}[language={linguagem_codigo}]")
                    latex_saida.extend(bloco_codigo_buffer)
                    latex_saida.append("\\end{lstlisting}\n")
                i += 1
                continue

            if em_bloco_codigo:
                bloco_codigo_buffer.append(linha_raw)
                i += 1
                continue

            # --- 2. Citações Diretas Longas (bloco > ...) ---
            if linha.startswith(">"):
                texto_citacao = linha.lstrip("> ").strip()
                if not em_citacao_longa:
                    em_citacao_longa = True
                    citacao_buffer = [self.converter_formatacao_inline(texto_citacao)]
                else:
                    citacao_buffer.append(self.converter_formatacao_inline(texto_citacao))
                i += 1
                continue
            else:
                if em_citacao_longa:
                    em_citacao_longa = False
                    latex_saida.append("\\begin{citacao}")
                    latex_saida.append(" ".join(citacao_buffer))
                    latex_saida.append("\\end{citacao}\n")
                    citacao_buffer = []

            # --- 3. Fechamento de Listas se a linha atual não for item ---
            eh_item_ul = bool(re.match(r'^[\*\-]\s+', linha))
            eh_item_ol = bool(re.match(r'^\d+\.\s+', linha))

            if not eh_item_ul and em_lista_ul:
                latex_saida.append("\\end{itemize}\n")
                em_lista_ul = False

            if not eh_item_ol and em_lista_ol:
                latex_saida.append("\\end{enumerate}\n")
                em_lista_ol = False

            # --- 4. Linhas em branco ---
            if not linha:
                latex_saida.append("")
                i += 1
                continue

            # --- 5. Títulos e Seções (Numeração progressiva ABNT NBR 6024 / EDUFBA) ---
            m_header = re.match(r'^(#{1,6})\s+(.*)$', linha)
            if m_header:
                nivel = len(m_header.group(1))
                titulo = m_header.group(2).strip()

                # Remove numeração manual do título se fornecida pela LLM (ex: "1. Introdução" -> "Introdução")
                titulo_limpo = re.sub(r'^\d+(\.\d+)*\.?\s*', '', titulo).strip()
                slug = gerar_slug(titulo_limpo)

                if nivel == 1:
                    latex_saida.append(f"\\chapter{{{titulo_limpo}}}\\label{{sec:{slug}}}\n")
                elif nivel == 2:
                    latex_saida.append(f"\\section{{{titulo_limpo}}}\\label{{sec:{slug}}}\n")
                elif nivel == 3:
                    latex_saida.append(f"\\subsection{{{titulo_limpo}}}\\label{{sec:{slug}}}\n")
                elif nivel == 4:
                    latex_saida.append(f"\\subsubsection{{{titulo_limpo}}}\\label{{sec:{slug}}}\n")
                else:
                    latex_saida.append(f"\\subsubsubsection{{{titulo_limpo}}}\\label{{sec:{slug}}}\n")
                i += 1
                continue

            # --- 6. Equações em Bloco ($$...$$) ---
            if linha.startswith("$$"):
                eq_lines = [linha.replace("$$", "").strip()]
                if not (linha.endswith("$$") and len(linha) > 2):
                    i += 1
                    while i < total_linhas and not linhas[i].strip().endswith("$$"):
                        eq_lines.append(linhas[i].strip())
                        i += 1
                    if i < total_linhas:
                        eq_lines.append(linhas[i].strip().replace("$$", "").strip())
                latex_saida.append("\\begin{equation}")
                latex_saida.append("\n".join(eq_lines).strip())
                latex_saida.append("\\end{equation}\n")
                i += 1
                continue

            # --- 7. Imagens / Figuras (ABNT / EDUFBA: Título acima, Fonte abaixo) ---
            m_img = re.match(r'^!\[(.*?)\]\((.*?)\)(?:\{(.*?)\})?$', linha)
            if m_img:
                legenda = m_img.group(1).strip()
                caminho = m_img.group(2).strip()
                attrs = m_img.group(3) or ""

                # Normalizar caminho de imagem
                caminho = caminho.replace('\\', '/')

                # Verificar se a linha seguinte define a Fonte
                fonte = "Elaborado pelo autor (2026)."
                label = ""

                # Extrai atributos inline se fornecidos: {#fig:slug fonte="..." largura="0.8"}
                m_label = re.search(r'#([a-zA-Z0-9_\-:]+)', attrs)
                if m_label:
                    label = m_label.group(1)
                else:
                    self.figure_counter += 1
                    label = f"fig:{gerar_slug(legenda) or self.figure_counter}"

                m_fonte = re.search(r'fonte=["\'](.*?)["\']', attrs, re.IGNORECASE)
                if m_fonte:
                    fonte = m_fonte.group(1)

                m_largura = re.search(r'largura=["\'](.*?)["\']', attrs)
                largura = m_largura.group(1) if m_largura else "0.85"

                # Se a próxima linha contiver "*Fonte: ...*" ou "Fonte: ..."
                if i + 1 < total_linhas:
                    prox = linhas[i+1].strip()
                    m_prox_fonte = re.match(r'^\*?Fonte:\s*(.*?)\*?$', prox, re.IGNORECASE)
                    if m_prox_fonte:
                        fonte = m_prox_fonte.group(1).rstrip('*').strip()
                        i += 1 # consome a linha de fonte

                latex_saida.append("\\begin{figure}[htb]")
                latex_saida.append(f"  \\caption{{{legenda}}}")
                latex_saida.append(f"  \\label{{{label}}}")
                latex_saida.append("  \\begin{center}")
                latex_saida.append(f"    \\includegraphics[width={largura}\\textwidth]{{{caminho}}}")
                latex_saida.append("  \\end{center}")
                latex_saida.append(f"  \\legend{{Fonte: {fonte}}}")
                latex_saida.append("\\end{figure}\n")
                i += 1
                continue

            # --- 8. Tabelas em Markdown ---
            if linha.startswith("|") and linha.endswith("|"):
                tabela_linhas = [linha]
                i += 1
                while i < total_linhas and linhas[i].strip().startswith("|") and linhas[i].strip().endswith("|"):
                    tabela_linhas.append(linhas[i].strip())
                    i += 1

                # Verifica se a linha seguinte é fonte
                fonte_tab = "Dados da pesquisa (2026)."
                if i < total_linhas:
                    prox = linhas[i].strip()
                    m_tab_fonte = re.match(r'^\*?Fonte:\s*(.*?)\*?$', prox, re.IGNORECASE)
                    if m_tab_fonte:
                        fonte_tab = m_tab_fonte.group(1).rstrip('*').strip()
                        i += 1

                self.table_counter += 1
                tab_latex = self._converter_tabela(tabela_linhas, f"Tabela descritiva {self.table_counter}", f"tab:tabela_{self.table_counter}", fonte_tab)
                latex_saida.append(tab_latex)
                continue

            # --- 9. Listas não ordenadas ---
            if eh_item_ul:
                if not em_lista_ul:
                    latex_saida.append("\\begin{itemize}")
                    em_lista_ul = True
                item_txt = re.sub(r'^[\*\-]\s+', '', linha)
                latex_saida.append(f"  \\item {self.converter_formatacao_inline(item_txt)}")
                i += 1
                continue

            # --- 10. Listas numeradas ---
            if eh_item_ol:
                if not em_lista_ol:
                    latex_saida.append("\\begin{enumerate}")
                    em_lista_ol = True
                item_txt = re.sub(r'^\d+\.\s+', '', linha)
                latex_saida.append(f"  \\item {self.converter_formatacao_inline(item_txt)}")
                i += 1
                continue

            # --- 11. Parágrafo comum ---
            linha_formatada = self.converter_formatacao_inline(linha)
            latex_saida.append(linha_formatada)
            i += 1

        # Fecha listas residuais se o arquivo terminar em lista
        if em_lista_ul:
            latex_saida.append("\\end{itemize}\n")
        if em_lista_ol:
            latex_saida.append("\\end{enumerate}\n")
        if em_citacao_longa:
            latex_saida.append("\\begin{citacao}")
            latex_saida.append(" ".join(citacao_buffer))
            latex_saida.append("\\end{citacao}\n")

        return "\n".join(latex_saida)

    def _converter_tabela(self, linhas, titulo, label, fonte):
        """Converte matriz de linhas Markdown para ambiente table do LaTeX."""
        if len(linhas) < 2:
            return ""

        # Cabeçalho
        cols_cabecalho = [c.strip() for c in linhas[0].strip('|').split('|')]
        num_cols = len(cols_cabecalho)
        alinhamento = "l" * num_cols

        # Linhas de dados (ignorando a linha divisória |---|---|)
        linhas_dados = []
        for l in linhas[1:]:
            if re.match(r'^[\|\s\:\-]+$', l):
                continue
            cols = [c.strip() for c in l.strip('|').split('|')]
            linhas_dados.append(cols)

        latex = []
        latex.append("\\begin{table}[htb]")
        latex.append(f"  \\caption{{{titulo}}}")
        latex.append(f"  \\label{{{label}}}")
        latex.append("  \\begin{center}")
        latex.append(f"  \\begin{{tabular}}{{{'|' + '|'.join(['l'] * num_cols) + '|'}}}")
        latex.append("    \\hline")
        
        # Header row com negrito
        header_tex = " & ".join([f"\\textbf{{{self.converter_formatacao_inline(c)}}}" for c in cols_cabecalho])
        latex.append(f"    {header_tex} \\\\ \\hline")

        # Dados
        for row in linhas_dados:
            row_tex = " & ".join([self.converter_formatacao_inline(c) for c in row])
            latex.append(f"    {row_tex} \\\\ \\hline")

        latex.append("  \\end{tabular}")
        latex.append("  \\end{center}")
        latex.append(f"  \\legend{{Fonte: {fonte}}}")
        latex.append("\\end{table}\n")
        return "\n".join(latex)


def gerar_latex_mestre(metadata, capitulos_tex, apendices_tex, anexos_tex):
    """Gera o arquivo LaTeX principal (main.tex) estruturado segundo as normas da UFBA."""

    titulo = metadata.get("titulo", "Título do Trabalho")
    subtitulo = metadata.get("subtitulo", "")
    autor = metadata.get("autor", "Nome do Autor")
    instituicao = metadata.get("instituicao", "Universidade Federal da Bahia")
    faculdade = metadata.get("faculdade", "Instituto de Computação")
    programa = metadata.get("programa", "Colegiado do Curso de Ciência da Computação")
    curso = metadata.get("curso", "Ciência da Computação")
    grau = metadata.get("grau", "Bacharel em Ciência da Computação")
    tipotrabalho = metadata.get("tipotrabalho", "Trabalho de Conclusão de Curso")
    cidade = metadata.get("local", "Salvador")
    ano = str(metadata.get("ano", "2026"))
    data_str = str(metadata.get("data", ano))

    # Orientador(a)
    orientador = metadata.get("orientador", {})
    nome_orientador = orientador.get("nome", "Prof. Dr. Orientador")
    genero_orientador = orientador.get("genero", "M").upper()

    # Coorientador(a)
    coorientador = metadata.get("coorientador", {})
    nome_coorientador = coorientador.get("nome", "")
    genero_coorientador = coorientador.get("genero", "M").upper()

    # Preâmbulo padrão
    preambulo = metadata.get("preambulo_customizado", "")
    if not preambulo:
        preambulo = (
            f"{tipotrabalho} apresentado ao {programa} da "
            f"{instituicao}, como requisito para obtenção do grau de {grau}."
        )

    # Referência própria para cabeçalho do Resumo (exigência EDUFBA p. 56)
    ref_autor = formatar_nome_referencia(autor)
    subtitulo_ref = f": {subtitulo}" if subtitulo else ""
    ref_trabalho = (
        f"{ref_autor}. \\textbf{{{titulo}{subtitulo_ref}}}. {ano}. "
        f"\\pageref{{LastPage}} f. {tipotrabalho} ({grau}) -- {faculdade}, "
        f"{instituicao}, {cidade}, {ano}."
    )

    # Início do documento
    tex = []
    tex.append(r"""\documentclass[
	oneside,
	a4paper,
	12pt,
	chapter=TITLE,
	section=TITLE
]{abntex2}

% --- PACOTES BÁSICOS ---
\usepackage{UFBA}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{lastpage}
\usepackage{indentfirst}
\usepackage{color}
\usepackage{graphicx}
\usepackage{float}
\usepackage{microtype}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{listings}
\usepackage{pdfpages}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{hyperref}

% --- SISTEMA DE CITAÇÕES ABNT (NBR 6023:2018 / NBR 10520) ---
\usepackage[
	alf,
	abnt-emphasize=bf,
	abnt-thesis-year=both,
	abnt-repeated-author-omit=yes,
	abnt-last-names=abnt,
	abnt-etal-cite,
	abnt-etal-list=3,
	abnt-etal-text=default,
	abnt-and-type=e,
	abnt-doi=doi,
	abnt-url-package=none,
	bibjustif
]{abntex2cite}

% --- CONFIGURAÇÕES DE CÓDIGO (Listings) ---
\lstset{
	basicstyle=\ttfamily\footnotesize,
	breaklines=true,
	frame=single,
	tabsize=2,
	showstringspaces=false
}

% --- MARGENS DO MANUAL EDUFBA (Quadro 5, p. 85: Sup. 3cm, Esq. 3cm, Inf. 2cm, Dir. 2cm) ---
\setlrmarginsandblock{3cm}{2cm}{*}
\setulmarginsandblock{3cm}{2cm}{*}
\checkandfixthelayout

% --- ESPAÇAMENTOS DO MANUAL EDUFBA ---
\OnehalfSpacing
\setlength{\parindent}{1.0cm}
\setlength{\parskip}{6pt}

% --- NOMES DE ITENS ---
\renewcommand{\figureautorefname}{Figura}
\renewcommand{\tableautorefname}{Tabela}
\renewcommand{\chapterautorefname}{Capítulo}
\renewcommand{\sectionautorefname}{Seção}

% --- DADOS INSTITUCIONAIS ---
""")

    tex.append(f"\\titulo{{{titulo}}}")
    if subtitulo:
        tex.append(f"\\subtitulo{{{subtitulo}}}")
    tex.append(f"\\autor{{{autor}}}")
    tex.append(f"\\local{{{cidade}}}")
    tex.append(f"\\data{{{data_str}}}")
    tex.append(f"\\instituicao{{{instituicao}}}")
    tex.append(f"\\faculdade{{{faculdade}}}")
    tex.append(f"\\programa{{{programa}}}")
    tex.append(f"\\tipotrabalho{{{tipotrabalho}}}")
    tex.append(f"\\preambulo{{{preambulo}}}")

    if genero_orientador == "F":
        tex.append(f"\\orientadora{{{nome_orientador}}}")
    else:
        tex.append(f"\\orientador{{{nome_orientador}}}")

    if nome_coorientador:
        if genero_coorientador == "F":
            tex.append(f"\\coorientadora{{{nome_coorientador}}}")
        else:
            tex.append(f"\\coorientador{{{nome_coorientador}}}")

    tex.append(r"""
% --- CONFIGURAÇÃO DO PDF ---
\hypersetup{
	colorlinks=true,
	linkcolor=black,
	citecolor=black,
	filecolor=black,
	urlcolor=black,
	pdfauthor=""" + f"{{{autor}}}" + r""",
	pdftitle=""" + f"{{{titulo}}}" + r""",
	pdfsubject=""" + f"{{{tipotrabalho}}}" + r""",
	pdfcreator={Python TCC-UFBA Markdown Builder}
}

% --- INÍCIO DO DOCUMENTO ---
\begin{document}
\frenchspacing
\selectlanguage{brazil}

% ==============================================================================
% ELEMENTOS PRÉ-TEXTUAIS
% ==============================================================================

\imprimircapa
\imprimirfolhaderosto
""")

    # Ficha catalográfica
    ficha = metadata.get("ficha_catalografica", {})
    if ficha.get("inserir", False) and os.path.exists(ficha.get("arquivo", "ficha.pdf")):
        tex.append("% Ficha Catalográfica (SIBI/UFBA)\n\\includepdf{" + ficha.get("arquivo", "ficha.pdf") + "}\n")

    # Folha de aprovação
    aprov = metadata.get("folha_aprovacao", {})
    if aprov.get("inserir", True):
        data_aprov = aprov.get("data_aprovacao", f"xx de mês de {ano}")
        tex.append(r"""
% --- FOLHA DE APROVAÇÃO (Manual EDUFBA p. 49, 52) ---
\begin{folhadeaprovacao}
  \begin{center}
    {\fontsize{14}{16}\selectfont\bfseries\MakeUppercase{\imprimirautor}\par}
    \vspace{1.5cm}
    {\fontsize{16}{18}\selectfont\bfseries\MakeUppercase{\imprimirtitulo}\par}
  \end{center}
  \vspace{1cm}
  \begin{flushright}
    \begin{minipage}{0.55\textwidth}
      \SingleSpacing\fontsize{11}{13}\selectfont
      \imprimirpreambulo
    \end{minipage}
  \end{flushright}
  \vspace{1cm}
  \noindent Trabalho aprovado. """ + f"{cidade}, {data_aprov}." + r"""
  \vspace{0.8cm}
  \begin{center}
    \bfseries Banca Examinadora
  \end{center}
""")
        banca = aprov.get("banca", [])
        if not banca:
            banca = [{"nome": nome_orientador, "papel": "Orientador", "instituicao": instituicao}]
        for membro in banca:
            m_nome = membro.get("nome", "")
            m_papel = membro.get("papel", "Examinador")
            m_inst = membro.get("instituicao", instituicao)
            tex.append(f"  \\assinatura{{\\textbf{{{m_nome}}} \\\\ {m_papel} -- {m_inst}}}")
        tex.append(r"\end{folhadeaprovacao}" + "\n")

    # Dedicatória
    dedicatoria = metadata.get("dedicatoria", "").strip()
    if dedicatoria:
        tex.append(r"""
% --- DEDICATÓRIA ---
\begin{dedicatoria}
  \vspace*{\fill}
  \begin{flushright}
    \noindent\textit{""" + dedicatoria.replace('\n', '\\\\\n') + r"""}
  \end{flushright}
  \vspace*{2cm}
\end{dedicatoria}
""")

    # Agradecimentos
    agradecimentos = metadata.get("agradecimentos", "").strip()
    if agradecimentos:
        tex.append(r"""
% --- AGRADECIMENTOS ---
\begin{agradecimentos}
""" + agradecimentos + r"""
\end{agradecimentos}
""")

    # Epígrafe
    epigrafe = metadata.get("epigrafe", {})
    if epigrafe and epigrafe.get("texto"):
        ep_texto = epigrafe.get("texto", "").strip()
        ep_autor = epigrafe.get("autor", "").strip()
        tex.append(r"""
% --- EPÍGRAFE ---
\begin{epigrafe}
  \vspace*{\fill}
  \begin{flushright}
    \textit{""" + f"``{ep_texto}''" + r"""}\\
    \vspace{0.5cm}
    """ + ep_autor + r"""
  \end{flushright}
  \vspace*{2cm}
\end{epigrafe}
""")

    # Resumo em Português
    resumo = metadata.get("resumo", "").strip()
    palavras_chave = metadata.get("palavras_chave", [])
    if resumo:
        kw_str = ". ".join(palavras_chave) + "." if palavras_chave else ""
        tex.append(r"""
% --- RESUMO (Manual EDUFBA p. 56 e 64: antecedido da referência do trabalho) ---
\setlength{\absparsep}{0pt}
\begin{resumo}
  \SingleSpacing
  \noindent """ + ref_trabalho + r"""
  \vspace{0.6cm}

  \noindent """ + resumo + r"""

  \vspace{0.5cm}
  \noindent\textbf{Palavras-chave}: """ + kw_str + r"""
\end{resumo}
""")

    # Abstract em Inglês
    abstract = metadata.get("abstract", "").strip()
    keywords = metadata.get("keywords", [])
    if abstract:
        kw_en_str = ". ".join(keywords) + "." if keywords else ""
        ref_trabalho_en = (
            f"{ref_autor}. \\textbf{{{titulo}{subtitulo_ref}}}. {ano}. "
            f"\\pageref{{LastPage}} p. Final Graduation Project ({grau}) -- {faculdade}, "
            f"{instituicao}, {cidade}, {ano}."
        )
        tex.append(r"""
% --- ABSTRACT ---
\begin{resumo}[Abstract]
  \SingleSpacing
  \noindent """ + ref_trabalho_en + r"""
  \vspace{0.6cm}

  \noindent """ + abstract + r"""

  \vspace{0.5cm}
  \noindent\textbf{Keywords}: """ + kw_en_str + r"""
\end{resumo}
""")

    # Listas
    listas = metadata.get("listas", {})
    if listas.get("figuras", True):
        tex.append(r"""
\pdfbookmark[0]{\listfigurename}{lof}
\listoffigures*
\cleardoublepage
""")
    if listas.get("tabelas", True):
        tex.append(r"""
\pdfbookmark[0]{\listtablename}{lot}
\listoftables*
\cleardoublepage
""")

    # Siglas
    siglas = metadata.get("siglas", {})
    if listas.get("siglas", True) and siglas:
        tex.append(r"""
% --- LISTA DE ABREVIATURAS E SIGLAS ---
\begin{siglas}
""")
        for sigla in sorted(siglas.keys()):
            expansao = siglas[sigla]
            tex.append(f"  \\item[{sigla}]\\quad {expansao}")
        tex.append(r"""\end{siglas}
\cleardoublepage
""")

    # Sumário
    tex.append(r"""
% --- SUMÁRIO (Manual EDUFBA p. 57, 69) ---
\pdfbookmark[0]{\contentsname}{toc}
\tableofcontents*
\cleardoublepage

% ==============================================================================
% ELEMENTOS TEXTUAIS
% ==============================================================================
\textual
""")

    # Inclusão dos capítulos
    for c_tex in capitulos_tex:
        tex.append(f"\n% --- {c_tex['nome']} ---")
        tex.append(c_tex['conteudo'])

    # Elementos pós-textuais
    tex.append(r"""
% ==============================================================================
% ELEMENTOS PÓS-TEXTUAIS
% ==============================================================================
\postextual

% --- REFERÊNCIAS BIBLIOGRÁFICAS (NBR 6023:2018) ---
\bibliography{references}
""")

    # Apêndices (se houver)
    if apendices_tex:
        tex.append(r"""
\begin{apendicesenv}
\partapendices
""")
        for ap in apendices_tex:
            tex.append(ap['conteudo'])
        tex.append(r"""\end{apendicesenv}""")

    # Anexos (se houver)
    if anexos_tex:
        tex.append(r"""
\begin{anexosenv}
\partanexos
""")
        for an in anexos_tex:
            tex.append(an['conteudo'])
        tex.append(r"""\end{anexosenv}""")

    tex.append(r"\end{document}" + "\n")

    return "\n".join(tex)


def executar_pipeline(apenas_tex=False, criar_zip=False, apenas_limpar=False):
    """Executa a leitura dos arquivos Markdown, compilação de TeX e criação do PDF/ZIP."""
    diretorio_raiz = Path(".")
    pasta_content = diretorio_raiz / "content"
    pasta_images = diretorio_raiz / "images"

    if apenas_limpar:
        limpar_arquivos_intermediarios()
        return

    print("================================================================================")
    print(" Compilador TCC UFBA - Markdown -> abnTeX2 (Manual EDUFBA 2019)")
    print("================================================================================")

    # 1. Carregar metadados
    print("[1/5] Carregando metadados de metadata.yaml...")
    metadata = carregar_metadados("metadata.yaml")

    # 2. Localizar arquivos Markdown em content/
    md_files = sorted(pasta_content.glob("*.md"))
    if not md_files:
        print("[ERRO] Nenhum arquivo Markdown (.md) encontrado na pasta content/!")
        return

    print(f"[2/5] Processando {len(md_files)} arquivos Markdown em content/...")
    converter = MarkdownToLatex()

    capitulos_tex = []
    apendices_tex = []
    anexos_tex = []

    for f_md in md_files:
        nome_arquivo = f_md.name
        with open(f_md, "r", encoding="utf-8") as f:
            conteudo_md = f.read()

        conteudo_tex = converter.converter(conteudo_md)
        item = {"nome": nome_arquivo, "conteudo": conteudo_tex}

        if nome_arquivo.lower().startswith("apendice"):
            apendices_tex.append(item)
            print(f"  -> Apêndice: {nome_arquivo}")
        elif nome_arquivo.lower().startswith("anexo"):
            anexos_tex.append(item)
            print(f"  -> Anexo: {nome_arquivo}")
        else:
            capitulos_tex.append(item)
            print(f"  -> Capítulo: {nome_arquivo}")

    # 3. Gerar main.tex
    print("[3/5] Gerando arquivo LaTeX mestre (main.tex)...")
    main_tex_content = gerar_latex_mestre(metadata, capitulos_tex, apendices_tex, anexos_tex)

    with open("main.tex", "w", encoding="utf-8") as f:
        f.write(main_tex_content)
    print("  -> main.tex gerado com sucesso!")

    if apenas_tex:
        print("\n[SUCESSO] Código LaTeX gerado em main.tex.")
        return

    zip_gerado = False
    if criar_zip:
        gerar_pacote_overleaf()
        zip_gerado = True

    # 5. Tentativa de compilação PDF local
    print("[4/5] Verificando compiladores LaTeX locais...")
    compilador_encontrado = verificar_compilador_latex()

    if compilador_encontrado:
        print(f"  -> Compilador detectado: {compilador_encontrado}. Compilando PDF...")
        compilar_pdf(compilador_encontrado)
    else:
        print("\n[INFO] Compilador LaTeX local (pdflatex/latexmk) não encontrado no PATH.")
        if not zip_gerado:
            print("  -> Criando pacote Overleaf automático 'tcc-ufba-overleaf.zip'...")
            gerar_pacote_overleaf()

        print("\n" + "="*80)
        print(" COMO OBTER SEU PDF IMEDIATAMENTE:")
        print(" 1. Acesse o Overleaf (https://www.overleaf.com/) - gratuito")
        print(" 2. Clique em 'Novo Projeto' -> 'Carregar Projeto'")
        print(" 3. Selecione o arquivo 'tcc-ufba-overleaf.zip' gerado nesta pasta.")
        print(" 4. Clique em Recompilar. O PDF do seu TCC será gerado perfeitamente!")
        print(" OU:")
        print(" Para compilar localmente no Windows, instale o MiKTeX:")
        print("    winget install MiKTeX.MiKTeX")
        print("="*80)


def gerar_pacote_overleaf(nome_zip="tcc-ufba-overleaf.zip"):
    """Compacta todos os arquivos necessários para compilação direta no Overleaf."""
    arquivos_essenciais = [
        "main.tex",
        "UFBA.sty",
        "abntex2.cls",
        "references.bib",
        "logo_ufba.png",
        "logo_ufba.eps",
        "ficha.pdf"
    ]

    with zipfile.ZipFile(nome_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos_essenciais:
            if os.path.exists(arq):
                zipf.write(arq, arcname=arq)
                print(f"     + Arquivo adicionado: {arq}")

        # Adiciona imagens
        if os.path.exists("images"):
            for img in glob.glob("images/*"):
                if os.path.isfile(img):
                    zipf.write(img, arcname=img)
                    print(f"     + Imagem adicionada: {img}")

    print(f"[ZIP] Pacote Overleaf criado com sucesso: {nome_zip}")


def verificar_compilador_latex():
    """Verifica se há compiladores LaTeX instalados."""
    for cmd in ["latexmk", "pdflatex", "xelatex"]:
        if shutil.which(cmd):
            return cmd
    return None


def compilar_pdf(engine="pdflatex"):
    """Compila o arquivo main.tex para PDF chamando o compilador."""
    try:
        if engine == "latexmk":
            cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "main.tex"]
            subprocess.run(cmd, check=True)
        else:
            # Ciclo completo de compilação com BibTeX
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], check=True)
            subprocess.run(["bibtex", "main"], check=False)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], check=True)
            subprocess.run(["pdflatex", "-interaction=nonstopmode", "main.tex"], check=True)

        if os.path.exists("main.pdf"):
            shutil.copy2("main.pdf", "tcc.pdf")
            print("[SUCESSO] PDF gerado com sucesso: tcc.pdf")
    except Exception as e:
        print(f"[ERRO] Falha durante a compilação do LaTeX: {e}")


def limpar_arquivos_intermediarios():
    """Remove arquivos temporários gerados pelo LaTeX."""
    extensoes = [
        "*.aux", "*.bbl", "*.blg", "*.log", "*.toc",
        "*.lof", "*.lot", "*.out", "*.idx", "*.ind",
        "*.ilg", "*.brf", "*.fls", "*.fdb_latexmk", "*.synctex.gz"
    ]
    removidos = 0
    for ext in extensoes:
        for f in glob.glob(ext):
            try:
                os.remove(f)
                removidos += 1
            except OSError:
                pass
    print(f"[LIMPEZA] {removidos} arquivos temporários foram excluídos.")


def main():
    parser = argparse.ArgumentParser(description="Compilador TCC UFBA (Markdown -> abnTeX2)")
    parser.add_argument("--tex", action="store_true", help="Gera apenas o código LaTeX (main.tex)")
    parser.add_argument("--pdf", action="store_true", help="Compila para PDF localmente")
    parser.add_argument("--zip", action="store_true", help="Gera pacote ZIP pronto para Overleaf")
    parser.add_argument("--clean", action="store_true", help="Limpa arquivos intermediários do LaTeX")
    args = parser.parse_args()

    executar_pipeline(
        apenas_tex=args.tex,
        criar_zip=args.zip,
        apenas_limpar=args.clean
    )


if __name__ == "__main__":
    main()
