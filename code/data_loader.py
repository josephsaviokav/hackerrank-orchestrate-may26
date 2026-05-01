"""
Data Loader: Handle reading and writing support ticket CSVs.
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class TicketDataLoader:
    """Load and manage support ticket CSV files."""
    
    def __init__(self, tickets_dir: str = "support_tickets"):
        """Initialize loader with path to support_tickets directory."""
        self.tickets_dir = Path(tickets_dir)
        self.tickets_dir.mkdir(parents=True, exist_ok=True)
    
    def load_tickets(self, filename: str) -> List[Dict[str, str]]:
        """Load tickets from CSV file."""
        file_path = self.tickets_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Ticket file not found: {file_path}")
        
        tickets = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:  # Skip empty rows
                        tickets.append(row)
        except Exception as e:
            print(f"Error loading tickets from {file_path}: {e}")
            return []
        
        return tickets
    
    def load_sample_tickets(self) -> List[Dict[str, str]]:
        """Load sample tickets with expected outputs."""
        return self.load_tickets("sample_support_tickets.csv")
    
    def load_production_tickets(self) -> List[Dict[str, str]]:
        """Load production tickets (inputs only)."""
        return self.load_tickets("support_tickets.csv")
    
    def save_output(self, results: List[Dict[str, Any]], filename: str = "output.csv"):
        """Write agent predictions to CSV."""
        file_path = self.tickets_dir / filename
        
        if not results:
            print(f"Warning: No results to write to {file_path}")
            return
        
        # Ensure all required columns are present
        required_columns = ["status", "product_area", "response", "justification", "request_type"]
        
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=required_columns)
                writer.writeheader()
                
                for result in results:
                    row = {col: result.get(col, "") for col in required_columns}
                    writer.writerow(row)
            
            print(f"✓ Results written to {file_path} ({len(results)} rows)")
        except Exception as e:
            print(f"Error writing results to {file_path}: {e}")
    
    def validate_output(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate output structure and values."""
        errors = []
        warnings = []
        
        # Check required columns
        required = {"status", "product_area", "response", "justification", "request_type"}
        
        for i, result in enumerate(results):
            row_errors = []
            
            # Check all required columns present
            missing = required - set(result.keys())
            if missing:
                row_errors.append(f"Missing columns: {missing}")
            
            # Validate enum values
            if result.get("status") not in ["replied", "escalated"]:
                row_errors.append(f"Invalid status: {result.get('status')}")
            
            if result.get("request_type") not in ["product_issue", "feature_request", "bug", "invalid"]:
                row_errors.append(f"Invalid request_type: {result.get('request_type')}")
            
            # Check for empty critical fields
            if not result.get("response", "").strip():
                warnings.append(f"Row {i}: Empty response")
            
            if not result.get("justification", "").strip():
                warnings.append(f"Row {i}: Empty justification")
            
            if row_errors:
                errors.append(f"Row {i}: {'; '.join(row_errors)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_rows": len(results)
        }
    
    def get_ticket_count(self) -> Dict[str, int]:
        """Get counts of tickets in each file."""
        counts = {}
        
        for filename in ["sample_support_tickets.csv", "support_tickets.csv"]:
            file_path = self.tickets_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        count = sum(1 for _ in csv.DictReader(f)) - 1  # -1 for header
                        counts[filename] = count
                except:
                    counts[filename] = 0
        
        return counts


def create_loader(tickets_dir: str = "support_tickets") -> TicketDataLoader:
    """Factory function to create data loader."""
    return TicketDataLoader(tickets_dir)
