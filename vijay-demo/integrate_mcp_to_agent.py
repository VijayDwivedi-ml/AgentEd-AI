#!/usr/bin/env python3
"""Automatically add MCP Service imports to agent.py"""
import re

# Read agent.py
with open('app/agent.py', 'r') as f:
    content = f.read()

# 1. Add MCP Service imports (using mcp_service, not mcp)
if 'from app.mcp_service import' not in content:
    print("Adding MCP Service imports to agent.py...")
    
    # Find where to add imports
    import_pattern = r'(from google\.cloud\.firestore_v1\.base_query import FieldFilter)'
    mcp_imports = r'\1\n\n# MCP Service Integration - World Bank and Google Trends data\nfrom app.mcp_service import (\n    get_india_education_stats,\n    get_trending_education_topics,\n    get_teaching_insights,\n    compare_country_education,\n    search_education_indicator\n)'
    
    content = re.sub(import_pattern, mcp_imports, content)
    print("   ✅ Added MCP Service imports")
else:
    print("MCP Service imports already present")

# Write back
with open('app/agent.py', 'w') as f:
    f.write(content)

print("\n✅ Integration complete!")
print("\nTo verify, run:")
print("  uv run python -c \"from app.agent import *; print('Agent loaded successfully')\"")
