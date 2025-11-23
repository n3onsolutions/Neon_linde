import os
import re
import tempfile
import pymupdf  # pymupdf (imported as `fitz` for brevity)
import pymupdf4llm   # provides `to_markdown`
from google import genai
from google.genai import types

from constants import SYSTEM_PROMPT

def extract_tables(input_pdf: str, table_img_dir: str, margin_vert: int = 20):
    """Extract tables from a PDF, save each as an image, and return markdown chunks.

    Returns:
        list: List of chunk dictionaries (as produced by pymupdf4llm.to_markdown)
    """
    os.makedirs(table_img_dir, exist_ok=True)
    doc = pymupdf.open(input_pdf)
    chunks = pymupdf4llm.to_markdown(
        doc,
        write_images=False,
        page_chunks=True,
    )
    for page_idx, page_dict in enumerate(chunks):
        page = doc[page_idx]
        tables = page_dict.get("tables", [])
        for tbl_idx, tbl in enumerate(tables):
            x0, y0, x1, y1 = tbl["bbox"]
            y0_adj = max(y0 - margin_vert, 0)
            y1_adj = min(y1 + margin_vert, page.rect.height)
            rect = pymupdf.Rect(x0, y0_adj, x1, y1_adj)
            mat = pymupdf.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, clip=rect)
            img_path = os.path.join(
                table_img_dir,
                f"page{page_idx + 1}_table{tbl_idx + 1}.png",
            )
            pix.save(img_path)
            # Insert markdown reference
            page_dict["text"] += f"\n\n![Table page{page_idx + 1}-{tbl_idx + 1}]({img_path})\n\n"
    return chunks

def write_markdown(output_md: str | None, chunks) -> str:
    """Write markdown to file (if provided) and also return the full markdown string."""
    full_text = ""
    for page in chunks:
        page_text = page["text"]
        full_text += page_text + "\n\n---\n\n"
            
    if output_md:
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(full_text)
            
    return full_text

def crear_mensaje(markdown_text: str, image_info_list):
    """Build the Gemini request payload.

    Args:
        markdown_text: Full markdown string.
        image_info_list: List of (title, path) tuples extracted from markdown.
    Returns:
        list of types.Content objects ready for `generate_content`.
    """
    parts = []
    parts.append(types.Part(text=SYSTEM_PROMPT))   
    parts.append(types.Part(text=markdown_text))
    for title, path in image_info_list:
        parts.append(types.Part(text=f"\n\nImage Reference: {title}"))
        try:
            with open(path, "rb") as f:
                img_bytes = f.read()
            parts.append(
                types.Part(
                    inline_data=types.Blob(mime_type="image/png", data=img_bytes),
                    media_resolution={"level": "media_resolution_high"},
                )
            )
        except Exception as e:
            parts.append(types.Part(text=f"[Error loading image: {path}]"))
    return [types.Content(parts=parts)]

def run_ai(full_markdown_text: str, analysis_output: str | None, model: str = "gemini-3.0-pro") -> str:
    """Send the markdown + images to Gemini and return the response text.
    
    Args:
        full_markdown_text: The complete markdown string.
        analysis_output: Optional path to save the response.
        model: Gemini model name.
    Returns:
        str: The analysis text.
    """
    pattern = r'!\[(.*?)\]\((.*?)\)'
    matches = re.findall(pattern, full_markdown_text)
    contents = crear_mensaje(full_markdown_text, matches)
    client = genai.Client(http_options={"api_version": "v1alpha"})
    response = client.models.generate_content(
        model=model,
        contents=contents,
    )
    if analysis_output:
        with open(analysis_output, "w", encoding="utf-8") as f:
            f.write(response.text)
    return response.text

def process_pdf(input_pdf: str, model: str = "gemini-3.0-pro") -> str:
    """Process a PDF and return the analysis text."""
    with tempfile.TemporaryDirectory() as table_img_dir:
        chunks = extract_tables(input_pdf, table_img_dir)
        full_md = write_markdown(None, chunks) 
        return run_ai(full_md, None, model=model)

def main(input_pdf: str, output_md: str = None, analysis_output: str = None):
    with tempfile.TemporaryDirectory() as table_img_dir:
        chunks = extract_tables(input_pdf, table_img_dir)
        full_md = write_markdown(output_md, chunks)
        if output_md:
            print(f"Markdown saved to {output_md}")
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.0-pro")
        result = run_ai(full_md, analysis_output, model=model_name)
        if analysis_output:
            print(f"Analysis saved to {analysis_output}")
        else:
            print("Analysis Result:")
            print(result)
