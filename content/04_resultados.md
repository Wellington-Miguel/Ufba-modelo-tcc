# Resultados e Discussão

Este capítulo apresenta a validação do pipeline proposto, analisando a conformidade tipográfica perante o Manual de Estilo Acadêmico da EDUFBA [@EDUFBA2019] e o ganho de produtividade obtido na redação assistida por modelos de linguagem.

## Conformidade com as Diretrizes da EDUFBA

A análise do documento compilado atesta o atendimento integral a todos os quesitos avaliados pelas bancas examinadoras e bibliotecas da UFBA:

1. **Capa e Folha de Rosto**: Exibem o brasão oficial da UFBA, hierarquia tipográfica correta (16pt para instituição/título, 14pt para unidade/autor, 12pt para programa) e alinhamento do preâmbulo à direita;
2. **Resumo e Abstract**: Incluem no topo a referência catalográfica padronizada da própria monografia, diferencial exigido pela UFBA que frequentemente é omitido em modelos genéricos;
3. **Seções Progressivas**: Aplicação exata da NBR 6024:2012, com capítulos primários em maiúsculas negrito, secundários em maiúsculas redondo, e terciários em minúsculas com inicial maiúscula e negrito;
4. **Figuras e Tabelas**: Inclusão automática de legendas superiores e fontes inferiores em corpo 10/11 pt com entrelinha simples;
5. **Citações e Referências**: Mapeamento transparente para o pacote `abntex2cite` em modo autor-data com alinhamento à margem esquerda.

A Tabela 2 apresenta uma análise comparativa entre os métodos tradicionais de escrita em LaTeX e o presente framework baseado em Markdown.

| Critério de Avaliação | Escrita Direta em LaTeX | Framework Markdown + abnTeX2 |
| :--- | :--- | :--- |
| Curva de Aprendizado | Elevada (comandos complexos) | Baixa (sintaxe amigável) |
| Compatibilidade com LLMs | Média (LLM erra comandos TeX) | Nativa (Markdown é o padrão de LLMs) |
| Modulariedade do Texto | Exige manipulação de `\input` | Automática por arquivos numerados |
| Inserção de Figuras/Fontes | Bloco manual de 8 linhas TeX | 2 linhas em Markdown |
| Risco de Quebra de Sintaxe | Frequente em tabelas e equações | Mitigado pelo parser automatizado |
*Fonte: Elaborado pelo autor (2026).*

## Guia Prático de Prompts para Interação com LLM

Para assegurar que as respostas geradas pela LLM se integrem perfeitamente ao projeto sem necessidade de ajustes manuais, recomenda-se fornecer um prompt de sistema contendo as seguintes diretrizes:

```text
Você é um assistente acadêmico auxiliando na redação do meu TCC para a UFBA.
Ao redigir as seções:
1. Responda em Markdown padrão com títulos iniciando em nível 2 (##) ou 3 (###);
2. Não inclua números manuais nos títulos (ex: use '## Contextualização' e não '## 1.1 Contextualização');
3. Utilize citações no formato BibTeX: [@AutorAno] ou 'Segundo @AutorAno';
4. Para citações diretas longas com mais de 3 linhas, use o bloco de citação '> texto da citação';
5. Para figuras, utilize '![Legenda da figura](images/nome.png)' seguido de '*Fonte: Autor (2026).*';
6. Mantenha tom acadêmico formal, impessoal e fundamentado na literatura científica.
```

Essa padronização simplifica o processo de cópia e colagem, permitindo que cada resposta da IA seja salva diretamente no respectivo arquivo `.md`.
