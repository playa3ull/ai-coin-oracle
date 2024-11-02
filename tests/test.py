# test_api.py
import requests
import asyncio
from datetime import datetime


def test_endpoints():
    BASE_URL = "http://localhost:8000"

    # Test endpoints and print results
    def make_request(endpoint, method='GET'):
        print(f"\n🔍 Testing {method} {endpoint} at {datetime.now().strftime('%H:%M:%S')}")
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")

            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    # Run tests
    endpoints = [
        ('/', 'GET'),
        ('/generate-tweet', 'POST')
    ]

    for endpoint, method in endpoints:
        make_request(endpoint, method)


if __name__ == "__main__":
    test_endpoints()