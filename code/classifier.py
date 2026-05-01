"""
Classifier: Classify request type, product area, urgency, and risk level.
"""

import re
from typing import Dict, List, Tuple, Optional, Any


class TicketClassifier:
    """Classify support tickets by type, area, and risk."""
    
    # High-risk keywords that should trigger escalation
    HIGH_RISK_KEYWORDS = {
        "fraud", "hack", "security", "breach", "stolen", "scam",
        "delete my account", "data deletion", "legal", "lawsuit",
        "refund", "chargeback", "billing", "payment failed", "unauthorized charge",
        "identity theft", "phishing", "malware", "exploit", "vulnerability",
        "emergency", "critical", "urgent", "down", "broken completely"
    }
    
    # Bug indicators
    BUG_KEYWORDS = {
        "bug", "error", "crash", "broken", "not working", "doesn't work", "fail",
        "issue", "problem", "stop", "freeze", "hang", "timeout", "exception",
        "exception", "stacktrace", "traceback", "null", "undefined", "404", "500"
    }
    
    # Feature request indicators
    FEATURE_KEYWORDS = {
        "want", "request", "feature", "suggest", "could", "would like", "idea",
        "enhancement", "add", "implement", "ability", "support for", "enable"
    }
    
    # Invalid/out-of-scope indicators
    INVALID_KEYWORDS = {
        "spam", "off topic", "irrelevant", "unrelated", "wrong company",
        "not relevant", "shouldn't be here"
    }
    
    def __init__(self):
        """Initialize classifier."""
        self.product_area_keywords = {
            "HackerRank": self._get_hackerrank_keywords(),
            "Claude": self._get_claude_keywords(),
            "Visa": self._get_visa_keywords(),
        }
    
    def classify_ticket(
        self, 
        issue: str, 
        subject: str, 
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """Classify a ticket and return comprehensive analysis."""
        
        combined_text = f"{subject} {issue}".lower()
        
        return {
            "request_type": self._classify_request_type(combined_text),
            "product_area": self._classify_product_area(combined_text, company),
            "risk_level": self._assess_risk_level(combined_text),
            "urgency_level": self._assess_urgency(combined_text),
            "company": company or self._infer_company(combined_text),
            "should_escalate": self._should_escalate(combined_text),
            "escalation_reason": self._get_escalation_reason(combined_text)
        }
    
    def _classify_request_type(self, text: str) -> str:
        """Classify request as: product_issue, feature_request, bug, or invalid."""
        text_lower = text.lower()
        
        # Check for invalid first (highest priority)
        if self._contains_any(text_lower, self.INVALID_KEYWORDS):
            return "invalid"
        
        # Check for bug
        if self._contains_any(text_lower, self.BUG_KEYWORDS):
            return "bug"
        
        # Check for feature request
        if self._contains_any(text_lower, self.FEATURE_KEYWORDS):
            return "feature_request"
        
        # Default to product_issue
        return "product_issue"
    
    def _classify_product_area(self, text: str, company: Optional[str] = None) -> str:
        """Classify into product area based on company and content."""
        if not company:
            company = self._infer_company(text)
        
        if company not in self.product_area_keywords:
            return "General"
        
        keywords = self.product_area_keywords[company]
        
        # Score each area
        scores = {}
        for area, keywords_list in keywords.items():
            score = sum(1 for keyword in keywords_list if keyword in text)
            if score > 0:
                scores[area] = score
        
        # Return highest-scoring area
        if scores:
            return max(scores, key=scores.get)
        
        return "General Help"
    
    def _assess_risk_level(self, text: str) -> str:
        """Assess risk level: low, medium, high."""
        text_lower = text.lower()
        
        # High risk
        if self._contains_any(text_lower, self.HIGH_RISK_KEYWORDS):
            return "high"
        
        # Medium risk: sensitive topics
        medium_risk = {"permission", "access", "account", "suspend", "ban", "limit", "lock"}
        if self._contains_any(text_lower, medium_risk):
            return "medium"
        
        # Low risk by default
        return "low"
    
    def _assess_urgency(self, text: str) -> str:
        """Assess urgency level: low, medium, high."""
        text_lower = text.lower()
        
        urgent_words = {
            "urgent", "emergency", "critical", "asap", "immediately", "now",
            "can't access", "can't use", "broken", "down", "not working"
        }
        
        if self._contains_any(text_lower, urgent_words):
            return "high"
        
        medium_urgency = {
            "soon", "quickly", "problem", "issue", "help", "need"
        }
        
        if self._contains_any(text_lower, medium_urgency):
            return "medium"
        
        return "low"
    
    def _should_escalate(self, text: str) -> bool:
        """Determine if ticket should be escalated."""
        # Escalate if high risk
        if self._assess_risk_level(text) == "high":
            return True
        
        # Escalate if request_type is invalid
        if self._classify_request_type(text) == "invalid":
            return True
        
        # Escalate if contains multiple questions or complex scenario
        if text.count("?") > 2:
            return True
        
        return False
    
    def _get_escalation_reason(self, text: str) -> str:
        """Get reason for escalation if needed."""
        if self._assess_risk_level(text) == "high":
            return "High-risk category (fraud, security, legal, billing)"
        
        if self._classify_request_type(text) == "invalid":
            return "Ticket appears to be invalid or off-topic"
        
        if text.count("?") > 2:
            return "Complex multi-part issue requiring human review"
        
        return "Routine escalation"
    
    def _infer_company(self, text: str) -> Optional[str]:
        """Infer company from ticket content."""
        company_keywords = {
            "HackerRank": {"hackerrank", "test", "hiring", "interview", "assessment", "skill"},
            "Claude": {"claude", "anthropic", "bedrock", "ai", "model", "api"},
            "Visa": {"visa", "card", "payment", "transaction", "merchant"}
        }
        
        text_lower = text.lower()
        scores = {}
        
        for company, keywords in company_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[company] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _contains_any(self, text: str, keywords: set) -> bool:
        """Check if text contains any of the keywords."""
        for keyword in keywords:
            if keyword in text:
                return True
        return False
    
    def _get_hackerrank_keywords(self) -> Dict[str, List[str]]:
        """Product area keywords for HackerRank."""
        return {
            "General Help": ["test", "assessment", "hiring", "candidate", "invite"],
            "Interviews": ["interview", "mock", "interview"],
            "Assessments": ["assessment", "evaluation", "score", "test"],
            "Test Settings": ["test active", "expiration", "start date", "end date"],
            "Screen": ["screen", "platform", "ide", "code"],
            "Integrations": ["integration", "api", "slack", "airtable"],
            "Skillup": ["learn", "course", "tutorial", "skill"],
            "Account": ["account", "profile", "password", "login"],
        }
    
    def _get_claude_keywords(self) -> Dict[str, List[str]]:
        """Product area keywords for Claude."""
        return {
            "Getting Started": ["start", "tutorial", "guide", "begin"],
            "API": ["api", "endpoint", "token", "authentication"],
            "Account": ["account", "login", "access", "password", "team"],
            "Claude API Usage": ["usage", "limit", "rate", "quota"],
            "Pricing": ["price", "billing", "cost", "plan", "payment"],
            "Claude Desktop": ["desktop", "app", "install"],
            "Claude Code": ["code", "review", "security", "analysis"],
            "Features": ["feature", "capability", "vision", "tool"],
        }
    
    def _get_visa_keywords(self) -> Dict[str, List[str]]:
        """Product area keywords for Visa."""
        return {
            "Payments": ["payment", "transaction", "charge", "card"],
            "Account": ["account", "setup", "register"],
            "Fraud": ["fraud", "unauthorized", "dispute", "chargeback"],
            "Technical": ["technical", "error", "system", "platform"],
            "General": ["help", "support", "question"],
        }


def create_classifier() -> TicketClassifier:
    """Factory function to create classifier."""
    return TicketClassifier()
