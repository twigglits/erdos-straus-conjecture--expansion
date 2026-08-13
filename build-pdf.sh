#!/bin/sh
# ponytail: one line, no Makefile — pdflatex needs unicode-header.tex for ✔ → ℓ σ χ outside math
pandoc JNAUDE-ERDOS-STRAUS-EXPANSION.md -o JNAUDE-ERDOS-STRAUS-EXPANSION.pdf --pdf-engine=pdflatex -H unicode-header.tex
