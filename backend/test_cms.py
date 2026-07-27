from scanner.cms_detector import detect_cms

websites = [
    "https://wordpress.com",
    "https://shopify.com",
    "https://github.com"
]

for site in websites:

    print("\n", site)

    print(detect_cms(site))