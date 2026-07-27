SECURITY_HEADERS = {
    "Content-Security-Policy": {
        "severity": "High",
        "description": "Helps prevent Cross-Site Scripting (XSS) attacks.",
        "recommendation": "Configure a Content-Security-Policy response header."
    },

    "X-Frame-Options": {
        "severity": "High",
        "description": "Protects against clickjacking attacks.",
        "recommendation": "Set X-Frame-Options to DENY or SAMEORIGIN."
    },

    "Strict-Transport-Security": {
        "severity": "High",
        "description": "Forces browsers to use HTTPS.",
        "recommendation": "Enable HSTS with an appropriate max-age."
    },

    "X-Content-Type-Options": {
        "severity": "Medium",
        "description": "Prevents MIME type sniffing.",
        "recommendation": "Set X-Content-Type-Options to nosniff."
    },

    "Referrer-Policy": {
        "severity": "Medium",
        "description": "Controls how much referrer information is shared.",
        "recommendation": "Configure an appropriate Referrer-Policy."
    },

    "Permissions-Policy": {
        "severity": "Low",
        "description": "Restricts browser features available to websites.",
        "recommendation": "Define a Permissions-Policy response header."
    }
}