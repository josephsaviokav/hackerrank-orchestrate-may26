"""
Main: Support Ticket Triage Agent
Terminal-based agent that routes support tickets across HackerRank, Claude, and Visa.

Usage:
    python main.py                    # Process production tickets
    python main.py --sample          # Test on sample tickets
    python main.py --debug-index     # Show corpus index summary
    python main.py --debug-classify  # Test classification on samples
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from corpus_indexer import create_indexer
from data_loader import create_loader
from classifier import create_classifier
from retriever import create_retriever
from router import create_router


class SupportTriageAgent:
    """Main orchestrator for support ticket triage."""
    
    def __init__(self, data_dir: str = "data", tickets_dir: str = "support_tickets"):
        """Initialize agent with corpus and data loaders."""
        print("🔧 Initializing Support Triage Agent...")
        
        self.data_loader = create_loader(tickets_dir)
        self.corpus_indexer = create_indexer(data_dir)
        self.classifier = create_classifier()
        self.retriever = create_retriever(self.corpus_indexer)
        self.router = create_router()
        
        print(f"✓ Corpus indexed: {self.corpus_indexer.doc_count} documents")
        print(f"✓ Ready to process tickets\n")
    
    def process_ticket(self, ticket: Dict[str, str]) -> Dict[str, Any]:
        """Process a single support ticket through the pipeline."""
        
        issue = ticket.get("Issue", "")
        subject = ticket.get("Subject", "")
        company = ticket.get("Company", None)
        
        # Step 1: Classify ticket
        classification = self.classifier.classify_ticket(issue, subject, company)
        
        # Step 2: Retrieve relevant docs
        query = f"{subject} {issue}"
        inferred_company = classification.get("company")
        retrieval_result = self.retriever.get_best_match(query, inferred_company)
        
        # Step 3: Route and generate response
        routed = self.router.route_ticket(classification, retrieval_result, ticket)
        
        return routed
    
    def process_tickets(self, tickets: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Process multiple tickets."""
        results = []
        
        for i, ticket in enumerate(tickets, 1):
            result = self.process_ticket(ticket)
            results.append(result)
            
            # Print progress
            if i % 5 == 0:
                print(f"  Processed {i}/{len(tickets)} tickets...")
        
        return results
    
    def run_on_production(self):
        """Run agent on production tickets and save output."""
        print("📋 Loading production tickets...")
        tickets = self.data_loader.load_production_tickets()
        print(f"✓ Loaded {len(tickets)} tickets\n")
        
        print("⚙️  Processing tickets...")
        results = self.process_tickets(tickets)
        print(f"✓ Processed {len(results)} tickets\n")
        
        print("💾 Saving output...")
        self.data_loader.save_output(results)
        
        # Validate
        validation = self.data_loader.validate_output(results)
        print(f"✓ Validation: {validation['total_rows']} rows")
        if validation['errors']:
            print(f"⚠️  {len(validation['errors'])} errors found")
            for error in validation['errors'][:3]:
                print(f"   - {error}")
        if validation['warnings']:
            print(f"⚠️  {len(validation['warnings'])} warnings")
    
    def run_on_sample(self):
        """Run agent on sample tickets for testing."""
        print("📋 Loading sample tickets...")
        tickets = self.data_loader.load_sample_tickets()
        print(f"✓ Loaded {len(tickets)} sample tickets\n")
        
        print("⚙️  Processing tickets...")
        results = self.process_tickets(tickets)
        print(f"✓ Processed {len(results)} tickets\n")
        
        # Compare against expected outputs
        print("📊 Sample Results (first 3):")
        for i, (ticket, result) in enumerate(zip(tickets[:3], results[:3]), 1):
            print(f"\n  [{i}] {ticket.get('Subject', 'No subject')[:50]}")
            print(f"      Status: {result['status']} | Type: {result['request_type']}")
            print(f"      Area: {result['product_area']}")
            if 'Response' in ticket:  # Has expected output
                expected_status = ticket.get('Status', 'unknown')
                match = "✓" if result['status'] == expected_status else "✗"
                print(f"      Expected status: {expected_status} {match}")
    
    def show_corpus_summary(self):
        """Display corpus statistics."""
        summary = self.corpus_indexer.get_summary()
        
        print("📚 Corpus Summary:")
        print(f"   Total documents: {summary['total_docs']}\n")
        
        for company, stats in summary['companies'].items():
            print(f"   {company}:")
            print(f"     - Categories: {stats['categories']}")
            print(f"     - Documents: {stats['docs']}")
            if stats['categories_list']:
                categories = ", ".join(stats['categories_list'][:5])
                if len(stats['categories_list']) > 5:
                    categories += f", ... (+{len(stats['categories_list']) - 5} more)"
                print(f"     - Examples: {categories}\n")
    
    def debug_classify_sample(self):
        """Debug classification on sample tickets."""
        print("🔍 Testing Classifier on Sample Tickets:\n")
        
        tickets = self.data_loader.load_sample_tickets()[:5]
        
        for i, ticket in enumerate(tickets, 1):
            issue = ticket.get("Issue", "")[:100]
            subject = ticket.get("Subject", "")
            company = ticket.get("Company", "?")
            
            classification = self.classifier.classify_ticket(
                ticket.get("Issue", ""),
                ticket.get("Subject", ""),
                company
            )
            
            print(f"  [{i}] {subject}")
            print(f"      Input company: {company}")
            print(f"      Inferred company: {classification['company']}")
            print(f"      Request type: {classification['request_type']}")
            print(f"      Product area: {classification['product_area']}")
            print(f"      Risk level: {classification['risk_level']}")
            print(f"      Should escalate: {classification['should_escalate']}\n")
    

def main():
    """Main entry point."""
    
    # Check if we're in the right directory
    if not Path("data").exists() or not Path("support_tickets").exists():
        print("❌ Error: data/ and support_tickets/ directories not found")
        print("   Please run from the repository root directory")
        sys.exit(1)
    
    # Create agent
    agent = SupportTriageAgent()
    
    # Parse arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--sample":
            agent.run_on_sample()
        elif command == "--debug-index":
            agent.show_corpus_summary()
        elif command == "--debug-classify":
            agent.debug_classify_sample()
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)
    else:
        # Default: run on production tickets
        agent.run_on_production()


if __name__ == "__main__":
    main()
