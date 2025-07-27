import re
import os
import fitz
from collections import defaultdict

def is_list_item(line):
    """Check if a line is part of a bulleted/numbered list"""
    return (re.match(r'^\d+\.\s', line) or 
            re.match(r'^[•\-]\s', line) or
            re.match(r'^[a-z]\)\s', line))

def is_form_field(text):
    """Check if text is a form field label"""
    return (re.match(r'^\d+\.\s', text) or
            re.match(r'^[A-Z][a-z]+:', text) or
            text.strip().endswith(':'))

def is_heading_candidate(text, spans, body_size):
    """Determine if text is a likely heading candidate"""
    # Check font characteristics
    larger_font = any(span["size"] > body_size * 1.2 for span in spans)
    bold = any(span["flags"] & 2**4 for span in spans)  # Check bold flag
    
    # Check text characteristics
    short_text = len(text.split()) <= 8
    all_caps = text == text.upper()
    title_case = text == text.title()
    
    return larger_font or bold or all_caps or title_case

def analyze_text_blocks(doc):
    """Analyze document structure and text characteristics"""
    size_stats = defaultdict(int)
    blocks = []
    
    for page in doc:
        page_blocks = page.get_text("dict")["blocks"]
        for block in page_blocks:
            if "lines" in block:
                block_text = []
                block_spans = []
                for line in block["lines"]:
                    for span in line["spans"]:
                        size_stats[span["size"]] += 1
                        block_text.append(span["text"])
                        block_spans.append(span)
                
                full_text = "".join(block_text).strip()
                if full_text:
                    blocks.append({
                        "text": full_text,
                        "spans": block_spans,
                        "bbox": block["bbox"],
                        "page": page.number
                    })
    
    common_sizes = sorted(size_stats.items(), key=lambda x: -x[1])
    body_size = common_sizes[0][0] if common_sizes else 12
    
    return body_size, blocks

def is_heading_block(block, body_size, page_height):
    """Determine if a text block is a heading"""
    # Skip header/footer content
    y_pos = block["bbox"][3]  # Bottom y-coordinate
    if y_pos < page_height * 0.1 or y_pos > page_height * 0.9:
        return False
    
    # Skip very long blocks (likely paragraphs)
    if len(block["text"].split()) > 15:
        return False
    
    # Check if this looks like a heading
    if not is_heading_candidate(block["text"], block["spans"], body_size):
        return False
    
    # Additional checks to exclude paragraph fragments
    if (block["text"].endswith(('.', ',', ';', ':')) and 
        not block["text"].strip()[0].isupper()):
        return False
    
    return True

def detect_headings(pdf_path):
    """Main heading detection function"""
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text()
    
    # Special handling for form documents
    if "Application form" in first_page_text or "Form" in first_page_text:
        first_line = first_page_text.split('\n')[0].strip()
        return {
            "title": first_line if first_line else os.path.basename(pdf_path).replace('.pdf', ''),
            "outline": []
        }
    
    # Analyze document structure
    body_size, blocks = analyze_text_blocks(doc)
    outline = []
    page_heights = {page.number: page.rect.height for page in doc}
    
    for block in blocks:
        page_height = page_heights[block["page"]]
        
        if not is_heading_block(block, body_size, page_height):
            continue
            
        # Determine heading level
        max_size = max(span["size"] for span in block["spans"])
        if max_size > body_size * 1.5:
            level = "H1"
        elif max_size > body_size * 1.2:
            level = "H2"
        else:
            level = "H3"
        
        outline.append({
            "level": level,
            "text": block["text"],
            "page": block["page"] + 1
        })
    
    return {
        "title": os.path.basename(pdf_path).replace('.pdf', ''),
        "outline": outline
    }