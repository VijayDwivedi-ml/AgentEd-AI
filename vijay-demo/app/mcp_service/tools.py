# app/mcp_service/tools.py
"""MCP Tools for ADK Agents - Fixed for event loop handling"""
import asyncio
from typing import Optional

def _run_async(coro):
    """Run async coroutine safely, handling existing event loops"""
    try:
        # Try to get the current running loop
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    else:
        # There's a running loop, need to handle carefully
        # Create a new loop in a separate thread
        import concurrent.futures
        import threading
        
        def run_in_new_loop():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_new_loop)
            return future.result()


def get_india_education_stats() -> str:
    """Get India's education statistics from World Bank data"""
    try:
        from .service import get_mcp_orchestrator
        
        async def _get_stats():
            mcp = await get_mcp_orchestrator()
            return await mcp.worldbank.get_education_data("IN")
        
        stats = _run_async(_get_stats())
        
        return f"""
📊 **India Education Statistics (World Bank 2023)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 Literacy Rate: {stats['literacy_rate']}%
🏫 Primary Enrollment: {stats['primary_enrollment']}%
🎓 Secondary Enrollment: {stats['secondary_enrollment']}%
💰 Education Spending: {stats['education_expenditure']}% of GDP
👩‍🏫 Pupil-Teacher Ratio: {stats['pupil_teacher_ratio']}:1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: World Bank Open Data (via MCP)
"""
    except Exception as e:
        return f"❌ Error fetching education data: {str(e)}"


def get_trending_education_topics() -> str:
    """Get trending education topics in India from Google Trends"""
    try:
        from .service import get_mcp_orchestrator
        
        async def _get_trends():
            mcp = await get_mcp_orchestrator()
            return await mcp.trends.get_trending("India", "education")
        
        trends = _run_async(_get_trends())
        
        lines = "\n".join([f"   {i+1}. 🔥 {t}" for i, t in enumerate(trends)])
        
        return f"""
🔥 **Trending Education Topics in India**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{lines}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Tip: Use these topics to make your lessons relevant!
Source: Google Trends (via MCP)
"""
    except Exception as e:
        return f"❌ Error fetching trending topics: {str(e)}"


def get_teaching_insights() -> str:
    """Get AI-powered teaching insights from MCP data"""
    try:
        from .service import get_mcp_orchestrator
        
        async def _get_insights():
            mcp = await get_mcp_orchestrator()
            return await mcp.get_insights()
        
        insights = _run_async(_get_insights())
        
        return f"""
💡 **Teaching Insights (Powered by MCP)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{insights}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    except Exception as e:
        return f"❌ Error getting insights: {str(e)}"


def compare_country_education(country1: str = "India", country2: str = "United States") -> str:
    """Compare education metrics between two countries"""
    try:
        from .service import get_mcp_orchestrator
        
        async def _compare():
            mcp = await get_mcp_orchestrator()
            
            # Map country names to codes
            country_map = {
                "india": "IN", "united states": "US", "usa": "US", "us": "US",
                "china": "CN", "japan": "JP", "uk": "GB", "germany": "DE"
            }
            
            code1 = country_map.get(country1.lower(), "IN")
            code2 = country_map.get(country2.lower(), "US")
            
            stats1 = await mcp.worldbank.get_education_data(code1)
            stats2 = await mcp.worldbank.get_education_data(code2)
            return stats1, stats2
        
        stats1, stats2 = _run_async(_compare())
        
        return f"""
📊 **Education Comparison: {stats1['country']} vs {stats2['country']}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric                          | {stats1['country'][:15]:15} | {stats2['country'][:15]:15}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Literacy Rate (%)              | {stats1['literacy_rate']:>15} | {stats2['literacy_rate']:>15}
Primary Enrollment (%)         | {stats1['primary_enrollment']:>15} | {stats2['primary_enrollment']:>15}
Secondary Enrollment (%)       | {stats1['secondary_enrollment']:>15} | {stats2['secondary_enrollment']:>15}
Education Spending (% GDP)     | {stats1['education_expenditure']:>15} | {stats2['education_expenditure']:>15}
Pupil-Teacher Ratio            | {stats1['pupil_teacher_ratio']:>15} | {stats2['pupil_teacher_ratio']:>15}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: World Bank Open Data (via MCP)
"""
    except Exception as e:
        return f"❌ Error comparing countries: {str(e)}"


def search_education_indicator(indicator: str = "literacy_rate", country: str = "India") -> str:
    """Search for a specific education indicator"""
    try:
        from .service import get_mcp_orchestrator
        
        async def _search():
            mcp = await get_mcp_orchestrator()
            
            country_map = {"india": "IN", "us": "US", "usa": "US", "china": "CN"}
            code = country_map.get(country.lower(), "IN")
            
            return await mcp.worldbank.get_education_data(code)
        
        stats = _run_async(_search())
        
        indicator_names = {
            "literacy_rate": "📖 Literacy Rate",
            "primary_enrollment": "🏫 Primary Enrollment", 
            "secondary_enrollment": "🎓 Secondary Enrollment",
            "tertiary_enrollment": "🏛️ Tertiary Enrollment",
            "education_expenditure": "💰 Education Spending",
            "pupil_teacher_ratio": "👩‍🏫 Pupil-Teacher Ratio"
        }
        
        name = indicator_names.get(indicator, indicator.replace("_", " ").title())
        value = stats.get(indicator, "N/A")
        unit = "%" if indicator not in ["pupil_teacher_ratio"] else ""
        
        return f"""
🔍 **{name} for {stats['country']}**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Value: {value}{unit}
📅 Year: {stats['year']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    except Exception as e:
        return f"❌ Error searching indicator: {str(e)}"
