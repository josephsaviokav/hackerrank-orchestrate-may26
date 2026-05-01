"""
Corpus Indexer: Parse support documentation and build searchable index.
Indexes all markdown files from data/ into company-specific, category-aware structure.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any


class CorpusIndexer:
    """Index support documentation by company and category."""
    
    def __init__(self, data_dir: str):
        """Initialize indexer with path to data directory."""
        self.data_dir = Path(data_dir)
        self.index: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
            "HackerRank": {},
            "Claude": {},
            "Visa": {}
        }
        self.doc_count = 0
        
    def index_corpus(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Index all docs in data/ directory."""
        companies = ["hackerrank", "claude", "visa"]
        
        for company in companies:
            company_dir = self.data_dir / company
            if not company_dir.exists():
                continue
                
            proper_name = {"hackerrank": "HackerRank", "claude": "Claude", "visa": "Visa"}[company]
            self._walk_directory(company_dir, proper_name)
        
        return self.index
    
    def _walk_directory(self, directory: Path, company_name: str, category: str = "Uncategorized"):
        """Recursively walk directory and index markdown files."""
        try:
            for item in directory.iterdir():
                if item.is_file() and item.suffix == ".md":
                    self._index_file(item, company_name, category)
                elif item.is_dir() and not item.name.startswith("."):
                    # Use directory name as category
                    new_category = item.name.replace("-", " ").title()
                    self._walk_directory(item, company_name, new_category)
        except (PermissionError, OSError):
            pass
    
    def _index_file(self, file_path: Path, company_name: str, category: str):
        """Index a single markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                return
            
            # Extract title from filename or first heading
            title = self._extract_title(file_path, content)
            
            doc_entry = {
                "title": title,
                "path": str(file_path.relative_to(self.data_dir)),
                "category": category,
                "content": content,
                "keywords": self._extract_keywords(content),
            }
            
            # Initialize category if needed
            if category not in self.index[company_name]:
                self.index[company_name][category] = []
            
            self.index[company_name][category].append(doc_entry)
            self.doc_count += 1
            
        except Exception as e:
            print(f"Warning: Failed to index {file_path}: {e}")
    
    def _extract_title(self, file_path: Path, content: str) -> str:
        """Extract title from filename or first heading."""
        # Try to find first heading
        for line in content.split("\n"):
            if line.startswith("#"):
                return line.lstrip("#").strip()
        
        # Fallback: use filename
        return file_path.stem.replace("-", " ").title()
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract potential keywords from content."""
        keywords = []
        
        # Extract headings as keywords
        for line in content.split("\n"):
            if line.startswith(("#", "**")):
                text = line.lstrip("#").strip("*").strip()
                if text and len(text) > 3:
                    keywords.append(text.lower())
        
        return keywords[:20]  # Limit to 20 keywords
    
    def search_by_keywords(self, keywords: List[str], company: str = None) -> List[Dict[str, Any]]:
        """Search index by keywords within a company or across all."""
        results = []
        companies = [company] if company and company in self.index else self.index.keys()
        
        for comp in companies:
            for category, docs in self.index[comp].items():
                for doc in docs:
                    # Score based on keyword matches
                    score = self._score_relevance(doc, keywords)
                    if score > 0:
                        results.append({**doc, "score": score, "company": comp})
        
        # Sort by score (descending) and limit to top 50 for performance
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:50]
    
    def _score_relevance(self, doc: Dict[str, Any], keywords: List[str]) -> int:
        """Score document relevance to keywords."""
        score = 0
        content_lower = doc["content"].lower()
        title_lower = doc["title"].lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Title match (higher weight)
            if keyword_lower in title_lower:
                score += 3
            # Content match (lower weight) - limit to first occurrence
            elif keyword_lower in content_lower:
                score += 1
        
        return score
    
    def get_docs_by_category(self, company: str, category: str) -> List[Dict[str, Any]]:
        """Get all docs in a specific category for a company."""
        if company not in self.index or category not in self.index[company]:
            return []
        return self.index[company][category]
    
    def get_categories(self, company: str) -> List[str]:
        """Get all categories for a company."""
        if company not in self.index:
            return []
        return list(self.index[company].keys())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        summary = {
            "total_docs": self.doc_count,
            "companies": {}
        }
        
        for company, categories in self.index.items():
            summary["companies"][company] = {
                "categories": len(categories),
                "docs": sum(len(docs) for docs in categories.values()),
                "categories_list": list(categories.keys())
            }
        
        return summary


def create_indexer(data_dir: str = "data") -> CorpusIndexer:
    """Factory function to create and initialize indexer."""
    indexer = CorpusIndexer(data_dir)
    indexer.index_corpus()
    return indexer
