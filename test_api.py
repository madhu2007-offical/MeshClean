#!/usr/bin/env python
"""Test Flask API endpoints"""

import requests
import json

print("Testing Flask API endpoints...\n")

# Test 1: Task endpoint
print("[1] Testing /api/task endpoint...")
try:
    response = requests.get('http://localhost:7860/api/task?id=task_1', timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Run endpoint
print("\n[2] Testing /api/run endpoint...")
try:
    response = requests.get('http://localhost:7860/api/run?task=task_1', timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Logs: {data.get('logs', '')[:200]}...")
        print(f"Analysis: {data.get('analysis', '')[:200]}...")
        print(f"Summary: {data.get('summary', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
