import argparse
import os
import sys
import json
from utils import detect_headings

def process_pdf(input_path, output_path):
    """Process a single PDF file and save as JSON"""
    try:
        print(f"Processing {os.path.basename(input_path)}...")
        result = detect_headings(input_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Results saved to {output_path}")
    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description='PDF Heading Detector')
    parser.add_argument('--input-dir', default='/app/input', help='Input directory for PDFs')
    parser.add_argument('--output-dir', default='/app/output', help='Output directory for results')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    for filename in os.listdir(args.input_dir):
        if filename.lower().endswith('.pdf'):
            input_path = os.path.join(args.input_dir, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_outline.json"
            output_path = os.path.join(args.output_dir, output_filename)
            process_pdf(input_path, output_path)

if __name__ == "__main__":
    main()