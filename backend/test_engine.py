from pprint import pprint

from scanner.scanner_engine import run_scan

result = run_scan("https://github.com")

pprint(result)