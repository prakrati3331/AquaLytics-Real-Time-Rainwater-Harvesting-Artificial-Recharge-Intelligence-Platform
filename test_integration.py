#!/usr/bin/env python3
"""
Simple test script for the integrated_app.py
Run this to verify the application starts correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from integrated_app import app
    print("✅ Successfully imported integrated_app")
    print(f"📱 App title: {app.title}")
    print(f"📝 Description: {app.description}")
    print(f"🔗 Available routes:")

    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"   {route.methods} {route.path}")

    print("\n✅ Integration successful!")
    print("🚀 You can now run: uvicorn integrated_app:app --reload")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
