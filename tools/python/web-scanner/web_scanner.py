import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from sys import argv
        
def test_sql_injection(url):
    sql_injection_test_string = "' OR 1=1 --"
    payload = {
        'query': sql_injection_test_string
    }
    injection_url = url + '?' + urlparse.urlencode(payload)
    response = requests.get(injection_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    if sql_injection_test_string in soup.text:
        print(f"SQL Injection vulnerability found in {url}")
    else:
        print(f"No SQL Injection vulnerability found in {url}")

def test_xss(url):
    xss_test_string = "<script>alert('XSS');</script>"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    payload = {
        'query': xss_test_string
    }
    xss_url = url + '?' + urlparse.urlencode(payload)
    response = requests.get(xss_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    if xss_test_string in soup.text:
        print(f"XSS vulnerability found in {url}")
    else:
        print(f"No XSS vulnerability found in {url}")

url = argv[1]
test_sql_injection(url)
test_xss(url)