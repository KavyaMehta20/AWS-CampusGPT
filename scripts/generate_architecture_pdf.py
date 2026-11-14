"""Generate CampusGPT Architecture & Pipeline Guide PDF."""

import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

OUTPUT_PDF = Path("c:/Users/Kavya/Desktop/AWS/campusgpt/docs/CampusGPT_System_Architecture_and_Pipeline_Guide.pdf")
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Brand Colors: Navy #101B2D, Orange #E58A32, Slate #64748B, Bg #F8FAFC
    navy = colors.HexColor("#101B2D")
    orange = colors.HexColor("#E58A32")
    slate = colors.HexColor("#475569")
    light_slate = colors.HexColor("#F1F5F9")
    border_color = colors.HexColor("#CBD5E1")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=navy,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=orange,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=navy,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=orange,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=navy,
        backColor=light_slate,
        borderPadding=4,
        spaceAfter=6
    )

    table_header = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TC',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("CampusGPT: System Architecture & Engineering Guide", title_style))
    story.append(Paragraph("Workshop Reference for Presenters, Instructors & Technical Readers | 90-Minute Masterclass", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=orange, spaceAfter=12))

    # Executive Overview
    story.append(Paragraph("1. System Purpose & Core Philosophy", h1_style))
    story.append(Paragraph(
        "<b>CampusGPT</b> is an AI university assistant engineered around Google's modern Gemini API suite. "
        "The project demonstrates real-world AI application engineering: grounding an existing foundation model "
        "through deterministic retrieval, multi-checkpoint guardrails, external tool connectivity via Model Context Protocol (MCP), "
        "and serverless AWS deployment. We do <b>not</b> fine-tune or train any weights; rather, we control behavior via pipeline architecture.",
        body_style
    ))

    # Architecture Pipeline Flow Table
    story.append(Paragraph("2. The 7-Step End-to-End Pipeline Workflow", h1_style))
    story.append(Paragraph(
        "Every incoming query passes through a strict sequential flow orchestrated in <code>backend/app/pipeline.py</code> (~30 lines of readable code):",
        body_style
    ))

    pipeline_data = [
        [Paragraph("Pipeline Step", table_header), Paragraph("Key Concept", table_header), Paragraph("Folder & Code Location", table_header), Paragraph("Engineering Action", table_header)],
        [
            Paragraph("<b>Step 0</b>", table_cell),
            Paragraph("Ingestion", table_cell),
            Paragraph("backend/app/ingestion/<br/>scripts/ingest.py", table_cell),
            Paragraph("Parses PDF, DOCX, MD, TXT; extracts metadata (source, page, section); cleans junk/headers.", table_cell)
        ],
        [
            Paragraph("<b>Step 1</b>", table_cell),
            Paragraph("Chunking", table_cell),
            Paragraph("backend/app/chunking/<br/>scripts/inspect_chunks.py", table_cell),
            Paragraph("Segments text using 4 interchangeable strategies: Overlapping, Fixed, Structure-aware, Semantic.", table_cell)
        ],
        [
            Paragraph("<b>Step 2</b>", table_cell),
            Paragraph("Dense Embeddings", table_cell),
            Paragraph("backend/app/embeddings/<br/>scripts/show_embeddings.py", table_cell),
            Paragraph("Embeds chunks via gemini-embedding-001; MD5 disk cache prevents quota waste; cosine similarity math.", table_cell)
        ],
        [
            Paragraph("<b>Step 3</b>", table_cell),
            Paragraph("Vector Storage", table_cell),
            Paragraph("backend/app/vectorstore/<br/>vectorstore/", table_cell),
            Paragraph("Unified VectorStore interface: <b>ChromaDB</b> (local persistent) and <b>FAISS</b> (in-memory / AWS Lambda).", table_cell)
        ],
        [
            Paragraph("<b>Step 4</b>", table_cell),
            Paragraph("Candidate Retrieval", table_cell),
            Paragraph("backend/app/retrieval/", table_cell),
            Paragraph("Embeds student question, queries vector store for TOP_K_CANDIDATES (20), drops &lt; MIN_RELEVANCE.", table_cell)
        ],
        [
            Paragraph("<b>Step 5</b>", table_cell),
            Paragraph("Hybrid Reranking", table_cell),
            Paragraph("backend/app/reranking/", table_cell),
            Paragraph("Blends vector cosine similarity (60%) with lexical keyword overlap (40%) to pick FINAL_K (5) top chunks.", table_cell)
        ],
        [
            Paragraph("<b>Step 6</b>", table_cell),
            Paragraph("Grounded Synthesis", table_cell),
            Paragraph("backend/app/generation/", table_cell),
            Paragraph("Injects delimited context into Gemini 2.5 Flash; enforces in-line source citations and strict refusal fallback.", table_cell)
        ],
        [
            Paragraph("<b>Guardrails</b>", table_cell),
            Paragraph("3-Check Defense", table_cell),
            Paragraph("backend/app/guardrails/<br/>rules.yaml", table_cell),
            Paragraph("Input Guard (injection/length), Retrieval Guard (source/threshold), Output Guard (API key redaction/grounding).", table_cell)
        ],
        [
            Paragraph("<b>MCP Tools</b>", table_cell),
            Paragraph("Model Context Protocol", table_cell),
            Paragraph("mcp_server/<br/>backend/app/mcp_client/", table_cell),
            Paragraph("Decoupled tool server over stdio for course catalog lookup (courses.json) and academic dates (calendar.json).", table_cell)
        ]
    ]

    t = Table(pipeline_data, colWidths=[55, 95, 140, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_slate]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Page Break for Deep Dive
    story.append(PageBreak())

    # Deep Dive: Models & Rationale
    story.append(Paragraph("3. Model Specifications & Rationale", h1_style))
    story.append(Paragraph(
        "CampusGPT strictly adheres to verified, modern Google GenAI SDK standards as documented in <code>docs/VERIFIED_VERSIONS.md</code>:",
        body_style
    ))
    story.append(Paragraph("<b>Generation Model (<code>gemini-2.5-flash</code>):</b> High-speed workhorse model featuring built-in reasoning, low latency, and 1M context window. Configured with temperature 0.2 and <code>api_version='v1beta'</code> to enable developer system instructions.", body_style))
    story.append(Paragraph("<b>Embedding Model (<code>gemini-embedding-001</code>):</b> Google's active multimodal/text embedding backbone. Replaces retired models such as <code>text-embedding-004</code> (which returns 404). Converts text to dense vectors matching Euclidean/cosine distance.", body_style))
    story.append(Paragraph("<b>Crucial Teaching Distinction:</b> The embedding model and generation model perform two fundamentally different operations: embedding maps text to mathematical coordinates; generation synthesizes natural language.", body_style))

    # Guardrails Specification
    story.append(Paragraph("4. Multi-Layer Guardrail Defense Architecture", h1_style))
    story.append(Paragraph(
        "Prompt instructions alone are NOT a security boundary. CampusGPT enforces a three-checkpoint deterministic defense (Slide 13):",
        body_style
    ))

    guard_data = [
        [Paragraph("Checkpoint", table_header), Paragraph("Trigger & Validation Rule", table_header), Paragraph("System Action & Exact Output", table_header)],
        [
            Paragraph("<b>1. Input Guard</b><br/>(<code>input_guard.py</code>)", table_cell),
            Paragraph("• Empty or whitespace strings<br/>• Query length &gt; <code>MAX_QUESTION_CHARS</code> (500)<br/>• Prompt injection keywords ('ignore all instructions', 'reveal key', 'system prompt')", table_cell),
            Paragraph("Halts pipeline immediately. On injection or credentials request, returns EXACTLY:<br/><code>I can't provide private credentials or system information.</code>", table_cell)
        ],
        [
            Paragraph("<b>2. Retrieval Guard</b><br/>(<code>retrieval_guard.py</code>)", table_cell),
            Paragraph("• Unapproved document files<br/>• Relevance score &lt; <code>MIN_RELEVANCE</code> (0.25)<br/>• Indirect injection triggers hidden inside retrieved chunks", table_cell),
            Paragraph("Neutralizes indirect triggers with <code>[SANITIZED_INSTRUCTION]</code>. If 0 chunks qualify, skips LLM call and returns standard fallback refusal.", table_cell)
        ],
        [
            Paragraph("<b>3. Output Guard</b><br/>(<code>output_guard.py</code>)", table_cell),
            Paragraph("• Scans model text for Google API key patterns (regex: <code>AIza[0-9A-Za-z\\-_]{30,}</code>)<br/>• Grounding verification: must cite a retrieved chunk", table_cell),
            Paragraph("Replaces leaked secret tokens with <code>[REDACTED_SECRET]</code>. Replaces hallucinated or unsupported statements with fallback message.", table_cell)
        ]
    ]

    gt = Table(guard_data, colWidths=[100, 210, 230])
    gt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_slate]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(gt)
    story.append(Spacer(1, 12))

    # MCP Section
    story.append(Paragraph("5. Model Context Protocol (MCP) Integration", h1_style))
    story.append(Paragraph(
        "<b>Model Context Protocol (MCP)</b> is an open standard that decouples tool servers from host applications. "
        "Unlike hardcoded function calls, the MCP server runs independently in <code>mcp_server/server.py</code> over standard I/O (<code>stdio</code>):",
        body_style
    ))
    story.append(Paragraph("• <code>get_course_info(course_code)</code>: Queries structured course catalog (<code>data/raw/courses.json</code> or sample).", body_style))
    story.append(Paragraph("• <code>lookup_calendar_event(query)</code>: Queries academic calendar dates (<code>data/raw/calendar.json</code> or sample).", body_style))
    story.append(Paragraph("• <code>search_documents(query, k)</code>: Semantic search over the indexed knowledge base.", body_style))
    story.append(Paragraph("When <code>ENABLE_MCP=true</code> in <code>.env</code>, CampusGPT converts MCP tools to Gemini declarations, lets the model request an invocation, runs the tool through <code>CampusMCPClient</code>, and passes the result back to Gemini.", body_style))

    # Full Directory Reference
    story.append(PageBreak())
    story.append(Paragraph("6. Complete Repository Directory & File Inventory", h1_style))

    dir_data = [
        [Paragraph("Path / Folder", table_header), Paragraph("Key Files", table_header), Paragraph("Purpose & What It Stores", table_header)],
        [
            Paragraph("backend/app/", table_cell),
            Paragraph("main.py<br/>config.py<br/>schemas.py<br/>pipeline.py", table_cell),
            Paragraph("FastAPI core app. Serves HTML/JS frontend at '/', manages CORS, loads settings from .env, defines Pydantic data schemas.", table_cell)
        ],
        [
            Paragraph("backend/app/ingestion/", table_cell),
            Paragraph("loader.py", table_cell),
            Paragraph("Parses PDF (pypdf), DOCX (python-docx), MD, and TXT files into DocumentSnippets with page and section tags.", table_cell)
        ],
        [
            Paragraph("backend/app/chunking/", table_cell),
            Paragraph("fixed.py<br/>overlapping.py<br/>structure.py<br/>semantic.py", table_cell),
            Paragraph("Token approximation (words * 1.3) and chunk generators. Emits structured chunks to data/processed/chunks.jsonl.", table_cell)
        ],
        [
            Paragraph("backend/app/embeddings/", table_cell),
            Paragraph("client.py", table_cell),
            Paragraph("Gemini embedding client. Implements batching, exponential retry for 429 errors, disk cache in .cache/, and cosine similarity.", table_cell)
        ],
        [
            Paragraph("backend/app/vectorstore/", table_cell),
            Paragraph("chroma_store.py<br/>faiss_store.py", table_cell),
            Paragraph("Vector database implementations. ChromaDB persists locally in vectorstore/; FAISS exports binary indices for AWS Lambda.", table_cell)
        ],
        [
            Paragraph("backend/app/retrieval/", table_cell),
            Paragraph("retriever.py", table_cell),
            Paragraph("Embeds queries, executes top-K candidate search, and applies minimum relevance score filter.", table_cell)
        ],
        [
            Paragraph("backend/app/reranking/", table_cell),
            Paragraph("reranker.py", table_cell),
            Paragraph("Lexical hybrid reranker (cosine + keyword overlap), passthrough ('none'), or neural cross-encoders.", table_cell)
        ],
        [
            Paragraph("backend/app/generation/", table_cell),
            Paragraph("prompts.py<br/>generator.py", table_cell),
            Paragraph("Contains SYSTEM_PROMPT_TEMPLATE with citation rules; calls Gemini 2.5 Flash via google-genai v1beta endpoint.", table_cell)
        ],
        [
            Paragraph("backend/app/guardrails/", table_cell),
            Paragraph("input_guard.py<br/>retrieval_guard.py<br/>output_guard.py<br/>rules.yaml", table_cell),
            Paragraph("YAML-configurable rules for disallowed phrases, character limits, source allowlists, and secret redaction regexes.", table_cell)
        ],
        [
            Paragraph("data/raw/", table_cell),
            Paragraph("Discovering_Your_Major.md", table_cell),
            Paragraph("Primary Knowledge Base: Real RIT Dubai Academic Advising document with core business, MIS, Finance, and GenEd policies.", table_cell)
        ],
        [
            Paragraph("data/sample/", table_cell),
            Paragraph("handbook.md<br/>courses.json<br/>calendar.json", table_cell),
            Paragraph("Fictional fallback dataset clearly marked as sample data for day-one offline verification.", table_cell)
        ],
        [
            Paragraph("frontend/", table_cell),
            Paragraph("index.html<br/>styles.css<br/>app.js<br/>config.js", table_cell),
            Paragraph("Plain HTML5/CSS/JS frontend (Navy #101B2D, Orange #E58A32). Includes 'How CampusGPT answered' collapsible trace panel.", table_cell)
        ],
        [
            Paragraph("scripts/", table_cell),
            Paragraph("ingest.py<br/>ask_cli.py<br/>test_injection.py<br/>mcp_demo.py", table_cell),
            Paragraph("Standalone CLI utilities mapping 1-to-1 with presentation slide concepts.", table_cell)
        ],
        [
            Paragraph("deploy/aws/", table_cell),
            Paragraph("template.yaml<br/>lambda_handler.py<br/>DEPLOY_GUIDE.md", table_cell),
            Paragraph("AWS SAM Serverless template: Lambda + Mangum, HTTP API Gateway, Secrets Manager cold-start fetching, and S3.", table_cell)
        ]
    ]

    dt = Table(dir_data, colWidths=[110, 150, 280])
    dt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_slate]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(dt)

    doc.build(story)
    print(f"✓ PDF generated successfully at: {OUTPUT_PDF}")

if __name__ == "__main__":
    build_pdf()
