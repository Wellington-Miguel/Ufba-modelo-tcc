"""
Gera os 3 diagramas em PNG (1600x900) com fontes TrueType UTF-8 (Arial) completas,
garantindo acentos perfeitos sem caixas de caracteres faltantes (quadradinhos).
"""
import os
from PIL import Image, ImageDraw, ImageFont

FONT_TITLE_PATH = r"C:\Windows\Fonts\arialbd.ttf"
FONT_BODY_PATH = r"C:\Windows\Fonts\arial.ttf"

font_header_title = ImageFont.truetype(FONT_TITLE_PATH, 28)
font_header_sub = ImageFont.truetype(FONT_BODY_PATH, 20)
font_card_title = ImageFont.truetype(FONT_TITLE_PATH, 22)
font_bullet = ImageFont.truetype(FONT_BODY_PATH, 19)
font_footer = ImageFont.truetype(FONT_BODY_PATH, 16)

DIAGRAMS = [
    {
        "filename": "images/arquitetura_assistente.png",
        "header_title": "ARQUITETURA EM ESTÁGIOS: ASSISTENTE DE OBSERVABILIDADE SOCIOTÉCNICA",
        "header_subtitle": "Fluxo Integrado de Prevenção, Validação e Diagnóstico Forense",
        "cards": [
            {
                "title": "Momento 1: Pre-Flight Data Profiler (Tempo Zero / Cliente)",
                "bullets": [
                    "• Entrada: Arquivo bruto do usuário (CSV, RIS, WOS, ZIP, JSON, XML)",
                    "• Ação: Validação determinística estática em Python/Pandas (charset UTF-8, delimitador, colunas mínimas)",
                    "• Saída: Semáforo visual (Verde/Amarelo/Vermelho) + Radiografia JSON salva em st.session_state",
                ],
                "border": (59, 130, 246),
                "fill": (239, 246, 255),
            },
            {
                "title": "Momento 2: Early-Warning Parser (Pós-Ingestão / Pré-Processamento)",
                "bullets": [
                    "• Entrada: Banco de dados relacional SQLite (.db) gerado pelo parser legado do CorText",
                    "• Ação: Inspeção de volumetria e validação de matriz de adjacência antes de submeter à fila",
                    "• Saída: Alerta preventivo se tabelas críticas resultarem vazias (evita erro 'network you produced is empty')",
                ],
                "border": (34, 197, 94),
                "fill": (240, 253, 244),
            },
            {
                "title": "Momento 3: Log Explainer & RAG Forense (Execução / Pós-Falha)",
                "bullets": [
                    "• Entrada: Mensagem de erro / log do servidor ('No logs found', estouro de memória)",
                    "• Ação: Recuperação aumentada no fórum oficial (ChromaDB) + Radiografia JSON + Ollama Local",
                    "• Saída: Diagnóstico pedagógico explicativo e passo a passo acionável de correção sem alucinações",
                ],
                "border": (239, 68, 68),
                "fill": (254, 242, 242),
            },
        ],
    },
    {
        "filename": "images/tela_profiler_placeholder.png",
        "header_title": "INTERFACE DO MÓDULO PRE-FLIGHT DATA PROFILER (STREAMLIT)",
        "header_subtitle": "Auditoria e Semáforo Preventivo de Conformidade Estrutural",
        "cards": [
            {
                "title": "Painel de Upload e Reconhecimento Automático",
                "bullets": [
                    "• Upload via Drag-and-Drop suportando múltiplos dialetos científicos",
                    "• Detecção em tempo real de codificação de caracteres (UTF-8 com ou sem BOM vs Windows-1252)",
                    "• Inferência de delimitador de colunas (vírgula, ponto-e-vírgula, tabulação)",
                ],
                "border": (59, 130, 246),
                "fill": (239, 246, 255),
            },
            {
                "title": "Diagnóstico e Semáforo de Conformidade",
                "bullets": [
                    "• Indicador Visual: Verde (Apto) / Amarelo (Avisos de Coerção) / Vermelho (Erros Obstativo)",
                    "• Tabela de Inconsistências: Apontamento exato de número de linha e cabeçalho violado",
                    "• Sugestão automática de correção antes de submeter ao CorText Manager",
                ],
                "border": (34, 197, 94),
                "fill": (240, 253, 244),
            },
            {
                "title": "Armazenamento Transparente de Metadados",
                "bullets": [
                    "• Radiografia estrutural serializada na sessão do navegador",
                    "• Preparação de contexto enriquecido para o módulo de IA RAG caso necessário",
                ],
                "border": (239, 68, 68),
                "fill": (254, 242, 242),
            },
        ],
    },
    {
        "filename": "images/tela_rag_placeholder.png",
        "header_title": "INTERFACE DO MÓDULO LOG EXPLAINER & RAG (STREAMLIT)",
        "header_subtitle": "Diagnóstico Pedagógico com Memória Técnica do Fórum CorText",
        "cards": [
            {
                "title": "Entrada de Logs e Captura de Falhas",
                "bullets": [
                    "• Campo de texto para colagem direta do log do CorText ('No logs found', traceback Python)",
                    "• Recuperação automática da radiografia do arquivo submetido no Tempo Zero",
                ],
                "border": (59, 130, 246),
                "fill": (239, 246, 255),
            },
            {
                "title": "Consulta Vetorial Semântica (ChromaDB)",
                "bullets": [
                    "• Busca nos 298 tópicos do acervo histórico auditado do fórum oficial",
                    "• Filtro por soluções validadas pela equipe técnica oficial (Staff as Human Parser)",
                ],
                "border": (34, 197, 94),
                "fill": (240, 253, 244),
            },
            {
                "title": "Geração Explicativa via LLM Local (Ollama)",
                "bullets": [
                    "• Explicação em linguagem natural (Português/Inglês/Francês) sem jargões opacos",
                    "• Instruções práticas de descompactação de ZIPs aninhados e reparo de cabeçalhos corrompidos",
                ],
                "border": (239, 68, 68),
                "fill": (254, 242, 242),
            },
        ],
    },
]

def render_diagram(data):
    im = Image.new("RGB", (1600, 900), color=(248, 249, 250))
    draw = ImageDraw.Draw(im)

    # Moldura externa sutil
    draw.rectangle([10, 10, 1590, 890], outline=(15, 23, 42), width=2)

    # Header
    draw.rectangle([20, 20, 1580, 140], fill=(30, 41, 59))
    draw.text((45, 40), data["header_title"], font=font_header_title, fill=(255, 255, 255))
    draw.text((45, 90), data["header_subtitle"], font=font_header_sub, fill=(203, 213, 225))

    # Cards
    card_positions = [
        (50, 180, 1550, 380),
        (50, 410, 1550, 610),
        (50, 640, 1550, 840),
    ]

    for idx, card in enumerate(data["cards"]):
        pos = card_positions[idx]
        draw.rectangle(pos, fill=card["fill"], outline=card["border"], width=2)
        
        # Card title
        draw.text((pos[0] + 25, pos[1] + 22), card["title"], font=font_card_title, fill=(15, 23, 42))

        # Bullets
        for b_idx, bullet in enumerate(card["bullets"]):
            y_bullet = pos[1] + 68 + (b_idx * 34)
            draw.text((pos[0] + 25, y_bullet), bullet, font=font_bullet, fill=(30, 41, 59))

    # Footer
    draw.text((50, 855), "TCC UFBA - Espaço Reservado para Artefato Visual / Diagrama Final", font=font_footer, fill=(100, 116, 139))

    os.makedirs(os.path.dirname(data["filename"]), exist_ok=True)
    im.save(data["filename"], format="PNG")
    print(f"Salvo com sucesso: {data['filename']}")

if __name__ == "__main__":
    for d in DIAGRAMS:
        render_diagram(d)
