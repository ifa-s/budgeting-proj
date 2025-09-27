"""
PDF Processing and Analysis Services
"""
import re
import pdfplumber
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service class for processing PDF bank statements and extracting transaction data"""
    
    def __init__(self):
        # Common patterns for different banks
        self.date_patterns = [
            r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',  # MM/DD/YYYY, MM-DD-YYYY
            r'(\d{2,4}[/\-]\d{1,2}[/\-]\d{1,2})',  # YYYY/MM/DD, YYYY-MM-DD
        ]
        
        # Pattern to match transaction lines (date + amount)
        self.transaction_patterns = [
            # Pattern for most common bank statement formats
            r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\s+([^\$]*?)\s+[\$]?([\d,]+\.?\d*)',
            # Alternative pattern with different spacing
            r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}).*?([A-Za-z].*?)\s+([\d,]+\.?\d*)',
        ]
        
        # Common transaction type keywords
        self.debit_keywords = [
            'purchase', 'withdrawal', 'debit', 'payment', 'transfer out',
            'check', 'fee', 'charge', 'atm', 'pos', 'online'
        ]
        
        self.credit_keywords = [
            'deposit', 'credit', 'transfer in', 'refund', 'interest',
            'dividend', 'salary', 'payroll', 'direct deposit'
        ]
        
        # Category mapping based on merchant/description patterns
        self.category_patterns = {
            'groceries': r'(walmart|kroger|publix|safeway|whole foods|trader joe|grocery|supermarket)',
            'restaurants': r'(restaurant|mcdonald|burger|pizza|starbucks|coffee|cafe|dining)',
            'gas': r'(shell|exxon|bp|chevron|mobil|gas|fuel|station)',
            'shopping': r'(amazon|target|best buy|mall|store|retail|shopping)',
            'entertainment': r'(netflix|spotify|movie|theater|game|entertainment|streaming)',
            'utilities': r'(electric|water|gas company|utility|internet|phone|cable)',
            'transportation': r'(uber|lyft|taxi|bus|train|metro|parking|toll)',
            'healthcare': r'(medical|doctor|hospital|pharmacy|health|dental|vision)',
            'education': r'(tuition|school|college|university|textbook|student)',
            'banking': r'(bank|fee|atm|overdraft|transfer|interest)',
        }

    def extract_complete_pdf_content(self, pdf_file) -> Dict:
        """Extract complete PDF content formatted for Gemini AI analysis"""
        try:
            content = {
                'raw_text': "",
                'structured_tables': [],
                'metadata': {},
                'formatted_content': ""
            }
            
            with pdfplumber.open(pdf_file) as pdf:
                # Extract metadata
                content['metadata'] = {
                    'total_pages': len(pdf.pages),
                    'page_count': len(pdf.pages)
                }
                
                formatted_text = "=== BANK STATEMENT PDF CONTENT ===\n\n"
                
                for page_num, page in enumerate(pdf.pages, 1):
                    formatted_text += f"--- PAGE {page_num} ---\n"
                    
                    # Extract text content
                    page_text = page.extract_text()
                    if page_text:
                        content['raw_text'] += page_text + "\n"
                        formatted_text += page_text + "\n"
                    
                    # Extract tables with structure
                    tables = page.extract_tables()
                    if tables:
                        formatted_text += "\n=== TABLES ON PAGE {} ===\n".format(page_num)
                        
                        for table_idx, table in enumerate(tables):
                            formatted_text += f"\nTable {table_idx + 1}:\n"
                            table_data = []
                            
                            for row_idx, row in enumerate(table):
                                if row and any(cell and str(cell).strip() for cell in row):  # Skip empty rows
                                    clean_row = [str(cell).strip() if cell else "" for cell in row]
                                    table_data.append(clean_row)
                                    
                                    # Format for display
                                    formatted_text += " | ".join(clean_row) + "\n"
                            
                            if table_data:
                                content['structured_tables'].append({
                                    'page': page_num,
                                    'table_index': table_idx,
                                    'data': table_data
                                })
                    
                    formatted_text += "\n" + "="*50 + "\n"
                
                content['formatted_content'] = formatted_text
                
                if not content['raw_text'].strip() and not content['structured_tables']:
                    raise Exception("No readable content found in PDF")
                
                return content
                
        except Exception as e:
            logger.error(f"Error extracting complete PDF content: {str(e)}")
            raise Exception(f"Failed to extract PDF content: {str(e)}")

    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text content from PDF file using pdfplumber for better accuracy"""
        try:
            text = ""
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    # Extract text from the page
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Also try to extract tables which are common in bank statements
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:  # Skip empty rows
                                row_text = " | ".join([cell or "" for cell in row])
                                text += row_text + "\n"
            
            if not text.strip():
                raise Exception("No text content found in PDF")
                
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def extract_structured_data(self, pdf_file) -> Dict:
        """Extract structured data including tables from bank statements"""
        try:
            all_text = ""
            all_tables = []
            
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + "\n"
                    
                    # Extract tables with better structure preservation
                    tables = page.extract_tables()
                    for table in tables:
                        if table and len(table) > 1:  # Skip empty or single-row tables
                            all_tables.append(table)
            
            return {
                'text': all_text,
                'tables': all_tables,
                'raw_content': all_text  # For backward compatibility
            }
            
        except Exception as e:
            logger.error(f"Error extracting structured data from PDF: {str(e)}")
            raise Exception(f"Failed to extract structured data: {str(e)}")

    def parse_transactions(self, text: str) -> List[Dict]:
        """Parse transaction data from extracted text"""
        transactions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match transaction patterns
            for pattern in self.transaction_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        transaction = self._parse_transaction_line(match, line)
                        if transaction:
                            transactions.append(transaction)
                            break
                    except Exception as e:
                        logger.warning(f"Failed to parse transaction line: {line}. Error: {str(e)}")
                        continue
        
        # Remove duplicates and sort by date
        unique_transactions = self._remove_duplicate_transactions(transactions)
        return sorted(unique_transactions, key=lambda x: x['date'], reverse=True)

    def parse_transactions_from_tables(self, tables: List[List]) -> List[Dict]:
        """Parse transactions from structured table data"""
        transactions = []
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Try to identify the header row and transaction rows
            header_row = table[0] if table else []
            
            # Look for common bank statement column headers
            date_col = self._find_column_index(header_row, ['date', 'transaction date', 'posted date'])
            desc_col = self._find_column_index(header_row, ['description', 'transaction', 'memo', 'details'])
            amount_col = self._find_column_index(header_row, ['amount', 'debit', 'credit', 'transaction amount'])
            
            # If we can't find standard columns, try to parse each row as potential transaction data
            for row_idx, row in enumerate(table[1:], 1):  # Skip header
                if not row or len(row) < 3:
                    continue
                
                try:
                    transaction = self._parse_table_row(row, date_col, desc_col, amount_col)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    logger.warning(f"Failed to parse table row {row_idx}: {row}. Error: {str(e)}")
                    continue
        
        # Remove duplicates and sort by date
        unique_transactions = self._remove_duplicate_transactions(transactions)
        return sorted(unique_transactions, key=lambda x: x['date'], reverse=True)

    def _find_column_index(self, header_row: List[str], possible_names: List[str]) -> Optional[int]:
        """Find the column index for a given header type"""
        if not header_row:
            return None
        
        for idx, header in enumerate(header_row):
            if header and isinstance(header, str):
                header_lower = header.lower().strip()
                for name in possible_names:
                    if name in header_lower:
                        return idx
        return None

    def _parse_table_row(self, row: List[str], date_col: Optional[int], 
                        desc_col: Optional[int], amount_col: Optional[int]) -> Optional[Dict]:
        """Parse a single table row into a transaction"""
        try:
            # Try to extract date, description, and amount from the row
            date_str = None
            description = ""
            amount_str = ""
            
            # Use column indices if available, otherwise try to auto-detect
            if date_col is not None and date_col < len(row):
                date_str = row[date_col]
            if desc_col is not None and desc_col < len(row):
                description = row[desc_col] or ""
            if amount_col is not None and amount_col < len(row):
                amount_str = row[amount_col] or ""
            
            # If columns weren't identified, try to auto-detect from the row
            if not date_str or not amount_str:
                for cell in row:
                    if not cell:
                        continue
                    
                    # Check if it looks like a date
                    if not date_str and re.search(r'\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}', cell):
                        date_str = cell
                    
                    # Check if it looks like an amount
                    elif not amount_str and re.search(r'[\$]?[\d,]+\.?\d*', cell):
                        amount_str = cell
                    
                    # Use remaining text as description
                    elif not description and len(cell.strip()) > 3:
                        description = cell
            
            # Parse the extracted data
            if date_str and amount_str:
                transaction_date = self._parse_date(date_str)
                if not transaction_date:
                    return None
                
                # Clean and parse amount
                amount_clean = re.sub(r'[^\d,.-]', '', amount_str)
                if amount_clean:
                    try:
                        amount = Decimal(amount_clean.replace(',', ''))
                        
                        # Determine transaction type and category
                        transaction_type = self._determine_transaction_type(description, ' | '.join(row))
                        category = self._categorize_transaction(description)
                        
                        return {
                            'date': transaction_date,
                            'description': description.strip(),
                            'amount': amount,
                            'transaction_type': transaction_type,
                            'category': category,
                            'raw_line': ' | '.join([cell or "" for cell in row])
                        }
                    except (InvalidOperation, ValueError):
                        pass
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing table row: {str(e)}")
            return None

    def _parse_transaction_line(self, match, full_line: str) -> Optional[Dict]:
        """Parse a single transaction from regex match"""
        try:
            date_str = match.group(1)
            description = match.group(2).strip()
            amount_str = match.group(3).replace(',', '')
            
            # Parse date
            transaction_date = self._parse_date(date_str)
            if not transaction_date:
                return None
            
            # Parse amount
            try:
                amount = Decimal(amount_str)
            except InvalidOperation:
                return None
            
            # Determine transaction type
            transaction_type = self._determine_transaction_type(description, full_line)
            
            # Determine category
            category = self._categorize_transaction(description)
            
            return {
                'date': transaction_date,
                'description': description,
                'amount': amount,
                'transaction_type': transaction_type,
                'category': category,
                'raw_line': full_line
            }
            
        except Exception as e:
            logger.warning(f"Error parsing transaction: {str(e)}")
            return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string into date object"""
        # Common date formats
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
            '%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'
        ]
        
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                # Reasonable date range check (last 5 years to next year)
                current_year = datetime.now().year
                if (current_year - 5) <= parsed_date.year <= (current_year + 1):
                    return parsed_date
            except ValueError:
                continue
        
        return None

    def _determine_transaction_type(self, description: str, full_line: str) -> str:
        """Determine if transaction is debit, credit, fee, or interest"""
        desc_lower = description.lower()
        line_lower = full_line.lower()
        
        # Check for specific transaction types first
        if any(keyword in desc_lower for keyword in ['fee', 'charge', 'overdraft']):
            return 'fee'
        
        if any(keyword in desc_lower for keyword in ['interest', 'dividend']):
            return 'interest'
        
        # Check for credit indicators
        if any(keyword in desc_lower for keyword in self.credit_keywords):
            return 'credit'
        
        # Check for debit indicators  
        if any(keyword in desc_lower for keyword in self.debit_keywords):
            return 'debit'
        
        # Look for visual indicators in the full line (-, +, CR, DR)
        if re.search(r'[\-\(]|\bDR\b', line_lower):
            return 'debit'
        if re.search(r'[\+]|\bCR\b', line_lower):
            return 'credit'
        
        # Default assumption based on common banking conventions
        return 'debit'  # Most transactions are debits

    def _categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description"""
        desc_lower = description.lower()
        
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, desc_lower, re.IGNORECASE):
                return category
        
        return 'other'

    def _remove_duplicate_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Remove duplicate transactions based on date, amount, and description similarity"""
        unique_transactions = []
        seen = set()
        
        for trans in transactions:
            # Create a key based on date, amount, and first few words of description
            desc_words = trans['description'].split()[:3]  # First 3 words
            key = (
                trans['date'],
                trans['amount'],
                ' '.join(desc_words).lower()
            )
            
            if key not in seen:
                seen.add(key)
                unique_transactions.append(trans)
        
        return unique_transactions

    def calculate_summary_stats(self, transactions: List[Dict]) -> Dict:
        """Calculate summary statistics from transactions"""
        total_income = Decimal('0')
        total_expenses = Decimal('0')
        category_totals = {}
        
        for trans in transactions:
            # Ensure amount is Decimal for consistent calculations
            amount = Decimal(str(trans['amount']))
            category = trans['category']
            trans_type = trans['transaction_type']
            
            # Update category totals
            if category not in category_totals:
                category_totals[category] = {
                    'total': Decimal('0'),
                    'count': 0,
                    'transactions': []
                }
            
            category_totals[category]['total'] += amount
            category_totals[category]['count'] += 1
            category_totals[category]['transactions'].append(trans)
            
            # Update income/expense totals
            if trans_type == 'credit':
                total_income += amount
            else:
                total_expenses += amount
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_change': total_income - total_expenses,
            'category_breakdown': category_totals,
            'transaction_count': len(transactions)
        }