# app/mcp_service/__init__.py
"""MCP Service Layer for Teacher Assistant"""
from .service import get_mcp_orchestrator, MCPOrchestrator
from .capabilities import get_enhanced_capabilities
from .tools import (
    get_india_education_stats,
    get_trending_education_topics,
    get_teaching_insights,
    compare_country_education,
    search_education_indicator
)

__all__ = [
    'get_mcp_orchestrator',
    'MCPOrchestrator',
    'get_india_education_stats',
    'get_trending_education_topics',
    'get_teaching_insights',
    'compare_country_education',
    'search_education_indicator',
    'get_enhanced_capabilities'
]
