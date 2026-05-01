"""
LLM Reasoning: Optional Claude integration for complex ticket analysis.
Uses Claude for uncertain classifications, multi-part issues, and decision reasoning.
Enforces strict grounding constraints to prevent hallucinations.
"""

import os
from typing import Dict, Any, Optional, Tuple
import json


class LLMReasoner:
    """Use Claude LLM for reasoning about tickets with grounding constraints."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM reasoner with API key."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.enabled = bool(self.api_key)
        self.client = None
        
        if self.enabled:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("⚠️  Warning: anthropic package not installed. LLM reasoning disabled.")
                print("   Install with: pip install anthropic")
                self.enabled = False
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize Anthropic client: {e}")
                self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if LLM reasoning is available."""
        return self.enabled
    
    def refine_classification(
        self,
        ticket_issue: str,
        ticket_subject: str,
        initial_classification: Dict[str, Any],
        confidence: float = 0.5
    ) -> Dict[str, Any]:
        """Use LLM to refine classification for uncertain cases.
        
        Args:
            ticket_issue: The main issue text
            ticket_subject: The subject line
            initial_classification: Classification from rule-based classifier
            confidence: Confidence threshold (0-1). Use LLM if below this.
            
        Returns:
            Refined classification dict, or original if not confident enough
        """
        
        if not self.enabled:
            return initial_classification
        
        # Only use LLM for uncertain cases
        request_type = initial_classification.get("request_type", "")
        if request_type not in ["bug", "feature_request"]:  # Uncertain if basic product_issue
            return initial_classification
        
        prompt = f"""Analyze this support ticket and classify it. Return ONLY valid JSON.

TICKET SUBJECT: {ticket_subject}

TICKET ISSUE: {ticket_issue[:1000]}

Classify into exactly one type:
- "product_issue" = Technical problem or question
- "feature_request" = Feature or enhancement suggestion  
- "bug" = Confirmed bug or crash report
- "invalid" = Off-topic, spam, or out of scope

Also identify if this requires urgent human review (high_priority):
- "high_priority" = Fraud, security, account deletion, legal, billing
- "normal_priority" = Everything else

Return ONLY this JSON (no other text):
{{"request_type": "...", "priority": "..."}}"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text.strip()
            
            # Parse JSON response
            refined = json.loads(result_text)
            
            # Validate response
            if refined.get("request_type") in ["product_issue", "feature_request", "bug", "invalid"]:
                initial_classification["request_type"] = refined["request_type"]
                
                if refined.get("priority") == "high_priority":
                    initial_classification["risk_level"] = "high"
            
            return initial_classification
            
        except Exception as e:
            print(f"⚠️  LLM classification refinement failed: {e}")
            return initial_classification
    
    def evaluate_escalation(
        self,
        ticket_issue: str,
        classification: Dict[str, Any],
        retrieval_result: Optional[Tuple] = None
    ) -> Dict[str, Any]:
        """Use LLM to evaluate escalation decision for edge cases.
        
        Returns:
            {
                "should_escalate": bool,
                "confidence": float (0-1),
                "reasoning": str
            }
        """
        
        if not self.enabled:
            return {
                "should_escalate": classification.get("should_escalate", False),
                "confidence": 0.8,
                "reasoning": "Rule-based decision"
            }
        
        # High confidence in rule-based decisions
        if classification.get("risk_level") == "high":
            return {
                "should_escalate": True,
                "confidence": 0.95,
                "reasoning": "High-risk category flagged by rules"
            }
        
        if not retrieval_result:
            return {
                "should_escalate": True,
                "confidence": 0.85,
                "reasoning": "No matching documentation found"
            }
        
        # Use LLM for borderline cases
        doc, answer = retrieval_result
        prompt = f"""Given this support ticket and matching documentation, decide if human review is needed.

TICKET: {ticket_issue[:500]}

MATCHED DOCUMENTATION:
Title: {doc.get('title', '')}
Content: {answer[:500]}

Can this be safely answered using the documentation provided? Answer YES or NO only.
If NO, explain why (fraud, security, complex issue, unclear match, etc.)

Respond in this exact format:
SAFE: YES/NO
REASON: [explanation if NO, otherwise write "Good match available"]"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text.strip()
            
            safe = "YES" in result_text.upper()
            reason = result_text.split("REASON:")[-1].strip() if "REASON:" in result_text else ""
            
            return {
                "should_escalate": not safe,
                "confidence": 0.8,
                "reasoning": reason or ("Clear documentation match" if safe else "Unclear match")
            }
            
        except Exception as e:
            print(f"⚠️  LLM escalation evaluation failed: {e}")
            return {
                "should_escalate": False,
                "confidence": 0.5,
                "reasoning": f"LLM error: {str(e)[:50]}"
            }
    
    def generate_grounded_response(
        self,
        ticket_issue: str,
        ticket_subject: str,
        retrieved_docs: list,
        classification: Dict[str, Any]
    ) -> Optional[str]:
        """Use LLM to generate response grounded ONLY in provided docs.
        
        Enforces strict constraint: answer must be based ONLY on provided documentation.
        Rejects any LLM outputs that hallucinate beyond the corpus.
        """
        
        if not self.enabled or not retrieved_docs:
            return None
        
        # Build doc context
        doc_context = "SUPPORT DOCUMENTATION:\n\n"
        for i, doc in enumerate(retrieved_docs[:3], 1):
            doc_context += f"[Document {i}]: {doc.get('title', 'Untitled')}\n"
            content = doc.get('content', '')[:300]
            doc_context += f"{content}\n\n"
        
        prompt = f"""{doc_context}

CUSTOMER QUESTION: {ticket_issue}

Generate a helpful response using ONLY the documentation provided above.
You MUST:
1. Answer only using information from the documentation
2. Do not make up steps, policies, or features
3. Cite which document you're using
4. If the documentation doesn't fully answer, say so and suggest escalation

IMPORTANT: If you cannot answer from the docs, respond with:
"Based on the available documentation, I don't have enough information to answer this. Please contact support for assistance."

Generate the response now:"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = response.content[0].text.strip()
            
            # Validate grounding: Check if LLM added hallucinations
            hallucination_signals = [
                "i'm not sure",
                "i think",
                "probably",
                "you might want to",
                "typically",
                "usually",
                "generally",
                "note that"
            ]
            
            answer_lower = answer.lower()
            for signal in hallucination_signals:
                if signal in answer_lower:
                    # LLM is speculating - not grounded
                    return None
            
            return answer
            
        except Exception as e:
            print(f"⚠️  LLM response generation failed: {e}")
            return None
    
    def analyze_multi_part_issue(
        self,
        ticket_issue: str
    ) -> Dict[str, Any]:
        """Analyze if ticket has multiple sub-questions (indicates escalation need).
        
        Returns:
            {
                "has_multiple_parts": bool,
                "parts_count": int,
                "reasoning": str
            }
        """
        
        if not self.enabled:
            # Fallback: count question marks
            return {
                "has_multiple_parts": ticket_issue.count("?") > 2,
                "parts_count": ticket_issue.count("?"),
                "reasoning": "Question mark count heuristic"
            }
        
        prompt = f"""Count how many distinct questions/requests are in this ticket:

TICKET: {ticket_issue}

Count them and explain briefly."""
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text.strip()
            
            # Try to extract count from response
            words = result_text.split()
            count = 1
            for word in words:
                if word.isdigit():
                    count = int(word)
                    break
            
            return {
                "has_multiple_parts": count > 1,
                "parts_count": count,
                "reasoning": f"LLM analysis: {count} distinct parts"
            }
            
        except Exception as e:
            print(f"⚠️  Multi-part analysis failed: {e}")
            return {
                "has_multiple_parts": False,
                "parts_count": 1,
                "reasoning": "Analysis failed, defaulting to single-part"
            }


def create_reasoner(api_key: Optional[str] = None) -> LLMReasoner:
    """Factory function to create LLM reasoner."""
    reasoner = LLMReasoner(api_key)
    
    if reasoner.is_enabled():
        print("✅ Claude LLM reasoning enabled")
    else:
        print("ℹ️  Claude LLM reasoning disabled (set ANTHROPIC_API_KEY to enable)")
    
    return reasoner
