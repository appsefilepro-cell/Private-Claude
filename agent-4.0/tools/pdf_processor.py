"""
PDF Processing Toolkit for Agent 4.0 Advanced
Handles PDF reading, parsing, extraction, generation, and more
"""

import os
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import PyPDF2
    import pdfplumber
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    logger.warning("PDF processing dependencies not installed. Install with: pip install PyPDF2 pdfplumber reportlab")
    # Define placeholders for missing dependencies
    letter = (612, 792)  # 8.5 x 11 inches in points
    A4 = (595, 842)  # A4 size in points


class PDFProcessor:
    """Main PDF processing class"""
    
    def __init__(self):
        if not DEPS_AVAILABLE:
            logger.warning("PDF processing disabled - dependencies not available")
        self.supported_operations = [
            'read', 'parse', 'extract_text', 'extract_images',
            'extract_tables', 'generate', 'merge', 'split',
            'sign', 'encrypt', 'decrypt', 'compress'
        ]
    
    def read_pdf(self, file_path: str) -> Dict:
        """
        Read PDF and return metadata and content
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with metadata and content
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'info': pdf_reader.metadata,
                    'encrypted': pdf_reader.is_encrypted,
                }
                
                # Extract text from all pages
                text_content = []
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content.append({
                        'page': page_num + 1,
                        'text': page.extract_text()
                    })
                
                return {
                    'success': True,
                    'metadata': metadata,
                    'content': text_content,
                    'file_path': file_path
                }
                
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_text(self, file_path: str, page_numbers: Optional[List[int]] = None) -> Dict:
        """
        Extract text from specific pages or all pages
        
        Args:
            file_path: Path to PDF file
            page_numbers: List of page numbers (1-indexed) or None for all pages
            
        Returns:
            Dictionary with extracted text
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_text = []
                
                pages_to_process = page_numbers if page_numbers else range(1, len(pdf.pages) + 1)
                
                for page_num in pages_to_process:
                    if 1 <= page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]
                        text = page.extract_text()
                        extracted_text.append({
                            'page': page_num,
                            'text': text
                        })
                
                return {
                    'success': True,
                    'extracted_text': extracted_text,
                    'total_pages': len(pdf.pages)
                }
                
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_tables(self, file_path: str, page_numbers: Optional[List[int]] = None) -> Dict:
        """
        Extract tables from PDF
        
        Args:
            file_path: Path to PDF file
            page_numbers: List of page numbers (1-indexed) or None for all pages
            
        Returns:
            Dictionary with extracted tables
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                extracted_tables = []
                
                pages_to_process = page_numbers if page_numbers else range(1, len(pdf.pages) + 1)
                
                for page_num in pages_to_process:
                    if 1 <= page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]
                        tables = page.extract_tables()
                        if tables:
                            extracted_tables.append({
                                'page': page_num,
                                'tables': tables,
                                'table_count': len(tables)
                            })
                
                return {
                    'success': True,
                    'tables': extracted_tables,
                    'total_tables': sum(t['table_count'] for t in extracted_tables)
                }
                
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_pdf(
        self,
        output_path: str,
        content: Union[str, List[Dict]],
        title: str = "Generated Document",
        author: str = "Agent X5.0",
        page_size: tuple = letter
    ) -> Dict:
        """
        Generate a PDF document
        
        Args:
            output_path: Path to save generated PDF
            content: String or list of content dictionaries
            title: Document title
            author: Document author
            page_size: Page size (letter, A4, etc.)
            
        Returns:
            Dictionary with generation results
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            c = canvas.Canvas(output_path, pagesize=page_size)
            c.setTitle(title)
            c.setAuthor(author)
            
            # Set up initial position
            width, height = page_size
            x = 72  # 1 inch margin
            y = height - 72
            
            if isinstance(content, str):
                # Simple text content
                lines = content.split('\n')
                for line in lines:
                    if y < 72:  # Bottom margin reached
                        c.showPage()
                        y = height - 72
                    c.drawString(x, y, line)
                    y -= 14  # Line spacing
            
            elif isinstance(content, list):
                # Structured content
                for item in content:
                    if y < 72:
                        c.showPage()
                        y = height - 72
                    
                    if item.get('type') == 'title':
                        c.setFont("Helvetica-Bold", 16)
                        c.drawString(x, y, item.get('text', ''))
                        y -= 24
                    elif item.get('type') == 'text':
                        c.setFont("Helvetica", 12)
                        text = item.get('text', '')
                        # Word wrap
                        words = text.split()
                        line = ""
                        for word in words:
                            if c.stringWidth(line + " " + word) < (width - 144):
                                line += " " + word if line else word
                            else:
                                c.drawString(x, y, line)
                                y -= 14
                                line = word
                        if line:
                            c.drawString(x, y, line)
                            y -= 14
            
            c.save()
            
            return {
                'success': True,
                'output_path': output_path,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return {'success': False, 'error': str(e)}
    
    def merge_pdfs(self, input_paths: List[str], output_path: str) -> Dict:
        """
        Merge multiple PDFs into one
        
        Args:
            input_paths: List of PDF file paths to merge
            output_path: Path to save merged PDF
            
        Returns:
            Dictionary with merge results
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            pdf_merger = PyPDF2.PdfMerger()
            
            for pdf_path in input_paths:
                pdf_merger.append(pdf_path)
            
            pdf_merger.write(output_path)
            pdf_merger.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'merged_files': len(input_paths)
            }
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            return {'success': False, 'error': str(e)}
    
    def split_pdf(self, input_path: str, output_dir: str, pages_per_file: int = 1) -> Dict:
        """
        Split PDF into multiple files
        
        Args:
            input_path: Path to PDF file
            output_dir: Directory to save split PDFs
            pages_per_file: Number of pages per output file
            
        Returns:
            Dictionary with split results
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with open(input_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                output_files = []
                for i in range(0, total_pages, pages_per_file):
                    pdf_writer = PyPDF2.PdfWriter()
                    
                    for page_num in range(i, min(i + pages_per_file, total_pages)):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    output_filename = f"split_{i // pages_per_file + 1}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    
                    output_files.append(output_path)
                
                return {
                    'success': True,
                    'output_files': output_files,
                    'total_files': len(output_files)
                }
                
        except Exception as e:
            logger.error(f"Error splitting PDF: {e}")
            return {'success': False, 'error': str(e)}
    
    def encrypt_pdf(self, input_path: str, output_path: str, password: str) -> Dict:
        """
        Encrypt a PDF with password
        
        Args:
            input_path: Path to PDF file
            output_path: Path to save encrypted PDF
            password: Password for encryption
            
        Returns:
            Dictionary with encryption results
        """
        if not DEPS_AVAILABLE:
            return {'error': 'Dependencies not available'}
        
        try:
            with open(input_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
                
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                pdf_writer.encrypt(password)
                
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            return {
                'success': True,
                'output_path': output_path,
                'encrypted': True
            }
            
        except Exception as e:
            logger.error(f"Error encrypting PDF: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Example usage"""
    processor = PDFProcessor()
    
    # Get agent version from environment or use default
    agent_name = os.environ.get('AGENT_VERSION', 'Agent 4.0 Advanced')
    
    print("=== PDF Processor Toolkit ===")
    print(f"Supported operations: {', '.join(processor.supported_operations)}")
    print(f"Dependencies available: {DEPS_AVAILABLE}")
    
    # Example: Generate a simple PDF
    content = [
        {'type': 'title', 'text': f'{agent_name} Report'},
        {'type': 'text', 'text': f'This is an automated report generated by {agent_name} system.'},
        {'type': 'text', 'text': f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'},
    ]
    
    result = processor.generate_pdf(
        output_path='/tmp/agent_report.pdf',
        content=content,
        title=f'{agent_name} Report'
    )
    
    if result.get('success'):
        print(f"\n✓ PDF generated successfully: {result['output_path']}")
    else:
        print(f"\n✗ PDF generation failed: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    main()
