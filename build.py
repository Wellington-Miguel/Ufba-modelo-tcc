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


def parse_yaml_fallback(text):
    """
    Parser YAML leve embutido para ambientes sem a biblioteca PyYAML.
    Suporta dicionários aninhados, listas, literais escalares e blocos multilinhas (|).
    """
    lines = text.splitlines()

    def parse_scalar(val):
        val = val.strip()
        if not val:
            return ""
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            return val[1:-1]
        if val.lower() == 'true':
            return True
        if val.lower() == 'false':
            return False
        if val.lower() in ('null', '~'):
            return None
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                return val

    def parse_block(start_idx, min_indent):
        result = None
        i = start_idx
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                i += 1
                continue

            indent = len(line) - len(line.lstrip(' '))
            if indent < min_indent:
                break

            # Item de lista (- ...)
            if stripped.startswith('- '):
                if result is None:
                    result = []
                elif not isinstance(result, list):
                    break

                content = stripped[2:].strip()
                if ':' in content:
                    k, v = content.split(':', 1)
                    item_dict = {k.strip(): parse_scalar(v)}
                    sub_dict, next_i = parse_block(i + 1, indent + 2)
                    if isinstance(sub_dict, dict):
                        item_dict.update(sub_dict)
                        i = next_i
                    else:
                        i += 1
                    result.append(item_dict)
                    continue
                else:
                    result.append(parse_scalar(content))
                    i += 1
                    continue

            # Par chave-valor ou início de bloco mapeado
            if ':' in stripped:
                if result is None:
                    result = {}
                elif not isinstance(result, dict):
                    break

                k, v = stripped.split(':', 1)
                k = k.strip()
                v = v.strip()

                if v == '|':
                    # Bloco multilinha com preservação de formatação
                    block_lines = []
                    i += 1
                    block_indent = None
                    while i < len(lines):
                        bline = lines[i]
                        bstripped = bline.strip()
                        if not bstripped:
                            block_lines.append('')
                            i += 1
                            continue
                        bindent = len(bline) - len(bline.lstrip(' '))
                        if block_indent is None:
                            if bindent <= indent:
                                break
                            block_indent = bindent
                        elif bindent < block_indent:
                            break
                        block_lines.append(bline[block_indent:])
                        i += 1
                    while block_lines and block_lines[-1] == '':
                        block_lines.pop()
                    result[k] = '\n'.join(block_lines) + '\n'
                    continue
                elif v == '':
                    # Objeto aninhado ou lista subsequente
                    sub_val, next_i = parse_block(i + 1, indent + 1)
                    result[k] = sub_val if sub_val is not None else {}
                    i = next_i
                    continue
                else:
                    result[k] = parse_scalar(v)
                    i += 1
                    continue
            else:
                i += 1
        return result, i

    res, _ = parse_block(0, 0)
    return res or {}


def carregar_metadados(arquivo_yaml="metadata.yaml"):
    """Carrega metadados do arquivo YAML com tratamento de fallbacks."""
    if not os.path.exists(arquivo_yaml):
        print(f"[AVISO] Arquivo {arquivo_yaml} não encontrado. Usando padrões.")
        return {}

    with open(arquivo_yaml, "r", encoding="utf-8") as f:
        conteudo = f.read()

    if yaml is not None:
        try:
            return yaml.safe_load(conteudo) or {}
        except Exception as e:
            print(f"[AVISO] Erro no PyYAML ({e}), utilizando parser embutido.")

    print("[INFO] PyYAML não encontrado, utilizando parser básico embutido.")
    return parse_yaml_fallback(conteudo)


def formatar_nome_referencia(nome_completo):
    """
    Formata o nome do autor para citação em referência ABNT.
    Ex: 'João Carlos da Silva' -> 'SILVA, J. C. da'
    """
    if not nome_completo:
        return "AUTOR, A."
    if "Wellington Miguel de Jesus Silva" in nome_completo:
        return "SILVA, W. M. de J. S."
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
    res = f"{sobrenome}, {' '.join(iniciais)}"
    res = re.sub(r'\.\.+', '.', res)
    return res


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
        if not texto:
            return ""
        # Remove eventuais marcadores de citação gerados por LLMs
        texto = re.sub(r'\[cite:\s*[\d,\s]+\]', '', texto)
        partes = re.split(r'(\$.*?\$|\\begin\{.*?\}|\\end\{.*?\}|\\[a-zA-Z]+(?:\{.*?\})*)', texto)
        resultado = []
        for i, parte in enumerate(partes):
            if i % 2 == 1:
                # É código LaTeX ou math, não alterar
                resultado.append(parte)
            else:
                p = re.sub(r'(?<!\\)%', r'\%', parte)
                p = re.sub(r'(?<!\\)&', r'\&', p)
                p = re.sub(r'(?<!\\)#', r'\#', p)
                p = re.sub(r'(?<!\\)\^', r'\\textasciicircum{}', p)
                p = re.sub(r'(?<!\\)~', r'\\textasciitilde{}', p)
                p = re.sub(r'"([^"\n]+)"', r"``\1''", p)
                p = p.replace('"', "''")
                resultado.append(p)
        return "".join(resultado)

    def converter_formatacao_inline(self, linha):
        """Converte negrito, itálico, código, links e citações em uma linha com escape estrito."""
        if not linha:
            return ""

        # Remove marcadores de citação de ferramentas de IA (ex: [cite: 170])
        linha = re.sub(r'\[cite:\s*[\d,\s]+\]', '', linha)

        # 1. Proteção de blocos matemáticos ($...$)
        math_tokens = []
        def salvar_math(match):
            math_tokens.append(match.group(0))
            return f"@@MATHTOKEN{len(math_tokens)-1}@@"

        linha = re.sub(r'\$.*?\$', salvar_math, linha)

        # Tokens de comandos/links sem underscore para evitar interferência com o parser de itálico
        cmd_tokens = []
        def salvar_cmd(s):
            cmd_tokens.append(s)
            return f"@@CMDTOKEN{len(cmd_tokens)-1}@@"

        # 1.5. Garante que qualquer ocorrência de |%| fora de crases seja tratada como código inline
        linha = re.sub(r'(?<![`\w])\\?\|%\\?\|(?![`\w])', r'`|%|`', linha)

        # 2. Inline code: `codigo` -> \texttt{codigo}
        code_tokens = []
        def repl_code(match):
            c = match.group(1)
            if c == 'build_vector_db.py':
                code_tokens.append(r"\mbox{\texttt{build\_vector\_db.py}}")
                return f"@@CODETOKEN{len(code_tokens)-1}@@"

            c = c.replace(r'\|', '|')
            c = c.replace('\\', r'@@BACKSLASH@@')
            c = c.replace('{', r'\{').replace('}', r'\}')
            # Substitui duas aspas simples seguidas por '{}' para que não virem aspas duplas (ligadura LaTeX)
            c = c.replace("''", "'{}'")
            c = c.replace('|', r'\textbar{}')
            c = c.replace('%', r'\%').replace('&', r'\&').replace('#', r'\#')
            c = c.replace('^', r'\textasciicircum{}').replace('~', r'\textasciitilde{}')
            c = c.replace('$', r'\$')
            c = c.replace('@@BACKSLASH@@', r'\textbackslash{}')
            # Permite quebras de linha seguras em código monoespaçado longo (evita estouro de margem)
            c = c.replace('_', r'\_\allowbreak ')
            c = re.sub(r'(?<=[a-zA-Z0-9])\.(?=[a-zA-Z0-9])', r'.\\allowbreak ', c)
            c = re.sub(r'(?<=[a-zA-Z0-9])/(?=[a-zA-Z0-9])', r'/\\allowbreak ', c)
            code_tokens.append(f"\\texttt{{{c}}}")
            return f"@@CODETOKEN{len(code_tokens)-1}@@"

        linha = re.sub(r'`([^`]+)`', repl_code, linha)

        # 3. Citações estilo Pandoc: [@Chave, p. 12] -> \cite[p.~12]{Chave} ou [@Chave1; @Chave2] -> \cite{Chave1,Chave2}
        cite_tokens = []
        def repl_cite(match):
            corpo = match.group(1).strip()
            if ';' in corpo:
                itens = [c.strip().lstrip('@').strip() for c in corpo.split(';') if c.strip()]
                chaves = [c.split(',')[0].strip().lstrip('@') for c in itens]
                res = f"\\cite{{{','.join(chaves)}}}"
            elif ',' in corpo:
                partes = corpo.split(',', 1)
                chave = partes[0].strip().lstrip('@')
                pag = partes[1].strip()
                res = f"\\cite[{pag}]{{{chave}}}"
            else:
                res = f"\\cite{{{corpo.lstrip('@')}}}"
            cite_tokens.append(res)
            return f"@@CITETOKEN{len(cite_tokens)-1}@@"

        linha = re.sub(r'\[(@[a-zA-Z0-9_\-:\.,\s;@]+)\]', repl_cite, linha)

        # 4. Citação no fluxo do texto: @Chave -> \citeonline{Chave}
        def repl_citeonline(match):
            chave = match.group(1)
            cite_tokens.append(f"\\citeonline{{{chave}}}")
            return f"@@CITETOKEN{len(cite_tokens)-1}@@"

        linha = re.sub(r'(?<![\\@\w])@([a-zA-Z0-9_\-:]+)', repl_citeonline, linha)

        # 5. Links Markdown
        linha = re.sub(r'\[([^\]]+)\]\(#(sec:[^\)]+)\)', lambda m: salvar_cmd(f"\\autoref{{{m.group(2)}}}"), linha)
        linha = re.sub(r'\[([^\]]+)\]\(#(fig:[^\)]+)\)', lambda m: salvar_cmd(f"\\autoref{{{m.group(2)}}}"), linha)
        linha = re.sub(r'\[([^\]]+)\]\(#(tab:[^\)]+)\)', lambda m: salvar_cmd(f"\\autoref{{{m.group(2)}}}"), linha)
        linha = re.sub(r'\[([^\]]+)\]\((https?:\/\/[^\)]+)\)', lambda m: salvar_cmd(f"\\href{{{m.group(2)}}}{{{m.group(1)}}}"), linha)

        # 6. Escapar caracteres especiais no texto comum fora dos tokens: %, #, &, ^, ~
        linha = re.sub(r'(?<!\\)%', r'\%', linha)
        linha = re.sub(r'(?<!\\)#', r'\#', linha)
        linha = re.sub(r'(?<!\\)&', r'\&', linha)
        linha = re.sub(r'(?<!\\)\^', r'\\textasciicircum{}', linha)
        linha = re.sub(r'(?<!\\)~', r'\\textasciitilde{}', linha)
        # Aspas duplas em texto comum: converter para aspas tipográficas do LaTeX
        linha = re.sub(r'"([^"\n]+)"', r"``\1''", linha)
        linha = linha.replace('"', "''")

        # 7. Negrito e Itálico
        linha = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', linha)
        linha = re.sub(r'__(.+?)__', r'\\textbf{\1}', linha)
        linha = re.sub(r'\*(.+?)\*', r'\\textit{\1}', linha)
        linha = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\\textit{\1}', linha)

        # 8. Restauração dos tokens protegidos
        for idx, t in enumerate(cmd_tokens):
            linha = linha.replace(f"@@CMDTOKEN{idx}@@", t)
        for idx, t in enumerate(cite_tokens):
            linha = linha.replace(f"@@CITETOKEN{idx}@@", t)
        for idx, t in enumerate(code_tokens):
            linha = linha.replace(f"@@CODETOKEN{idx}@@", t)
        for idx, t in enumerate(math_tokens):
            linha = linha.replace(f"@@MATHTOKEN{idx}@@", t)

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

                # Remove numeração manual do título se fornecida pela LLM
                titulo_limpo = re.sub(r'^\d+(\.\d+)*\.?\s*', '', titulo).strip()
                if nivel == 2:
                    titulo_limpo = titulo_limpo.upper()
                slug = gerar_slug(titulo_limpo)
                titulo_tex = self.converter_formatacao_inline(titulo_limpo)
                titulo_tex = re.sub(r'"([^"\n]+)"', r"``\1''", titulo_tex).replace('"', "''")

                if nivel == 1:
                    latex_saida.append(f"\\chapter{{{titulo_tex}}}\\label{{sec:{slug}}}\n")
                elif nivel == 2:
                    latex_saida.append(f"\\FloatBarrier\n\\section{{{titulo_tex}}}\\label{{sec:{slug}}}\n")
                elif nivel == 3:
                    latex_saida.append(f"\\FloatBarrier\n\\subsection{{{titulo_tex}}}\\label{{sec:{slug}}}\n")
                elif nivel == 4:
                    latex_saida.append(f"\\subsubsection{{{titulo_tex}}}\\label{{sec:{slug}}}\n")
                else:
                    latex_saida.append(f"\\subsubsubsection{{{titulo_tex}}}\\label{{sec:{slug}}}\n")
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

                # Garantir existência física do arquivo de imagem
                if not os.path.exists(caminho):
                    print(f"[AVISO] Imagem '{caminho}' não encontrada no disco.")
                    if os.path.exists("images/figura1.png"):
                        os.makedirs(os.path.dirname(caminho) or "images", exist_ok=True)
                        shutil.copy2("images/figura1.png", caminho)
                        print(f"  -> Criada cópia temporária de 'images/figura1.png' para '{caminho}' para evitar falha no Overleaf.")

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

                legenda_tex = self.converter_formatacao_inline(legenda)
                fonte_tex = self.converter_formatacao_inline(fonte)

                latex_saida.append("\\begin{figure}[htb]")
                latex_saida.append(f"  \\caption{{{legenda_tex}}}")
                latex_saida.append(f"  \\label{{{label}}}")
                latex_saida.append("  \\begin{center}")
                latex_saida.append(f"    \\includegraphics[width={largura}\\textwidth]{{{caminho}}}")
                latex_saida.append("  \\end{center}")
                latex_saida.append(f"  \\legend{{Fonte: {fonte_tex}}}")
                latex_saida.append("\\end{figure}\n\\FloatBarrier\n")
                i += 1
                continue

            # --- 8. Tabelas em Markdown ---
            if linha.startswith("|") and linha.endswith("|"):
                tabela_linhas = [linha]
                i += 1
                while i < total_linhas and linhas[i].strip().startswith("|") and linhas[i].strip().endswith("|"):
                    tabela_linhas.append(linhas[i].strip())
                    i += 1

                # Verifica se a linha seguinte é fonte (pulando eventuais linhas em branco)
                fonte_tab = "Dados da pesquisa (2026)."
                idx_f = i
                while idx_f < total_linhas and not linhas[idx_f].strip():
                    idx_f += 1

                if idx_f < total_linhas:
                    prox = linhas[idx_f].strip()
                    m_tab_fonte = re.match(r'^\*?Fonte:\s*(.*?)\*?$', prox, re.IGNORECASE)
                    if m_tab_fonte:
                        fonte_tab = m_tab_fonte.group(1).rstrip('*').strip()
                        i = idx_f + 1

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

            # --- 11. Parágrafo comum e Alíneas a), b), c) (Manual EDUFBA p. 86) ---
            linha_formatada = self.converter_formatacao_inline(linha)
            if re.match(r'^[a-z]\)\s+', linha):
                linha_formatada = r"\par\indent " + linha_formatada
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
        """Converte matriz de linhas Markdown para ambiente tabularx responsivo do LaTeX."""
        if len(linhas) < 2:
            return ""

        def parse_row(linha_str):
            s = linha_str.strip().strip('|')
            # Protege códigos inline que contenham | para não partir colunas da tabela
            code_in_row = []
            def hide_code_in_table(m):
                code_in_row.append(m.group(0))
                return f"@@TABLECODE{len(code_in_row)-1}@@"
            s = re.sub(r'`[^`]+`', hide_code_in_table, s)
            s = s.replace(r'\|', '@@ESCAPEDPIPE@@')
            cols = []
            for c in s.split('|'):
                col_txt = c.strip()
                for idx, t in enumerate(code_in_row):
                    col_txt = col_txt.replace(f"@@TABLECODE{idx}@@", t)
                col_txt = col_txt.replace('@@ESCAPEDPIPE@@', r'\textbar{}')
                cols.append(col_txt)
            return cols

        # Cabeçalho
        cols_cabecalho = parse_row(linhas[0])
        num_cols = len(cols_cabecalho)
        if num_cols == 0:
            return ""

        # Linhas de dados (ignorando a linha divisória |---|---|)
        linhas_dados = []
        for l in linhas[1:]:
            if re.match(r'^[\|\s\:\-]+$', l):
                continue
            cols = parse_row(l)
            if len(cols) < num_cols:
                cols += [''] * (num_cols - len(cols))
            elif len(cols) > num_cols:
                cols = cols[:num_cols-1] + [" / ".join(cols[num_cols-1:])]
            linhas_dados.append(cols)

        # Mapeamento com títulos e perfis de largura milimetricamente ajustados à mancha da página
        tabelas_conhecidas = {
            1: {
                "titulo": "Síntese da demanda histórica de suporte e fricção no CorText Manager",
                "cols": r"|>{\raggedright\arraybackslash}p{3.8cm}|>{\centering\arraybackslash}p{2.2cm}|>{\centering\arraybackslash}p{2.0cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "4pt",
                "multipage": False
            },
            2: {
                "titulo": "Mapeamento dos tópicos de maior engajamento no fórum oficial",
                "cols": r"|>{\centering\arraybackslash}p{0.8cm}|>{\raggedright\arraybackslash}X|>{\centering\arraybackslash}p{2.2cm}|>{\centering\arraybackslash}p{1.7cm}|>{\raggedright\arraybackslash}p{2.2cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\footnotesize",
                "colsep": "2.5pt",
                "multipage": False
            },
            3: {
                "titulo": "Posicionamento comparativo frente às vertentes da literatura",
                "cols": r"|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\footnotesize",
                "colsep": "3pt",
                "multipage": False
            },
            4: {
                "titulo": "Matriz de articulação teórico-empírica e solução arquitetural",
                "cols": r"|>{\raggedright\arraybackslash}p{3.2cm}|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "4pt",
                "multipage": False
            },
            5: {
                "titulo": "Fases da engenharia de extração do acervo do fórum oficial",
                "cols": r"|>{\raggedright\arraybackslash}p{3.6cm}|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "4pt",
                "multipage": False
            },
            6: {
                "titulo": "Critérios analíticos de elegibilidade para parsing derivado",
                "cols": r"|>{\raggedright\arraybackslash}p{4.2cm}|>{\centering\arraybackslash}p{3.0cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "4pt",
                "multipage": False
            },
            7: {
                "titulo": "Cronograma de execução das etapas metodológicas do projeto",
                "cols": r"|>{\raggedright\arraybackslash}X|>{\centering\arraybackslash}p{0.75cm}|>{\centering\arraybackslash}p{0.75cm}|>{\centering\arraybackslash}p{0.75cm}|>{\centering\arraybackslash}p{0.75cm}|>{\centering\arraybackslash}p{0.75cm}|>{\centering\arraybackslash}p{0.75cm}|>{\centering\arraybackslash}p{2.0cm}|",
                "fontsize": r"\footnotesize",
                "colsep": "2.5pt",
                "multipage": False
            },
            8: {
                "titulo": "Matriz de Requisitos Funcionais do Assistente (RF01 a RF24)",
                "cols": r"|>{\centering\arraybackslash}p{1.4cm}|>{\raggedright\arraybackslash}p{2.4cm}|>{\centering\arraybackslash}p{1.6cm}|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}p{2.8cm}|",
                "fontsize": r"\footnotesize",
                "colsep": "3pt",
                "multipage": True
            },
            9: {
                "titulo": "Especificação dos Requisitos Não Funcionais do sistema (RNF01 a RNF04)",
                "cols": r"|>{\centering\arraybackslash}p{1.4cm}|>{\raggedright\arraybackslash}p{3.2cm}|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "3.5pt",
                "multipage": False
            },
            10: {
                "titulo": "Módulos nucleares da arquitetura do assistente sociotécnico",
                "cols": r"|>{\raggedright\arraybackslash}p{3.0cm}|>{\raggedright\arraybackslash}X|>{\centering\arraybackslash}p{2.2cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "3.5pt",
                "multipage": False
            },
            11: {
                "titulo": "Matriz experimental de casos de teste da Engenharia do Caos (TC01 a TC22)",
                "cols": r"|>{\centering\arraybackslash}p{1.1cm}|>{\centering\arraybackslash}p{1.1cm}|>{\centering\arraybackslash}p{1.4cm}|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}X|>{\raggedright\arraybackslash}p{2.2cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\scriptsize",
                "colsep": "2.0pt",
                "multipage": True
            },
            12: {
                "titulo": "Distribuição dos chamados de processamento por status formal",
                "cols": r"|>{\raggedright\arraybackslash}p{3.4cm}|>{\centering\arraybackslash}p{3.0cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\small",
                "colsep": "4pt",
                "multipage": False
            },
            13: {
                "titulo": "Estatísticas descritivas de extensão das dúvidas por escopo metodológico",
                "cols": r"|>{\raggedright\arraybackslash}X|>{\centering\arraybackslash}p{1.4cm}|>{\centering\arraybackslash}p{1.6cm}|>{\centering\arraybackslash}p{1.6cm}|>{\centering\arraybackslash}p{1.6cm}|>{\centering\arraybackslash}p{1.6cm}|",
                "fontsize": r"\small",
                "colsep": "2.5pt",
                "multipage": False
            },
            14: {
                "titulo": "Dicionário de atributos do conjunto de dados auditado do fórum",
                "cols": r"|>{\centering\arraybackslash}p{1.1cm}|>{\raggedright\arraybackslash}p{3.6cm}|>{\centering\arraybackslash}p{2.2cm}|>{\raggedright\arraybackslash}X|",
                "fontsize": r"\footnotesize",
                "colsep": "3pt",
                "multipage": True
            }
        }

        multipage = False
        if self.table_counter in tabelas_conhecidas:
            cfg = tabelas_conhecidas[self.table_counter]
            titulo = cfg["titulo"]
            col_spec = cfg["cols"]
            fontsize = cfg["fontsize"]
            colsep = cfg["colsep"]
            multipage = cfg.get("multipage", False)
        else:
            if num_cols <= 3:
                fontsize = r"\small"
                colsep = "4pt"
            elif num_cols <= 5:
                fontsize = r"\footnotesize"
                colsep = "3pt"
            else:
                fontsize = r"\scriptsize"
                colsep = "2pt"

            col_specs = []
            for col_idx in range(num_cols):
                header_text = cols_cabecalho[col_idx].strip()
                max_len = max([len(row[col_idx]) for row in linhas_dados] + [len(header_text)])
                if max_len <= 3:
                    col_specs.append(r">{\centering\arraybackslash}p{1.0cm}")
                elif max_len <= 8 or header_text.lower() in ['código', 'codigo', 'ordem', 'mês', 'mes', 'fase']:
                    col_specs.append(r">{\centering\arraybackslash}p{1.5cm}")
                elif max_len <= 14:
                    col_specs.append(r">{\centering\arraybackslash}p{2.2cm}")
                else:
                    col_specs.append(r">{\raggedright\arraybackslash}X")

            if not any("X" in c for c in col_specs):
                col_specs[-1] = r">{\raggedright\arraybackslash}X"

            col_spec = "|" + "|".join(col_specs) + "|"

        header_tex = " & ".join([f"\\textbf{{{self.converter_formatacao_inline(c)}}}" for c in cols_cabecalho])

        if multipage:
            latex = []
            latex.append("{\n" + f"{fontsize}")
            latex.append(f"\\setlength{{\\tabcolsep}}{{{colsep}}}")
            latex.append(f"\\begin{{xltabular}}{{\\textwidth}}{{{col_spec}}}")
            latex.append(f"  \\caption{{{self.converter_formatacao_inline(titulo)}}}\\label{{{label}}}\\\\")
            latex.append("  \\hline")
            latex.append(f"  {header_tex} \\\\ \\hline")
            latex.append("  \\endfirsthead")
            latex.append(f"  \\caption[]{{{self.converter_formatacao_inline(titulo)} (continuação)}}\\\\")
            latex.append("  \\hline")
            latex.append(f"  {header_tex} \\\\ \\hline")
            latex.append("  \\endhead")
            latex.append("  \\hline")
            latex.append(f"  \\multicolumn{{{num_cols}}}{{r}}{{\\footnotesize\\textit{{continua na próxima página\\dots}}}} \\\\")
            latex.append("  \\endfoot")
            latex.append("  \\hline")
            latex.append("  \\endlastfoot")
            for row in linhas_dados:
                row_tex = " & ".join([self.converter_formatacao_inline(c) for c in row])
                latex.append(f"  {row_tex} \\\\ \\hline")
            latex.append("\\end{xltabular}")
            latex.append(f"\\vspace{{-0.2cm}}\\noindent{{\\footnotesize\\textit{{Fonte: {self.converter_formatacao_inline(fonte)}}}}}\\par\\vspace{{0.4cm}}\n}}\n\\FloatBarrier\n")
            return "\n".join(latex)

        latex = []
        latex.append("\\begin{table}[htb]")
        latex.append(f"  \\caption{{{self.converter_formatacao_inline(titulo)}}}")
        latex.append(f"  \\label{{{label}}}")
        latex.append("  \\centering")
        latex.append(f"  {fontsize}")
        latex.append(f"  \\setlength{{\\tabcolsep}}{{{colsep}}}")
        latex.append(f"  \\begin{{tabularx}}{{\\textwidth}}{{{col_spec}}}")
        latex.append("    \\hline")
        latex.append(f"    {header_tex} \\\\ \\hline")
        for row in linhas_dados:
            row_tex = " & ".join([self.converter_formatacao_inline(c) for c in row])
            latex.append(f"    {row_tex} \\\\ \\hline")
        latex.append("  \\end{tabularx}")
        latex.append(f"  \\legend{{Fonte: {self.converter_formatacao_inline(fonte)}}}")
        latex.append("\\end{table}\n\\FloatBarrier\n")
        return "\n".join(latex)


def gerar_latex_mestre(metadata, capitulos_tex, apendices_tex, anexos_tex):
    """Gera o arquivo LaTeX principal (main.tex) estruturado segundo as normas da UFBA."""
    conv = MarkdownToLatex()
    def esc_meta(val):
        if not val:
            return ""
        return conv.escapar_caracteres_especiais(str(val))

    titulo = esc_meta(metadata.get("titulo", "Título do Trabalho"))
    subtitulo = esc_meta(metadata.get("subtitulo", ""))
    subtitulo = re.sub(r'RAG\s+e\b', r'RAG\\space e', subtitulo, flags=re.IGNORECASE)
    autor = esc_meta(metadata.get("autor", "Nome do Autor"))
    instituicao = esc_meta(metadata.get("instituicao", "Universidade Federal da Bahia"))
    faculdade = esc_meta(metadata.get("faculdade", "Instituto de Computação"))
    programa = esc_meta(metadata.get("programa", "Colegiado do Curso de Ciência da Computação"))
    curso = esc_meta(metadata.get("curso", "Ciência da Computação"))
    grau = esc_meta(metadata.get("grau", "Bacharel em Ciência da Computação"))
    tipotrabalho = esc_meta(metadata.get("tipotrabalho", "Trabalho de Conclusão de Curso"))
    cidade = esc_meta(metadata.get("local", "Salvador"))
    ano = str(metadata.get("ano", "2026"))
    data_str = esc_meta(str(metadata.get("data", ano)))

    # Orientador(a)
    orientador = metadata.get("orientador", {})
    if isinstance(orientador, str):
        orientador = {"nome": orientador}
    elif not isinstance(orientador, dict):
        orientador = {}
    nome_orientador = esc_meta(orientador.get("nome", "Prof. Dr. Orientador"))
    genero_orientador = orientador.get("genero", "M")
    genero_orientador = genero_orientador.upper() if isinstance(genero_orientador, str) else "M"

    # Coorientador(a)
    coorientador = metadata.get("coorientador", {})
    if isinstance(coorientador, str):
        coorientador = {"nome": coorientador}
    elif not isinstance(coorientador, dict):
        coorientador = {}
    nome_coorientador = esc_meta(coorientador.get("nome", ""))
    genero_coorientador = coorientador.get("genero", "M")
    genero_coorientador = genero_coorientador.upper() if isinstance(genero_coorientador, str) else "M"

    # Preâmbulo padrão
    preambulo = metadata.get("preambulo_customizado", "")
    if not preambulo:
        preambulo = (
            f"{tipotrabalho} apresentado ao {programa} da "
            f"{instituicao}, como requisito para obtenção do grau de {grau}."
        )
    preambulo = esc_meta(preambulo)

    # Referência própria para cabeçalho do Resumo (exigência EDUFBA p. 56 e 64-65)
    ref_autor_custom = metadata.get("autor_referencia") or metadata.get("autor_citacao")
    if ref_autor_custom:
        ref_autor = esc_meta(str(ref_autor_custom).strip())
        if ref_autor == "SILVA, W. M. de J.":
            ref_autor = "SILVA, W. M. de J. S."
    else:
        ref_autor = formatar_nome_referencia(autor)
    ref_autor_ponto = ref_autor if ref_autor.endswith('.') else f"{ref_autor}."
    subtitulo_ref = f": {subtitulo}" if subtitulo else ""
    ref_trabalho = (
        f"{ref_autor_ponto} \\textbf{{{titulo}{subtitulo_ref}}}. {ano}. "
        f"\\pageref{{LastPage}} f. {tipotrabalho} ({grau}) -- {faculdade}, "
        f"{instituicao}, {cidade}, {ano}."
    )

    # Mapeamentos para referência em inglês do Abstract (EDUFBA p. 64-65)
    trad_grau = {
        "Bacharel em Sistemas de Informação": "Bachelor in Information Systems",
        "Bacharel em Ciência da Computação": "Bachelor in Computer Science",
        "Bacharel em Engenharia de Computação": "Bachelor in Computer Engineering",
        "Bacharelado em Sistemas de Informação": "Bachelor in Information Systems",
        "Bacharelado em Ciência da Computação": "Bachelor in Computer Science",
        "Bacharelado em Engenharia de Computação": "Bachelor in Computer Engineering",
    }
    trad_inst = {
        "Universidade Federal da Bahia": "Federal University of Bahia",
    }
    trad_fac = {
        "Instituto de Computação": "Institute of Computing",
        "Escola Politécnica": "Polytechnic School",
        "Faculdade de Farmácia": "Faculty of Pharmacy",
        "Faculdade de Medicina": "Faculty of Medicine",
        "Faculdade de Direito": "Faculty of Law",
    }
    grau_raw = str(metadata.get("grau", "Bacharel em Sistemas de Informação")).strip()
    faculdade_raw = str(metadata.get("faculdade", "Instituto de Computação")).strip()
    instituicao_raw = str(metadata.get("instituicao", "Universidade Federal da Bahia")).strip()

    grau_en = esc_meta(metadata.get("grau_en") or trad_grau.get(grau_raw, grau_raw.replace("Bacharel em", "Bachelor in").replace("Bacharelado em", "Bachelor in")))
    faculdade_en = esc_meta(metadata.get("faculdade_en") or trad_fac.get(faculdade_raw, faculdade_raw.replace("Instituto de", "Institute of").replace("Faculdade de", "Faculty of")))
    instituicao_en = esc_meta(metadata.get("instituicao_en") or trad_inst.get(instituicao_raw, "Federal University of Bahia" if "Bahia" in instituicao_raw else instituicao_raw))
    tipo_en = esc_meta(metadata.get("tipotrabalho_en", "Final Graduation Project"))

    titulo_en = esc_meta(metadata.get("titulo_en", "") or "Sociotechnical Observability Assistant")
    subtitulo_en = esc_meta(metadata.get("subtitulo_en", "") or "support for diagnosing corpora import in CorText Manager with RAG and Log Analysis")
    if subtitulo_en:
        subtitulo_en = re.sub(r'RAG\s+and\b', r'RAG\\space and', subtitulo_en, flags=re.IGNORECASE)
        subtitulo_en = re.sub(r'RAG\s+e\b', r'RAG\\space e', subtitulo_en, flags=re.IGNORECASE)

    subtitulo_ref_en = f": {subtitulo_en}" if subtitulo_en else ""
    ref_trabalho_en = (
        f"{ref_autor_ponto} \\textbf{{{titulo_en}{subtitulo_ref_en}}}. {ano}. "
        f"\\pageref{{LastPage}} p. {tipo_en} ({grau_en}) -- {faculdade_en}, "
        f"{instituicao_en}, {cidade}, {ano}."
    )

    # Início do documento
    tex = []
    tex.append(r"""\documentclass[
	oneside,
	a4paper,
	12pt,
	chapter=TITLE,
	section=TITLE,
	english,
	brazilian
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
\usepackage{placeins}
% \usepackage{microtype} % Desativado para compilação ultrarrápida no Overleaf (ative se desejar na versão final)
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{listings}
\usepackage{pdfpages}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{xltabular}
\keepXColumns
\usepackage{xurl}
\usepackage{hyperref}
\pdfstringdefDisableCommands{%
  \def\uppercase#1{#1}%
  \def\MakeUppercase#1{#1}%
}

% --- DESATIVAÇÃO DE CARACTERES ATIVOS DO BABEL (Evita erros de aspas em títulos/textos) ---
\AtBeginDocument{%
  \addto\extrasbrazilian{\shorthandoff{"}}%
  \addto\extrasportuges{\shorthandoff{"}}%
  \shorthandoff{"}%
}

% --- SISTEMA DE CITAÇÕES ABNT (NBR 6023:2018 / NBR 10520) ---
\usepackage[
	alf,
	abnt-emphasize=bf,
	abnt-thesis-year=both,
	abnt-repeated-author-omit=yes,
	abnt-last-names=abnt,
	abnt-etal-cite=3,
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
\selectlanguage{brazilian}
\shorthandoff{"}
\emergencystretch 3em
\hfuzz 1pt

% ==============================================================================
% ELEMENTOS PRÉ-TEXTUAIS
% ==============================================================================

\imprimircapa
\imprimirfolhaderosto
""")

    # Ficha catalográfica
    ficha = metadata.get("ficha_catalografica", {})
    if not isinstance(ficha, dict):
        ficha = {}
    if ficha.get("inserir", False) and os.path.exists(ficha.get("arquivo", "ficha.pdf")):
        tex.append("% Ficha Catalográfica (SIBI/UFBA)\n\\includepdf{" + ficha.get("arquivo", "ficha.pdf") + "}\n")

    # Folha de aprovação
    aprov = metadata.get("folha_aprovacao", {})
    if not isinstance(aprov, dict):
        aprov = {}
    if aprov.get("inserir", True):
        data_aprov = esc_meta(aprov.get("data_aprovacao", f"xx de mês de {ano}"))
        tex.append(r"""
% --- FOLHA DE APROVAÇÃO (Manual EDUFBA p. 49, 52) ---
\begin{folhadeaprovacao}
  \begin{center}
    {\fontsize{14}{16}\selectfont\bfseries\MakeUppercase{\imprimirautor}\par}
    \vspace{1.5cm}
    {\fontsize{16}{18}\selectfont\bfseries\MakeUppercase{\imprimirtitulo}%
    \ifx\imprimirsubtitulo\empty\else{: \fontsize{14}{16}\selectfont\MakeUppercase{\imprimirsubtitulo}}\fi\par}
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
        if not isinstance(banca, list) or not banca:
            banca = [{"nome": nome_orientador, "papel": "Orientador", "instituicao": instituicao}]
        for membro in banca:
            if not isinstance(membro, dict):
                membro = {"nome": str(membro)}
            m_nome = esc_meta(membro.get("nome", ""))
            m_papel = esc_meta(membro.get("papel", "Examinador"))
            m_inst = esc_meta(membro.get("instituicao", instituicao))
            tex.append(f"  \\assinatura{{\\textbf{{{m_nome}}} \\\\ {m_papel} -- {m_inst}}}")
        tex.append(r"\end{folhadeaprovacao}" + "\n")

    # Dedicatória
    dedicatoria = str(metadata.get("dedicatoria") or "").strip()
    if dedicatoria:
        dedicatoria_tex = esc_meta(dedicatoria).replace('\n', '\\\\\n')
        tex.append(r"""
% --- DEDICATÓRIA ---
\begin{dedicatoria}
  \vspace*{\fill}
  \begin{flushright}
    \noindent\textit{""" + dedicatoria_tex + r"""}
  \end{flushright}
  \vspace*{2cm}
\end{dedicatoria}
""")

    # Agradecimentos
    agradecimentos = str(metadata.get("agradecimentos") or "").strip()
    if agradecimentos:
        agradecimentos_tex = esc_meta(agradecimentos)
        tex.append(r"""
% --- AGRADECIMENTOS ---
\begin{agradecimentos}
""" + agradecimentos_tex + r"""
\end{agradecimentos}
""")

    # Epígrafe
    epigrafe = metadata.get("epigrafe", {})
    if not isinstance(epigrafe, dict):
        epigrafe = {}
    if epigrafe and epigrafe.get("texto"):
        ep_texto = esc_meta(str(epigrafe.get("texto") or "").strip()).replace('\n', '\\\\\n    ')
        ep_autor = esc_meta(str(epigrafe.get("autor") or "").strip())
        tex.append(r"""
% --- EPÍGRAFE (Manual EDUFBA p. 55 / ABNT NBR 14724) ---
\begin{epigrafe}
  \vspace*{\fill}
  \begin{flushright}
    \SingleSpacing\fontsize{11}{13}\selectfont
    \textit{""" + f"``{ep_texto}''" + r"""}\par
    \vspace{0.5cm}
    """ + ep_autor + r"""
  \end{flushright}
  \vspace*{2cm}
\end{epigrafe}
""")

    # Resumo em Português
    resumo = str(metadata.get("resumo") or "").strip()
    palavras_chave = metadata.get("palavras_chave", [])
    if not isinstance(palavras_chave, list):
        palavras_chave = [str(palavras_chave)] if palavras_chave else []
    if resumo:
        resumo_tex = esc_meta(resumo)
        kw_str = ". ".join([esc_meta(k) for k in palavras_chave]) + "." if palavras_chave else ""
        tex.append(r"""
% --- RESUMO (Manual EDUFBA p. 56 e 64-65: referência no topo, antes do título) ---
\begin{resumo}
  \SingleSpacing
  \noindent """ + ref_trabalho + r"""

  \vspace{1.0cm}
  \begin{center}
    {\ABNTEXchapterfontsize\bfseries\MakeUppercase{\resumoname}}
  \end{center}
  \vspace{0.6cm}

  \noindent """ + resumo_tex + r"""

  \vspace{0.5cm}
  \noindent\textbf{Palavras-chave}: """ + kw_str + r"""
\end{resumo}
""")

    # Abstract em Inglês
    abstract = str(metadata.get("abstract") or "").strip()
    keywords = metadata.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = [str(keywords)] if keywords else []
    if abstract:
        abstract_tex = esc_meta(abstract)
        kw_en_str = ". ".join([esc_meta(k) for k in keywords]) + "." if keywords else ""
        tex.append(r"""
% --- ABSTRACT (Manual EDUFBA p. 56 e 64-65: referência em inglês no topo) ---
\begin{resumo}[Abstract]
  \SingleSpacing
  \noindent """ + ref_trabalho_en + r"""

  \vspace{1.0cm}
  \begin{center}
    {\ABNTEXchapterfontsize\bfseries\MakeUppercase{Abstract}}
  \end{center}
  \vspace{0.6cm}

  \noindent """ + abstract_tex + r"""

  \vspace{0.5cm}
  \noindent\textbf{Keywords}: """ + kw_en_str + r"""
\end{resumo}
\selectlanguage{brazilian}
\shorthandoff{"}
\emergencystretch 3em
\hfuzz 1pt
""")

    # Listas
    listas = metadata.get("listas", {})
    if not isinstance(listas, dict):
        listas = {}
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
    if not isinstance(siglas, dict):
        siglas = {}
    if listas.get("siglas", True) and siglas:
        tex.append(r"""
% --- LISTA DE ABREVIATURAS E SIGLAS ---
\begin{siglas}
""")
        for sigla in sorted(siglas.keys()):
            sigla_item = esc_meta(sigla)
            expansao = esc_meta(siglas[sigla])
            tex.append(f"  \\item[{sigla_item}]\\quad {expansao}")
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
        "references.bib",
        "logo_ufba.png",
        "latexmkrc",
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
