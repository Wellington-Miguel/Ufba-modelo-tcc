# Conclusão

A elaboração de um trabalho científico de fôlego como um TCC, dissertação ou tese impõe ao pesquisador uma dupla responsabilidade: a solidez do conteúdo investigado e o atendimento irrestrito às normas técnicas de formatação e normalização. No âmbito da Universidade Federal da Bahia, essas exigências encontram respaldo nas diretrizes consolidadas pelo Manual da EDUFBA [@EDUFBA2019].

O presente projeto demonstrou que a divisão do trabalho acadêmico em blocos modulares escritos em Markdown resolve com eficácia a principal dificuldade enfrentada por estudantes ao utilizarem modelos de linguagem de grande porte (LLMs): a fragmentação de respostas e a inconsistência de contexto em textos extensos.

A implementação de uma esteira automatizada em Python permitiu unir a agilidade da escrita em Markdown à precisão gráfica da classe abnTeX2, assegurando que:

- Metadados institucionais fiquem centralizados em um único arquivo de fácil edição (`metadata.yaml`);
- As referências bibliográficas sejam validadas e formatadas no padrão ABNT NBR 6023:2018;
- As ilustrações e tabelas recebam automaticamente títulos superiores e legendas de fonte inferiores, em cumprimento às recomendações da UFBA;
- O projeto possa ser compilado localmente em sistemas Windows, Linux e macOS ou exportado em um único arquivo ZIP pronto para o Overleaf.

## Contribuições do Trabalho

As principais contribuições deste modelo incluem:

1. **Reprodutibilidade e Modularidade**: O estudante pode editar ou adicionar novos capítulos sem risco de desconfigurar cabeçalhos, preâmbulos ou numeração de páginas;
2. **Integração Fluida com IA**: Elimina a necessidade de pedir à LLM que gere códigos complexos em LaTeX, reduzindo significativamente alucinações e erros de sintaxe;
3. **Conformidade Institucional**: Garante aderência estrita às especificidades da UFBA, tais como a referência no cabeçalho do resumo e dimensões de margem e recuo.

## Trabalhos Futuros

Como desdobramentos futuros para a evolução desta ferramenta, recomenda-se:

- A disponibilização de um plugin ou extensão para o Visual Studio Code com pré-visualização em tempo real das páginas diagramadas;
- A integração com ferramentas de gerenciamento de bibliografia em nuvem (como Zotero e Mendeley) para sincronização automática de referências em BibTeX;
- A inclusão de scripts de verificação de plágio e conferência automática de citações órfãs antes da compilação final.
