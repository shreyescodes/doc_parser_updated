"""
Specialized extractor for LP document data.
"""
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)


class LPDocumentExtractor:
    """Specialized extractor for LP document structured data."""
    
    def __init__(self):
        # Common patterns for LP documents
        self.currency_pattern = r'\$[\d,]+\.?\d*|\d+\.?\d*\s*(USD|EUR|GBP|CAD|AUD)'
        self.date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{1,2}-\d{1,2}\b'
        self.percentage_pattern = r'\d+\.?\d*\s*%'
        self.amount_pattern = r'[\d,]+\.?\d*'
    
    def extract_capital_call_data(self, text_content: str) -> Dict[str, Any]:
        """
        Extract capital call specific data from document text.
        
        Args:
            text_content: Extracted text content
            
        Returns:
            Dictionary containing capital call data
        """
        try:
            logger.info("Extracting capital call data")
            
            data = {}
            text_lower = text_content.lower()
            
            # Extract dates
            data['call_date'] = self._extract_date(text_content, ['call date', 'notice date', 'date'])
            data['due_date'] = self._extract_date(text_content, ['due date', 'payment due', 'deadline'])
            
            # Extract amounts
            data['call_amount'] = self._extract_amount(text_content, ['call amount', 'contribution', 'capital call'])
            data['lp_commitment'] = self._extract_amount(text_content, ['commitment', 'total commitment'])
            data['remaining_commitment'] = self._extract_amount(text_content, ['remaining commitment', 'outstanding'])
            
            # Extract percentages
            data['call_percentage'] = self._extract_percentage(text_content, ['call percentage', 'contribution percentage'])
            
            # Extract fund information
            data['fund_name'] = self._extract_fund_name(text_content)
            data['fund_size'] = self._extract_amount(text_content, ['fund size', 'total commitments'])
            
            # Extract LP information
            data['lp_name'] = self._extract_lp_name(text_content)
            
            # Extract payment instructions
            data['payment_instructions'] = self._extract_payment_instructions(text_content)
            
            # Extract wire transfer information
            data['wire_transfer_info'] = self._extract_wire_transfer_info(text_content)
            
            logger.info(f"Capital call data extracted: {len(data)} fields")
            return data
            
        except Exception as e:
            logger.error(f"Capital call extraction failed: {str(e)}")
            return {}
    
    def extract_distribution_data(self, text_content: str) -> Dict[str, Any]:
        """
        Extract distribution specific data from document text.
        
        Args:
            text_content: Extracted text content
            
        Returns:
            Dictionary containing distribution data
        """
        try:
            logger.info("Extracting distribution data")
            
            data = {}
            text_lower = text_content.lower()
            
            # Extract dates
            data['distribution_date'] = self._extract_date(text_content, ['distribution date', 'payment date'])
            data['record_date'] = self._extract_date(text_content, ['record date', 'ex-date'])
            
            # Extract amounts
            data['distribution_amount'] = self._extract_amount(text_content, ['distribution amount', 'distribution'])
            data['lp_distribution_amount'] = self._extract_amount(text_content, ['your distribution', 'distribution to'])
            data['distribution_per_unit'] = self._extract_amount(text_content, ['per unit', 'per share'])
            
            # Extract fund information
            data['fund_name'] = self._extract_fund_name(text_content)
            data['fund_nav'] = self._extract_amount(text_content, ['nav', 'net asset value'])
            data['total_distributions'] = self._extract_amount(text_content, ['total distributions'])
            
            # Extract LP information
            data['lp_name'] = self._extract_lp_name(text_content)
            data['lp_units'] = self._extract_amount(text_content, ['units', 'shares', 'partnership units'])
            
            # Extract performance metrics
            data['irr'] = self._extract_percentage(text_content, ['irr', 'internal rate of return'])
            data['multiple'] = self._extract_amount(text_content, ['multiple', 'total return multiple'])
            
            # Extract payment information
            data['payment_method'] = self._extract_payment_method(text_content)
            data['payment_instructions'] = self._extract_payment_instructions(text_content)
            
            logger.info(f"Distribution data extracted: {len(data)} fields")
            return data
            
        except Exception as e:
            logger.error(f"Distribution extraction failed: {str(e)}")
            return {}
    
    def _extract_date(self, text: str, keywords: List[str]) -> Optional[datetime]:
        """Extract date from text based on keywords."""
        try:
            text_lower = text.lower()
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the line containing the keyword
                    lines = text.split('\n')
                    for line in lines:
                        if keyword in line.lower():
                            # Look for date pattern in the line
                            dates = re.findall(self.date_pattern, line)
                            if dates:
                                date_str = dates[0]
                                # Try different date formats
                                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y']:
                                    try:
                                        return datetime.strptime(date_str, fmt)
                                    except ValueError:
                                        continue
            return None
            
        except Exception as e:
            logger.error(f"Date extraction failed: {str(e)}")
            return None
    
    def _extract_amount(self, text: str, keywords: List[str]) -> Optional[float]:
        """Extract monetary amount from text based on keywords."""
        try:
            text_lower = text.lower()
            
            for keyword in keywords:
                if keyword in text_lower:
                    # Find the line containing the keyword
                    lines = text.split('\n')
                    for line in lines:
                        if keyword in line.lower():
                            # Look for currency pattern
                            currencies = re.findall(self.currency_pattern, line)
                            if currencies:
                                amount_str = currencies[0]
                                # Clean and convert to float
                                amount_str = re.sub(r'[^\d.,]', '', amount_str)
                                amount_str = amount_str.replace(',', '')
                                try:
                                    return float(amount_str)
                                except ValueError:
                                    continue
                            
                            # Fallback to amount pattern
                            amounts = re.findall(self.amount_pattern, line)
                            if amounts:
                                try:
                                    return float(amounts[0].replace(',', ''))
                                except ValueError:
                                    continue
            return None
            
        except Exception as e:
            logger.error(f"Amount extraction failed: {str(e)}")
            return None
    
    def _extract_percentage(self, text: str, keywords: List[str]) -> Optional[float]:
        """Extract percentage from text based on keywords."""
        try:
            text_lower = text.lower()
            
            for keyword in keywords:
                if keyword in text_lower:
                    lines = text.split('\n')
                    for line in lines:
                        if keyword in line.lower():
                            percentages = re.findall(self.percentage_pattern, line)
                            if percentages:
                                pct_str = percentages[0].replace('%', '')
                                try:
                                    return float(pct_str)
                                except ValueError:
                                    continue
            return None
            
        except Exception as e:
            logger.error(f"Percentage extraction failed: {str(e)}")
            return None
    
    def _extract_fund_name(self, text: str) -> Optional[str]:
        """Extract fund name from text."""
        try:
            # Look for common fund name patterns
            patterns = [
                r'fund[:\s]+([A-Z][^.\n]*)',
                r'([A-Z][A-Z\s]+fund)',
                r'([A-Z][A-Z\s]+partners)',
                r'([A-Z][A-Z\s]+capital)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0].strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Fund name extraction failed: {str(e)}")
            return None
    
    def _extract_lp_name(self, text: str) -> Optional[str]:
        """Extract LP name from text."""
        try:
            # Look for LP name patterns
            patterns = [
                r'dear\s+([^,\n]+)',
                r'to:\s*([^,\n]+)',
                r'limited partner[:\s]+([^,\n]+)',
                r'lp[:\s]+([^,\n]+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
            
            return None
            
        except Exception as e:
            logger.error(f"LP name extraction failed: {str(e)}")
            return None
    
    def _extract_payment_instructions(self, text: str) -> Optional[str]:
        """Extract payment instructions from text."""
        try:
            # Look for payment instruction sections
            sections = [
                'payment instructions',
                'wire instructions',
                'payment details',
                'banking information'
            ]
            
            text_lower = text.lower()
            for section in sections:
                if section in text_lower:
                    # Find the section and extract following lines
                    lines = text.split('\n')
                    start_idx = -1
                    for i, line in enumerate(lines):
                        if section in line.lower():
                            start_idx = i
                            break
                    
                    if start_idx >= 0:
                        # Extract next few lines
                        instructions = []
                        for i in range(start_idx + 1, min(start_idx + 10, len(lines))):
                            line = lines[i].strip()
                            if line and not line.lower().startswith(('sincerely', 'regards', 'best')):
                                instructions.append(line)
                            elif line.lower().startswith(('sincerely', 'regards', 'best')):
                                break
                        
                        if instructions:
                            return '\n'.join(instructions)
            
            return None
            
        except Exception as e:
            logger.error(f"Payment instructions extraction failed: {str(e)}")
            return None
    
    def _extract_wire_transfer_info(self, text: str) -> Optional[Dict[str, str]]:
        """Extract wire transfer information from text."""
        try:
            wire_info = {}
            
            # Common wire transfer fields
            fields = {
                'bank_name': ['bank name', 'bank:'],
                'account_number': ['account number', 'account no', 'acct no'],
                'routing_number': ['routing number', 'routing no', 'aba'],
                'swift_code': ['swift', 'bic'],
                'beneficiary': ['beneficiary', 'pay to']
            }
            
            text_lower = text.lower()
            lines = text.split('\n')
            
            for field, keywords in fields.items():
                for keyword in keywords:
                    for line in lines:
                        if keyword in line.lower():
                            # Extract value after colon
                            if ':' in line:
                                value = line.split(':', 1)[1].strip()
                                if value:
                                    wire_info[field] = value
                                    break
            
            return wire_info if wire_info else None
            
        except Exception as e:
            logger.error(f"Wire transfer info extraction failed: {str(e)}")
            return None
    
    def _extract_payment_method(self, text: str) -> Optional[str]:
        """Extract payment method from text."""
        try:
            text_lower = text.lower()
            
            methods = ['wire transfer', 'ach', 'check', 'electronic transfer', 'direct deposit']
            
            for method in methods:
                if method in text_lower:
                    return method
            
            return None
            
        except Exception as e:
            logger.error(f"Payment method extraction failed: {str(e)}")
            return None
