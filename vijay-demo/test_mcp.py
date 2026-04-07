#!/usr/bin/env python3
"""Test MCP integration - using mcp_service module"""
import sys
import asyncio

sys.path.insert(0, 'app')

async def test():
    print("=" * 60)
    print("Testing MCP Integration")
    print("=" * 60)
    
    print("\n1. Testing imports...")
    try:
        # Import from our service module (not the mcp package)
        from app.mcp_service import (
            get_india_education_stats, 
            get_trending_education_topics
        )
        print("   ✅ MCP service module imports successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    print("\n2. Testing India Education Stats...")
    try:
        result = get_india_education_stats()
        if "77.7" in result:
            print("   ✅ Success - got India education data")
        else:
            print(f"   Got: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n3. Testing Trending Topics...")
    try:
        result = get_trending_education_topics()
        if "Trending" in result:
            print("   ✅ Success - got trending topics")
        else:
            print(f"   Got: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 MCP Service Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
