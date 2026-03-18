"""
Document processing using GPT-4o multimodal.
Extracts real estate info from images, PDFs, and DOCX files.
Extracted text stored in DB and injected into agent prompt.
"""
import base64
from pathlib import Path
import httpx
from src.app.common import Settings


async def extract_text_from_document(file_path: str, file_type: str) -> str:
    file_type = file_type.lower().strip(".")

    if not Settings.openai_api_key:
        return f"Document uploaded: {Path(file_path).name}. OpenAI API key not configured — text extraction skipped."

    if file_type in ["jpg", "jpeg", "png", "gif", "webp", "bmp"]:
        return await _extract_from_image(file_path)
    elif file_type == "pdf":
        return await _extract_from_pdf(file_path)
    elif file_type in ["docx", "doc"]:
        return await _extract_from_docx(file_path)
    else:
        return await _extract_from_image(file_path)


async def _extract_from_image(file_path: str) -> str:
    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = Path(file_path).suffix.lower().strip(".")
    media_type = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg",
        "png": "image/png", "gif": "image/gif",
        "webp": "image/webp", "bmp": "image/bmp"
    }.get(ext, "image/jpeg")

    prompt = """You are processing a real estate project document.
    First extract all the data that is present in the image and 
    if there is information about the follwing fields, extract that as well: 
- Project Overview
- Location
- Unit Types & Sizes  
- Pricing
- Amenities
- Possession & RERA Details
- Payment Plans

There may be the floor plans or site plans embedded as images in the document, 
if you see any references to floor plans or site plans, extract those as well.
Try to understand the floor plan or site plan and extract the information that can be useful to a sales agent, 
such as unit layouts, key features, or unique selling points.Or Any other information that can be useful to a sales agent.

Raw text:
{raw_text[:8000]}

Provide clean, structured output with all key information preserved.
If there are sections with missing information, just skip those sections.
Extract EVERYTHING visible in the document."""

    return await _call_openai_vision(prompt, image_data, media_type)


async def _extract_from_pdf(file_path: str) -> str:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        all_text = []
        for page_num in range(min(len(doc), 10)):
            page = doc[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            image_data = base64.b64encode(pix.tobytes("png")).decode("utf-8")
            prompt = """You are processing a real estate project document.
    First extract all the data that is present in the image and 
    if there is information about the follwing fields, extract that as well: 
- Project Overview
- Location
- Unit Types & Sizes  
- Pricing
- Amenities
- Possession & RERA Details
- Payment Plans

There may be the floor plans or site plans embedded as images in the document, 
if you see any references to floor plans or site plans, extract those as well.
Try to understand the floor plan or site plan and extract the information that can be useful to a sales agent, 
such as unit layouts, key features, or unique selling points.Or Any other information that can be useful to a sales agent.

Raw text:
{raw_text[:8000]}

Provide clean, structured output with all key information preserved.
If there are sections with missing information, just skip those sections.
Extract EVERYTHING visible in the document."""
            text = await _call_openai_vision(prompt, image_data, "image/png")
            all_text.append(f"=== Page {page_num + 1} ===\n{text}")
        doc.close()
        return "\n\n".join(all_text)
    except ImportError:
        return await _extract_pdf_text_only(file_path)
    except Exception:
        return await _extract_pdf_text_only(file_path)


async def _extract_pdf_text_only(file_path: str) -> str:
    try:
        import PyPDF2
        text_parts = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages[:10]:
                text_parts.append(page.extract_text() or "")
        raw_text = "\n".join(text_parts)
        if raw_text.strip():
            return await _structure_text_with_gpt4(raw_text)
        return "PDF uploaded but no text could be extracted."
    except Exception as e:
        return f"PDF extraction failed: {str(e)}"


async def _extract_from_docx(file_path: str) -> str:
    try:
        from docx import Document
        doc = Document(file_path)
        text_parts = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)
        return await _structure_text_with_gpt4("\n".join(text_parts))
    except Exception as e:
        return f"DOCX extraction failed: {str(e)}"


async def _structure_text_with_gpt4(raw_text: str) -> str:
    prompt = f"""You are processing a real estate project document.
    First extract all the data that is present in the image and 
    if there is information about the follwing fields, extract that as well: 
- Project Overview
- Location
- Unit Types & Sizes  
- Pricing
- Amenities
- Possession & RERA Details
- Payment Plans

There may be the floor plans or site plans embedded as images in the document, 
if you see any references to floor plans or site plans, extract those as well.
Try to understand the floor plan or site plan and extract the information that can be useful to a sales agent, 
such as unit layouts, key features, or unique selling points.Or Any other information that can be useful to a sales agent.

Raw text:
{raw_text[:8000]}

Provide clean, structured output with all key information preserved.
If there are sections with missing information, just skip those sections.
Extract EVERYTHING visible in the document."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {Settings.openai_api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000},
            timeout=60.0
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Structuring failed: {data.get('error', {}).get('message', 'Unknown')}"


async def _call_openai_vision(prompt: str, image_data: str, media_type: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {Settings.openai_api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:{media_type};base64,{image_data}",
                            "detail": "high"
                        }}
                    ]
                }],
                "max_tokens": 2000
            },
            timeout=60.0
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Extraction error: {data.get('error', {}).get('message', 'Unknown error')}"
