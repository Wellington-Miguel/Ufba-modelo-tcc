# Revisão de Literatura

A fundamentação teórica deste trabalho apoia-se em dois eixos complementares: a normalização documentária aplicada ao ambiente universitário da Universidade Federal da Bahia e os princípios de interação com Modelos de Linguagem de Grande Porte voltados à redação acadêmica modular.

## As Normas ABNT e o Manual de Estilo Acadêmico da EDUFBA

A padronização dos trabalhos acadêmicos no Brasil é regida por um conjunto de normas emitidas pela Associação Brasileira de Normas Técnicas. Conforme exposto por Severino [@Severino2016], a normalização não se limita a exigências burocráticas, mas constitui elemento essencial para a circulação pública e indexação de resultados científicos.

Na UFBA, a referência oficial para formatação é o Manual de Estilo Acadêmico da EDUFBA [@EDUFBA2019], atualmente em sua 6ª edição revista e ampliada. Esse manual compila e exemplifica a aplicação de normas cruciais:

1. **ABNT NBR 14724:2011**: Estrutura geral dos trabalhos acadêmicos (elementos pré-textuais, textuais e pós-textuais);
2. **ABNT NBR 6023:2018**: Regras para elaboração de referências bibliográficas;
3. **ABNT NBR 10520:2002**: Apresentação de citações diretas, indiretas e notas de rodapé;
4. **ABNT NBR 6028:2003**: Requisitos para resumos e palavras-chave (150 a 500 palavras);
5. **ABNT NBR 6024:2012**: Numeração progressiva das seções de um documento escrito.

### Requisitos Gráficos e Tipográficos

O Manual da EDUFBA estabelece diretrizes rigorosas para a apresentação gráfica, sintetizadas na Tabela 1.

| Elemento Gráfico | Dimensão / Configuração Normativa | Observações UFBA (EDUFBA 2019) |
| :--- | :--- | :--- |
| Margem Superior | 3,0 cm | Aplicável ao anverso da folha |
| Margem Esquerda | 3,0 cm | Espaço destinado à encadernação |
| Margem Inferior | 2,0 cm | Padrão ABNT |
| Margem Direita | 2,0 cm | Padrão ABNT |
| Recuo de Parágrafo | 1,0 cm | Primeira linha do parágrafo |
| Citação Longa (> 3 linhas) | Recuo de 4,0 cm | Fonte menor (10 ou 11pt), espaço simples |
| Espaçamento Entrelinhas | 1,5 linha | Corpo do texto principal |
| Fonte Tipográfica | Tamanho 12 | Latin Modern, Times New Roman ou Arial |
*Fonte: Adaptado de Lubisco e Vieira [@EDUFBA2019, p. 85-86].*

Segundo orienta a norma, as ilustrações (figuras, gráficos, fotografias) e tabelas devem conter identificação na parte superior e a respectiva fonte na parte inferior, ambas em corpo menor (10 ou 11 pt) e espaçamento simples.

## Modelos de Linguagem e Escrita Modular

A arquitetura *Transformer*, introduzida por Vaswani et al. [@Vaswani2017], viabilizou saltos qualitativos no processamento de linguagem natural, culminando em modelos densos como o GPT-3 [@Brown2020] e seus sucessores contemporâneos. Esses modelos exibem alta capacidade de síntese e estruturação argumentativa.

Entretanto, ao redigir monografias completas, surgem problemas conhecidos como perda de coerência em contextos longos (*lost-in-the-middle*) e limites estritos de geração por resposta. Por esse motivo, Gil [@Gil2019] salienta que qualquer produção científica requer um delineamento prévio em tópicos bem delimitados.

A abordagem modular resolve esse gargalo ao decompor a monografia em blocos temáticos autônomos expressos em Markdown, permitindo:

- Redação iterativa e assistida seção por seção;
- Validação contínua do conteúdo pelo autor e orientador;
- Armazenamento em arquivos de texto simples, compatíveis com sistemas de controle de versão como o Git.
