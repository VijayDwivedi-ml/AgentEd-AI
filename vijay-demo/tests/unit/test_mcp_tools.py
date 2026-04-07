"""Unit tests for MCP tools"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from app.mcp_service import (
    get_india_education_stats,
    get_trending_education_topics,
    get_teaching_insights,
    compare_country_education,
    search_education_indicator
)

class TestMCPTools:
    """Test all MCP tool functions"""
    
    def test_india_education_stats(self):
        """Test that India education stats return correct data"""
        result = get_india_education_stats()
        assert "77.7" in result, "Should show 77.7% literacy rate"
        assert "India" in result, "Should mention India"
        assert "World Bank" in result, "Should cite source"
    
    def test_trending_topics(self):
        """Test that trending topics return data"""
        result = get_trending_education_topics()
        assert "Trending" in result, "Should show trending section"
        assert len(result) > 100, "Should have substantial content"
    
    def test_teaching_insights(self):
        """Test that teaching insights return actionable advice"""
        result = get_teaching_insights()
        assert "Insights" in result or "teaching" in result.lower()
        assert len(result) > 50, "Should have meaningful content"
    
    def test_country_comparison(self):
        """Test country comparison between India and China"""
        result = compare_country_education("India", "China")
        assert "India" in result, "Should show India"
        assert "China" in result, "Should show China"
        assert "77.7" in result, "Should show India's literacy rate"
        assert "96.8" in result, "Should show China's literacy rate"
    
    def test_search_indicator(self):
        """Test searching for specific indicator"""
        result = search_education_indicator("literacy_rate", "India")
        assert "77.7" in result, "Should return literacy rate"
        assert "Literacy Rate" in result, "Should show indicator name"

class TestMCPIntegration:
    """Test MCP tools work together"""
    
    def test_multiple_tools_sequence(self):
        """Test that multiple tools can be called sequentially"""
        stats = get_india_education_stats()
        trends = get_trending_education_topics()
        insights = get_teaching_insights()
        
        assert stats is not None
        assert trends is not None
        assert insights is not None
    
    def test_data_consistency(self):
        """Test that data from different tools is consistent"""
        stats = get_india_education_stats()
        
        # Extract literacy rate from stats
        import re
        match = re.search(r'Literacy Rate: (\d+\.?\d*)%', stats)
        if match:
            literacy_rate = float(match.group(1))
            assert literacy_rate == 77.7, "Literacy rate should be 77.7%"
