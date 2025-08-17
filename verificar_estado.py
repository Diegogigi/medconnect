#!/usr/bin/env python3
import requests

try:
    # Verificar endpoint de health
    r = requests.get('http://localhost:5000/health')
    print(f"Health endpoint: {r.status_code}")
    
    # Verificar endpoint de profile
    r = requests.get('http://localhost:5000/api/professional/profile')
    print(f"Profile endpoint: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    print(f"Response length: {len(r.text)}")
    print(f"Response preview: {r.text[:100]}")
    
except Exception as e:
    print(f"Error: {e}") 