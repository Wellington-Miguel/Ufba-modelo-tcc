# ==============================================================================
# Makefile para Automação do TCC UFBA (Markdown -> abnTeX2 -> PDF)
# ==============================================================================

PYTHON ?= python

.PHONY: all pdf tex zip clean help

# Alvo padrão: gera o LaTeX e compila o PDF (ou gera o ZIP para Overleaf se não houver LaTeX local)
all:
	$(PYTHON) build.py

# Gera apenas o arquivo LaTeX principal (main.tex) a partir dos Markdowns
tex:
	$(PYTHON) build.py --tex

# Força a tentativa de compilação em PDF local
pdf:
	$(PYTHON) build.py --pdf

# Empacota todo o projeto para importação direta no Overleaf
zip:
	$(PYTHON) build.py --zip

# Limpa arquivos intermediários e auxiliares gerados pela compilação
clean:
	$(PYTHON) build.py --clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make         - Compila o TCC (gera main.tex e tenta gerar o PDF)"
	@echo "  make tex     - Gera apenas o arquivo LaTeX mestre (main.tex)"
	@echo "  make pdf     - Compila o PDF localmente usando pdflatex/latexmk"
	@echo "  make zip     - Cria pacote tcc-ufba-overleaf.zip para upload no Overleaf"
	@echo "  make clean   - Remove arquivos temporários de compilação (.aux, .log, etc.)"
