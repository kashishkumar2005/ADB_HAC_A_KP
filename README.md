Approach
This solution takes a structured outline out of any PDF, finding the document title and hierarchical headings (H1, H2, H3) and their page numbers. The result is a tidy JSON file that reflects the document's logical structure, which can fuel more intelligent document navigation, indexing, or semantic analysis.

Extraction relies solely on layout and visual features, without any use of internet connectivity or external APIs. The core concept is to deduce document structure from font size, style, and position through PDF metadata.

Step-by-step:
Text Block Analysis: We use PyMuPDF to extract all the text blocks from the PDF along with their font size, flags (bold, etc.), and page location.

Body Size Detection: We figure out the most prevalent body font size throughout the document to use as body text. This serves as a starting point for heading detection.

Heading Detection: Blocks are sieved out with heuristics—brief text, title or all caps case, font size considerably bigger than body, and no footers, list items, or lengthy paragraphs.

Heading Level Classification:

H1 → Font size > 1.5× body size

H2 → Font size > 1.2× body size

H3 → Contenders left behind

Title Detection: The title is derived from the first line of page one or through keywords such as "Application Form" for form documents.

JSON Output: End output consists of the title and outline as a list of heading entries with level, text, and page number.

Used Libraries
PyMuPDF (fitz): For retrieving structured text, font metadata, and layout information from PDFs.

Python Standard Libraries: os, json, re, collections, argparse for file and command-line operations, regex filtering.

No machine learning models are employed. This guarantees rapid, deterministic performance and a small, offline-compatible solution.

Build & Run Instructions
Although our submission will be tested through the anticipated Docker execution pathway, here's how to manually build and run it:

Build Docker Image
docker build --platform linux/amd64 -t mysolution:extractor .

Run the Container
docker run --rm
-v $PWD/input:/app/input \
  -v $PWD/output:/app/output \
  --network none \
  mysolution:extractor

Put input PDFs in the /input directory.

Output JSON files go to /output with file names such as document_outline.json.
