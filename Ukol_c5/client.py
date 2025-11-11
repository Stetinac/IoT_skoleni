import requests

# response = requests.post("http://localhost:5006/api/switch", json={"state": "off"})
response = requests.post("http://localhost:5006/api/switch2", json={"manstate": "off"})

print(response.status_code)
print(response.json())