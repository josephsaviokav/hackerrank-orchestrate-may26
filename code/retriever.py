"""
Retriever: Search and rank relevant support documents from corpus.
"""

from typing import List, Dict, Any, Optional, Tuple
import re


class DocumentRetriever:
    """Retrieve and rank relevant docs from indexed corpus."""
    
    def __init__(self, corpus_index: Any):
        """Initialize retriever with indexed corpus."""
        self.index = corpus_index
    
    def retrieve_docs(
        self,
        query: str,
        company: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k most relevant documents for a query."""
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        if not keywords:
            # Fallback: use entire query as single keyword
            keywords = [query.lower()[:50]]
        
        # Limit keywords for performance
        keywords = keywords[:5]
        
        # Search in company-specific index if provided
        if company:
            results = self.index.search_by_keywords(keywords, company)
        else:
            results = self.index.search_by_keywords(keywords)
        
        # Return top-k, with minimum score threshold to avoid low-quality matches
        scored_results = [r for r in results if r.get("score", 0) > 0]
        return scored_results[:top_k]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "is", "are", "am", "was", "were", "be", "been", "being", "have", "has",
            "do", "does", "did", "should", "would", "could", "may", "might", "can",
            "i", "you", "he", "she", "it", "we", "they", "what", "which", "who",
            "how", "when", "where", "why", "this", "that", "these", "those"
        }
        
        # Split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        
        # Filter stop words and short tokens
        keywords = [
            token for token in tokens 
            if token not in stop_words and len(token) > 2
        ]
        
        return keywords[:10]  # Limit to 10 keywords
    
    def rank_by_relevance(
        self,
        docs: List[Dict[str, Any]],
        query: str,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Re-rank documents by relevance to query."""
        
        query_lower = query.lower()
        
        for doc in docs:
            score = 0
            
            # Title match (high weight)
            if query_lower in doc.get("title", "").lower():
                score += 5
            
            # Exact phrase in content (high weight)
            if query_lower in doc.get("content", "").lower():
                score += 3
            
            # Category match (medium weight)
            if category and category.lower() in doc.get("category", "").lower():
                score += 2
            
            # Word overlap (low weight)
            query_words = set(query_lower.split())
            content_words = set(doc.get("content", "").lower().split())
            overlap = len(query_words & content_words)
            score += overlap * 0.5
            
            doc["relevance_score"] = score
        
        # Sort by score
        docs.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return docs
    
    def extract_answer_section(
        self,
        doc: Dict[str, Any],
        query: str,
        max_chars: int = 1000
    ) -> str:
        """Extract most relevant section from document as answer."""
        
        content = doc.get("content", "")
        query_lower = query.lower()
        
        # Find paragraphs containing query terms
        paragraphs = content.split("\n\n")[:20]  # Limit to first 20 paragraphs for performance
        relevant_paras = []
        
        for para in paragraphs:
            para_lower = para.lower()
            
            # Skip headers and short fragments
            if len(para.strip()) < 20:
                continue
            
            # Score paragraph
            if query_lower in para_lower or any(word in para_lower for word in query_lower.split()[:3]):
                relevant_paras.append(para)
        
        # Combine top paragraphs up to max_chars
        answer = ""
        for para in relevant_paras[:2]:  # Use up to 2 paragraphs for performance
            if len(answer) + len(para) < max_chars:
                answer += para + "\n\n"
            else:
                break
        
        # Fallback: return first substantial paragraph
        if not answer:
            for para in paragraphs:
                if len(para.strip()) > 50:
                    answer = para[:max_chars]
                    break
        
        return answer.strip()
    
    def format_response_with_citation(
        self,
        answer: str,
        doc: Dict[str, Any],
        company: str
    ) -> str:
        """Format answer with citation to source document."""
        
        citation = f"\n\n---\n*Based on {company} Support: {doc.get('title', 'Support Documentation')}*"
        return answer + citation
    
    def get_best_match(
        self,
        query: str,
        company: Optional[str] = None
    ) -> Optional[Tuple[Dict[str, Any], str]]:
        """Get best matching doc with extracted answer section.
        
        Returns: (doc_dict, answer_text) or None if no good match
        """
        docs = self.retrieve_docs(query, company, top_k=3)
        
        if not docs:
            return None
        
        best_doc = docs[0]
        answer = self.extract_answer_section(best_doc, query)
        
        if answer and len(answer) > 50:  # Only return if we found substantial content
            return best_doc, answer
        
        return None
    
    def search_by_category(
        self,
        company: str,
        category: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for all docs in a specific category."""
        docs = self.index.get_docs_by_category(company, category)
        return docs[:limit]


def create_retriever(corpus_index: Any) -> DocumentRetriever:
    """Factory function to create retriever."""
    return DocumentRetriever(corpus_index)
