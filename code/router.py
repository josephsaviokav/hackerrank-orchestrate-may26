"""
Router: Make escalation vs. reply decisions and generate justifications.
"""

from typing import Dict, Any, Optional, Tuple


class TicketRouter:
    """Route tickets to escalation or reply with justification."""
    
    def __init__(self):
        """Initialize router."""
        pass
    
    def route_ticket(
        self,
        classification: Dict[str, Any],
        retrieval_result: Optional[Tuple[Dict, str]],
        ticket: Dict[str, str]
    ) -> Dict[str, Any]:
        """Route ticket and generate decision with justification."""
        
        status = self._determine_status(classification, retrieval_result)
        
        return {
            "status": status,
            "product_area": classification.get("product_area", "General"),
            "request_type": classification.get("request_type", "product_issue"),
            "response": self._generate_response(status, retrieval_result, classification),
            "justification": self._generate_justification(status, classification, retrieval_result)
        }
    
    def _determine_status(
        self,
        classification: Dict[str, Any],
        retrieval_result: Optional[Tuple[Dict, str]]
    ) -> str:
        """Determine whether to reply or escalate."""
        
        # Always escalate high-risk tickets
        if classification.get("risk_level") == "high":
            return "escalated"
        
        # Always escalate invalid requests
        if classification.get("request_type") == "invalid":
            return "escalated"
        
        # Escalate if no good retrieval result found
        if not retrieval_result:
            return "escalated"
        
        # Escalate if should_escalate flag is set
        if classification.get("should_escalate"):
            return "escalated"
        
        # Otherwise, reply
        return "replied"
    
    def _generate_response(
        self,
        status: str,
        retrieval_result: Optional[Tuple[Dict, str]],
        classification: Dict[str, Any]
    ) -> str:
        """Generate appropriate response text."""
        
        if status == "escalated":
            return self._generate_escalation_response(classification)
        
        # Format reply response
        if retrieval_result:
            doc, answer = retrieval_result
            return answer
        
        # Shouldn't reach here, but fallback
        return "Thank you for contacting support. Your request requires further review by our team."
    
    def _generate_escalation_response(self, classification: Dict[str, Any]) -> str:
        """Generate response for escalated tickets."""
        
        reason = classification.get("escalation_reason", "")
        
        responses = {
            "High-risk category (fraud, security, legal, billing)":
                "Thank you for reporting this issue. Due to the sensitive nature of your request "
                "(involving security, fraud, legal, or billing concerns), we're escalating this to our "
                "specialized support team for priority review. You'll hear from us shortly.",
            
            "Ticket appears to be invalid or off-topic":
                "Thank you for reaching out. This request appears to be outside the scope of our support. "
                "If you have a valid support issue, please resubmit with more details.",
            
            "Complex multi-part issue requiring human review":
                "Thank you for your detailed request. Your issue involves multiple components that require "
                "careful review by our support team. We're escalating this for personalized assistance.",
            
            "Routine escalation":
                "Thank you for contacting support. Your request requires further investigation by our team. "
                "We'll respond as soon as possible."
        }
        
        return responses.get(
            reason,
            "Thank you for contacting support. Your request has been escalated to our team for review."
        )
    
    def _generate_justification(
        self,
        status: str,
        classification: Dict[str, Any],
        retrieval_result: Optional[Tuple[Dict, str]]
    ) -> str:
        """Generate justification for the routing decision."""
        
        parts = []
        
        # Request classification
        request_type = classification.get("request_type", "unknown")
        parts.append(f"Request type: {request_type}")
        
        # Risk assessment
        risk = classification.get("risk_level", "low")
        parts.append(f"Risk level: {risk}")
        
        # Urgency
        urgency = classification.get("urgency_level", "low")
        parts.append(f"Urgency: {urgency}")
        
        # Routing decision reason
        if status == "escalated":
            reason = classification.get("escalation_reason", "Manual escalation")
            parts.append(f"Decision: Escalated ({reason})")
        else:
            if retrieval_result:
                doc, _ = retrieval_result
                parts.append(f"Decision: Replied (matched to {doc.get('title', 'documentation')})")
            else:
                parts.append("Decision: Replied based on standard procedure")
        
        return " | ".join(parts)
    
    def batch_route(
        self,
        tickets: list,
        classifications: list,
        retrieval_results: list
    ) -> list:
        """Route multiple tickets at once."""
        
        results = []
        for ticket, classification, retrieval in zip(tickets, classifications, retrieval_results):
            route = self.route_ticket(classification, retrieval, ticket)
            results.append(route)
        
        return results


def create_router() -> TicketRouter:
    """Factory function to create router."""
    return TicketRouter()
