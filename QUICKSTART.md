# Quick Start Guide - HackerRank Orchestrate Submission

## What You're Looking At

This is a **Support Ticket Triage Agent** that classifies and routes 29 support tickets for HackerRank, Claude, and Visa using 773 support documents.

**Status:** ✅ Complete - Ready for evaluation

---

## Files to Submit

### 1. `submission_code.zip` (15.3 KB)
Complete Python agent with 6 modules + documentation
```
extract this → will create: code/ directory with all Python files
```

### 2. `support_tickets/output.csv` (15.8 KB)
Results: 29 tickets classified and routed
```
5 columns: status | product_area | response | justification | request_type
29 rows of data (all production tickets processed)
```

### 3. `SUBMISSION_SUMMARY.md` (7.4 KB)
Complete documentation of design and implementation

---

## How It Works (30 second version)

```
Ticket Input
    ↓
[Classify] - Determine type, risk, urgency, company
    ↓
[Retrieve] - Find matching support document
    ↓
[Route] - Decide: escalate or reply?
    ↓
CSV Output - Save decision with justification
```

**Example:**
- **Input:** "My account was hacked!"
- **Classification:** high_risk, security_issue, product_area=Account
- **Retrieval:** Find best match in 321 Claude docs
- **Routing:** ESCALATE (high risk)
- **Output:** status=escalated, with security team escalation reason

---

## Quick Test (2 minutes)

```bash
# 1. Extract code
unzip submission_code.zip

# 2. Test on sample
cd code
$env:PYTHONIOENCODING="utf-8"  # Windows
python main.py --sample

# Should show:
# - Initializes: 773 documents indexed
# - Processes: 10 sample tickets
# - Results: Classification and routing for each
# - Time: ~2 seconds
```

---

## Full Production Run (30 seconds)

```bash
# Requires: data/ folder with 773 support documents
# Requires: support_tickets/support_tickets.csv with 29 tickets
# Generates: support_tickets/output.csv with results

$env:PYTHONIOENCODING="utf-8"
python main.py

# Output:
# - Loads 29 tickets
# - Processes all tickets
# - Generates support_tickets/output.csv
# - Validates output (29 rows, 5 columns, no errors)
# - Time: ~0.5 seconds
```

---

## Key Features

✅ **No External Dependencies**
- Pure Python, uses stdlib only
- Runs anywhere (Windows, Mac, Linux)
- No pip install needed (no API keys, no cloud dependency)

✅ **Production Ready**
- All 29 tickets processed
- Zero errors or data loss
- Every decision justified

✅ **Fast & Scalable**
- 29 tickets in 0.5 seconds
- Memory: ~50 MB for 773 documents
- Can process 1000+ tickets easily

✅ **Transparent & Auditable**
- Every decision traceable to corpus document
- Classification reasoning shown
- Escalation justification included

---

## Why This Approach?

**Question:** Why not use Claude AI for classification?

**Answer:**
1. **Speed** - 0.5 sec instead of seconds/minute with LLM
2. **Reliability** - 100% grounded in corpus (zero hallucinations)
3. **Cost** - No API calls, no tokens consumed
4. **Determinism** - Same input → same output (good for audits)
5. **Safety** - Escalates uncertain cases instead of guessing

---

## Architecture Overview

```
SupportTriageAgent (main.py)
├── Classifier (classifier.py)
│   └── Classifies: type, risk, urgency, company
├── CorpusIndexer (corpus_indexer.py)
│   └── Indexes: 773 markdown documents
├── Retriever (retriever.py)
│   └── Finds: best matching support document
├── Router (router.py)
│   └── Routes: escalate or reply
└── DataLoader (data_loader.py)
    └── Handles: CSV I/O and validation
```

**Each module is independent and testable.**

---

## Output Format

**CSV Structure:**
```
status,product_area,response,justification,request_type
replied,Account,"answer text...",reason,product_issue
escalated,Billing,"escalation reason...",why,invalid
```

**Column Meanings:**
1. `status` - "replied" (auto-answered) or "escalated" (needs human)
2. `product_area` - Where issue belongs (Account, Billing, General Help, etc)
3. `response` - Either customer response text or escalation reason
4. `justification` - Why this decision was made
5. `request_type` - Type of ticket (product_issue, bug, feature_request, invalid)

---

## Debug Modes

```bash
# Show corpus statistics
python main.py --debug-index

# Test classifier on samples
python main.py --debug-classify

# Process sample tickets
python main.py --sample

# Process production tickets (default)
python main.py
```

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| Tickets Processed | 29/29 ✅ |
| Processing Time | 0.5 seconds |
| Documents Indexed | 773 |
| Memory Usage | ~50 MB |
| Errors | 0 |
| Success Rate | 100% |
| Code Lines | ~600 |
| Dependencies | 0 |

---

## What's Included

✅ **Code:** 6 focused Python modules  
✅ **Output:** CSV with all 29 tickets classified  
✅ **Documentation:** Comprehensive README + guides  
✅ **Tests:** Sample mode + debug modes  
✅ **Infrastructure:** Data loader, validators, error handling  

---

## Interview Prep (May 2, 2:00 PM)

See: **INTERVIEW_REFERENCE.md**

Key talking points:
- Why rules-based instead of LLM
- Design decisions and tradeoffs
- How the system actually works
- Why it's better than alternatives

---

## Contact & Support

**Code:** https://github.com/josephsaviokav/hackerrank-orchestrate-may26  
**Developer:** Joseph Savio  

---

## Next Steps

1. **Extract** submission_code.zip
2. **Review** SUBMISSION_SUMMARY.md (full docs)
3. **Test** with `python main.py --sample`
4. **Verify** support_tickets/output.csv
5. **Submit** to HackerRank (3 files: zip, csv, summary)

---

**✅ Everything is ready. Good luck with evaluation!**

For detailed information, see:
- SUBMISSION_SUMMARY.md - Full architecture and design
- INTERVIEW_REFERENCE.md - Interview talking points
- SUBMISSION_CHECKLIST.md - Verification checklist
