from __future__ import annotations

CATEGORY_KEYWORDS = {
    "ransomware": {"ransomware", "extortion", "encryptor"},
    "data-breach": {"data breach", "breach", "leaked data", "stolen data", "exposed records"},
    "vulnerability": {"vulnerability", "cve-", "zero-day", "0-day", "security flaw", "patch"},
    "malware": {"malware", "trojan", "backdoor", "botnet", "infostealer", "rootkit", "spyware"},
    "phishing": {"phishing", "credential theft", "social engineering", "smishing"},
    "cloud-security": {"aws", "azure", "google cloud", "kubernetes", "cloud security", "container"},
    "supply-chain": {"supply chain", "dependency", "npm", "pypi", "package repository", "software supply"},
    "threat-intelligence": {"apt", "threat actor", "campaign", "nation-state", "threat intelligence"},
    "privacy": {"privacy", "surveillance", "tracking", "personal data"},
}


def classify(title: str, summary: str | None) -> set[str]:
    haystack = f"{title} {summary or ''}".lower()
    result = {
        slug
        for slug, keywords in CATEGORY_KEYWORDS.items()
        if any(keyword in haystack for keyword in keywords)
    }
    return result or {"general-security"}
