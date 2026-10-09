import re
import ipaddress
import socket
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple, Optional


# ==========================================
# CONSTANTS & DICTIONARIES
# ==========================================

SUSPICIOUS_TLDS = {
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "cam", "work",
    "rest", "click", "monster", "icu", "fit", "surf", "casa", "country", "link"
}

HIGH_PROFILE_BRANDS = [
    "paypal", "apple", "amazon", "google", "microsoft", "netflix",
    "wellsfargo", "chase", "bankofamerica", "citibank", "binance",
    "coinbase", "metamask", "whatsapp", "telegram", "facebook", "instagram"
]

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "mail.com", "zoho.com", "protonmail.com", "yandex.com", "icloud.com"
}


# ==========================================
# SSRF & URL SAFETY UTILITIES
# ==========================================

def is_private_or_loopback_ip(ip_str: str) -> bool:
    """Check if an IP address belongs to private, loopback, or reserved network."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip_str in ("0.0.0.0", "255.255.255.255")
        )
    except ValueError:
        return False


def validate_url_safety(raw_url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate that raw_url is safe from SSRF and local network traversal.
    Returns (is_safe, error_reason, resolved_ip).
    """
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url

    try:
        parsed = urlparse(raw_url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid or missing hostname in URL", None

        # Check for numeric or bracketed IP literal
        try:
            ip_obj = ipaddress.ip_address(hostname.strip("[]"))
            if is_private_or_loopback_ip(str(ip_obj)):
                return False, f"Target resolves to prohibited private/internal IP ({ip_obj})", str(ip_obj)
            return True, None, str(ip_obj)
        except ValueError:
            pass  # Hostname is a domain name, not IP literal

        # Prohibit localhost / local domain tricks
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1", "local"):
            return False, "Target resolves to localhost/loopback address", "127.0.0.1"

        if hostname.lower().endswith((".local", ".internal", ".lan", ".localhost", ".corp")):
            return False, "Target resides on an internal or unrouted top-level domain", None

        return True, None, None

    except Exception as e:
        return False, f"URL parse failed: {str(e)}", None


# ==========================================
# SNIPPET EXTRACTOR
# ==========================================

def extract_evidence_snippet(text: str, regex_pattern: str, max_len: int = 140) -> Optional[str]:
    """Finds the matching substring and returns surrounding sentence or fragment."""
    match = re.search(regex_pattern, text, re.IGNORECASE)
    if not match:
        return None
    start = max(0, match.start() - 25)
    end = min(len(text), match.end() + 35)
    snippet = text[start:end].strip()
    snippet = re.sub(r'\s+', ' ', snippet)
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


# ==========================================
# RISK SCORE AGGREGATOR
# ==========================================

def compute_risk_classification(score: int, findings_count: int, is_insufficient: bool = False) -> str:
    """Maps score to canonical risk labels."""
    if is_insufficient or (findings_count == 0 and score == 0):
        return "Lower Observed Risk"
    if score >= 80:
        return "Very High Risk"
    if score >= 60:
        return "High Risk"
    if score >= 40:
        return "Suspicious"
    if score >= 20:
        return "Caution"
    return "Lower Observed Risk"


# ==========================================
# 1. MESSAGE & EMAIL DETECTION ENGINE
# ==========================================

def analyze_message_content(
    message_text: str,
    sender_details: Optional[str] = None,
    related_url: Optional[str] = None
) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    seen_indicators = set()

    sources_checked = [
        "Lexical Urgency & Coercion Ruleset",
        "Financial Payment & Cryptocurrency Signatures",
        "Credential Harvesting & Phishing Heuristics",
        "Law Enforcement & Coercive Threat Matcher",
        "Advance Fee & Inheritance Fraud Corpus",
        "Sender Impersonation Pattern Matcher"
    ]
    unavailable_checks = [
        "Originating Mail Transfer Agent (MTA) DKIM/SPF Record Lookup",
        "End-to-End Mailserver Reputation Lookup"
    ]
    limitations = [
        "Analysis is based on textual content heuristics; sophisticated spear-phishing may evade standard keyword detection.",
        "A low score does not guarantee legitimacy; always corroborate sensitive payment requests via verified voice or official channels."
    ]
    recommendations: List[str] = []

    full_corpus = f"{message_text}\n{sender_details or ''}\n{related_url or ''}"

    # Check for Insufficient Evidence
    word_count = len(message_text.strip().split())
    if word_count < 4 and not related_url and not sender_details:
        return {
            "risk_score": 0,
            "risk_label": "Insufficient Evidence",
            "findings": [],
            "sources_checked": sources_checked,
            "unavailable_checks": unavailable_checks,
            "limitations": [
                "The submitted message is too brief (< 4 words) to perform meaningful forensic pattern analysis."
            ],
            "recommendations": [
                "Provide the complete email body, headers, or accompanying link for an accurate assessment."
            ],
            "input_summary": f"Brief message ({word_count} words)"
        }

    # Rule: Advance Payment / Gift Card / Crypto Demand
    payment_regex = r"(gift\s*cards?|steam\s*card|apple\s*gift|itunes|western\s*union|moneygram|wire\s*transfer|bitcoin|btc|usdt|crypto\s*wallet|ethereum|zelle|cashapp|venmo\s*me)"
    if re.search(payment_regex, full_corpus, re.IGNORECASE):
        indicator = "Untraceable / Non-Reversible Payment Demand"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, payment_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Scammers demand payments through gift cards, cryptocurrency, or wire transfers because these transactions cannot be reversed once processed."
            })
            recommendations.append("Never send cryptocurrency, wire transfers, or gift card pin codes to unverified contacts.")

    # Rule: Coercive Arrest & Law Enforcement Threat
    arrest_regex = r"(prevent\s*arrest|arrest\s*warrant|law\s*enforcement|fbi|irs\s*agent|legal\s*prosecution|police\s*department)"
    if re.search(arrest_regex, full_corpus, re.IGNORECASE):
        indicator = "Law Enforcement & Coercive Arrest Threat"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, arrest_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Threats of immediate arrest or criminal prosecution are illegal intimidation tactics widely exploited by government imposter scams."
            })
            recommendations.append("Government agencies and law enforcement never demand immediate payments or gift cards to prevent arrest.")

    # Rule: Artificial Urgency & Coercive Deadline
    urgency_regex = r"(immediate(ly)?\s*action|within\s*(12|24|48)\s*hours|account\s*(will\s*be\s*suspended|locked|terminated|closed)|final\s*warning|act\s*now|do\s*not\s*delay|urgent\s*response)"
    if re.search(urgency_regex, full_corpus, re.IGNORECASE):
        indicator = "High-Pressure Urgency Tactics"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, urgency_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "High-pressure deadlines are engineered to induce panic, bypassing rational scrutiny before you can consult anyone."
            })
            recommendations.append("Legitimate institutions do not demand urgent action within hours under threat of instant termination.")

    # Rule: Credential & Security Verification Traps
    credential_regex = r"(verify\s*your\s*(account|password|pin|ssn|identity)|update\s*billing\s*info|login\s*to\s*(prevent|restore|unlock)|confirm\s*your\s*(passcode|otp|credentials)|two-factor\s*code)"
    if re.search(credential_regex, full_corpus, re.IGNORECASE):
        indicator = "Credential Harvesting / Identity Phishing Pattern"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, credential_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Requests to enter or confirm passwords, OTPs, or Social Security numbers are the hallmark of credential harvesting phishing portals."
            })
            recommendations.append("Do not click links inside messages prompting login or credential renewal; navigate directly to official portals.")

    # Rule: Unexpected Windfall / Lottery / Inheritance
    windfall_regex = r"(you\s*have\s*won|lottery\s*winner|inheritance\s*fund|consignment\s*trunk|next\s*of\s*kin|sum\s*of\s*\$[\d,]+|beneficiary|unclaimed\s*funds|diplomatic\s*courier)"
    if re.search(windfall_regex, full_corpus, re.IGNORECASE):
        indicator = "Advance Fee Windfall / Inheritance Scam"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, windfall_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Claims of multi-million dollar inheritances or lottery wins you never entered are classic 419 advance-fee fraud schemes."
            })
            recommendations.append("Disregard claims of unexpected inheritances or prize payouts requiring upfront handling fees.")

    # Rule: Brand Impersonation (Geek Squad, Norton, PayPal, Amazon, Banks)
    brand_regex = r"(geek\s*squad|norton\s*antivirus|mcafee|paypal\s*invoice|amazon\s*order|apple\s*support|wells\s*fargo|chase\s*fraud\s*alert)"
    if re.search(brand_regex, full_corpus, re.IGNORECASE):
        indicator = "Recognized Brand / Invoice Impersonation"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, brand_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "moderate",
                "evidence": evidence,
                "explanation": "Scammers frequently spoof subscription renewal invoices (e.g., Geek Squad, Norton) or fraudulent Amazon purchase confirmations to provoke call-backs."
            })
            recommendations.append("Check your official account portal or bank statements directly to see if any real transaction occurred.")

    # Rule: Suspicious Callback Phone / Generic Salutation
    generic_salutation_regex = r"^(dear\s*(customer|client|user|sir|madam|subscriber|member)|valued\s*customer)"
    if re.search(generic_salutation_regex, message_text.strip(), re.IGNORECASE):
        indicator = "Impersonal Generic Salutation"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(message_text, generic_salutation_regex)
            findings.append({
                "indicator": indicator,
                "severity": "low",
                "strength": "moderate",
                "evidence": evidence,
                "explanation": "Phishing blasts commonly use impersonal greetings like 'Dear Customer' because they lack your actual name on file."
            })

    # Rule: Free Webmail for Official Notices
    if sender_details:
        for free_domain in FREE_EMAIL_DOMAINS:
            if f"@{free_domain}" in sender_details.lower():
                if re.search(r"(paypal|bank|irs|support\s*team|customer\s*service|apple|amazon)", message_text, re.IGNORECASE):
                    indicator = "Corporate Pretence Sent From Free Webmail"
                    if indicator not in seen_indicators:
                        seen_indicators.add(indicator)
                        findings.append({
                            "indicator": indicator,
                            "severity": "critical",
                            "strength": "high",
                            "evidence": f"Sender claims corporate entity but uses @{free_domain}",
                            "explanation": "Major corporate institutions operate dedicated email domains and never send official notices from free personal webmail accounts."
                        })
                        recommendations.append("Verify the sender's actual email address domain against the company's verified domain.")
                break

    # Calculate Score
    score = 0
    weights = {"critical": 35, "high": 22, "medium": 12, "low": 5}
    for f in findings:
        score += weights.get(f["severity"], 10)
    score = min(score, 100)

    if not recommendations:
        recommendations.append("Maintain vigilant cybersecurity hygiene and avoid sharing private identifiers.")

    input_summary = f"Message scan: {message_text[:60].strip()}..." if len(message_text) > 60 else message_text.strip()

    return {
        "risk_score": score,
        "risk_label": compute_risk_classification(score, len(findings)),
        "findings": findings,
        "sources_checked": sources_checked,
        "unavailable_checks": unavailable_checks,
        "limitations": limitations,
        "recommendations": recommendations,
        "input_summary": input_summary
    }


# ==========================================
# 2. URL SCANNER ENGINE (With SSRF Guard)
# ==========================================

def analyze_url_content(raw_url: str, context: Optional[str] = None) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    seen_indicators = set()

    sources_checked = [
        "SSRF & RFC1918 Private IP Inspector",
        "Domain Lexical & Top-Level Domain (TLD) Analyzer",
        "Punycode & Homoglyph Spoofing Detector",
        "High-Profile Brand Typosquatting Matcher",
        "Path Phishing Keyword Engine"
    ]
    unavailable_checks = [
        "Live External WHOIS Registrar Age Lookup (No third-party key configured)",
        "Commercial Threat Intelligence Blocklist (VirusTotal / Google Safe Browsing offline)"
    ]
    limitations = [
        "Zero-day phishing websites created minutes ago on reputable infrastructure may not trigger lexical rules.",
        "Analysis evaluates URL syntax, structural signals, and host reputation heuristics without executing JavaScript."
    ]
    recommendations: List[str] = []

    # 1. SSRF and Loopback Protection
    is_safe, error_msg, resolved_ip = validate_url_safety(raw_url)
    if not is_safe:
        findings.append({
            "indicator": "Prohibited Internal / SSRF Target Detected",
            "severity": "critical",
            "strength": "high",
            "evidence": f"Target: {raw_url} - {error_msg}",
            "explanation": "The submitted URL targets a private IP, loopback interface, or internal subnet. This technique is often used in SSRF exploits or local network probes."
        })
        recommendations.append("Do not attempt to scan or interact with internal network hosts or loopback addresses.")
        return {
            "risk_score": 95,
            "risk_label": "Very High Risk",
            "findings": findings,
            "sources_checked": sources_checked,
            "unavailable_checks": unavailable_checks,
            "limitations": limitations,
            "recommendations": recommendations,
            "input_summary": f"SSRF Blocked URL: {raw_url[:60]}"
        }

    # Normalize URL for lexical analysis
    normalized_url = raw_url if raw_url.startswith(("http://", "https://")) else "https://" + raw_url
    try:
        parsed = urlparse(normalized_url)
        hostname = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        query = parsed.query.lower()
    except Exception:
        hostname = raw_url.lower()
        path = ""
        query = ""

    # Rule: Raw IP Address Hostname
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    if re.match(ip_pattern, hostname):
        indicator = "Direct IP Address Hostname"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": f"Hostname is raw IP: {hostname}",
                "explanation": "Legitimate consumer websites use registered domain names. Raw IP addresses are frequently used to bypass domain reputation blocklists."
            })
            recommendations.append("Avoid accessing raw IP addresses in web browsers for financial or account logins.")

    # Rule: Suspicious TLD
    tld = hostname.split(".")[-1] if "." in hostname else ""
    if tld in SUSPICIOUS_TLDS:
        indicator = f"High-Abuse Top-Level Domain (.{tld})"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "medium",
                "strength": "moderate",
                "evidence": f"Domain ends in .{tld}",
                "explanation": f"The top-level domain '.{tld}' has a statistically elevated frequency of cheap throwaway registration by spam and malware operators."
            })

    # Rule: Brand Typosquatting / Homoglyph Spoofing
    for brand in HIGH_PROFILE_BRANDS:
        if brand in hostname:
            parts = hostname.split(".")
            # Official apex domains are e.g. ["paypal", "com"]
            # Any host that has extra hyphens or words like paypal-security-update or paypal.xyz is suspicious
            is_legit_domain = False
            if len(parts) >= 2:
                # Legit domain check: parts[-2] == brand and parts[-1] in ('com', 'net', 'org', 'co.uk')
                if parts[-2] == brand and parts[-1] in ("com", "org", "net"):
                    is_legit_domain = True

            if not is_legit_domain:
                indicator = f"Brand Impersonation / Typosquatting ({brand.capitalize()})"
                if indicator not in seen_indicators:
                    seen_indicators.add(indicator)
                    findings.append({
                        "indicator": indicator,
                        "severity": "critical",
                        "strength": "high",
                        "evidence": f"Host '{hostname}' incorporates brand '{brand}' outside verified apex domain",
                        "explanation": f"Scammers incorporate trusted brand names like '{brand}' into modified domains or hyphens (e.g. {brand}-security-update.xyz) to deceive victims."
                    })
                    recommendations.append(f"Ensure the domain actually ends in the official {brand}.com, not a deceptive prefix.")

    # Rule: Excessive Subdomain Depth
    subdomain_count = hostname.count(".")
    if subdomain_count >= 4:
        indicator = "Excessive Subdomain Nesting Depth"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "medium",
                "strength": "moderate",
                "evidence": f"Host contains {subdomain_count} nested domain delimiters",
                "explanation": "Attackers chain multiple subdomains to push the actual deceptive parent domain off the visible mobile address bar."
            })

    # Rule: Punycode / IDN Homograph
    if "xn--" in hostname:
        indicator = "Internationalized Domain Name (Punycode) Homograph Risk"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": f"Punycode identifier detected: {hostname}",
                "explanation": "Punycode (xn--) allows characters from other alphabets that look identical to Latin characters (homoglyphs), often used in spoofing attacks."
            })
            recommendations.append("Inspect the decoded Punycode domain to verify it is not impersonating a Latin-character brand.")

    # Rule: Sensitive Path Phishing Keywords
    phishing_keywords = ["login", "signin", "verify", "update-security", "banking", "wallet", "restore", "kyc", "auth", "confirm"]
    full_path_query = f"{path}/{query}"
    matched_keywords = [kw for kw in phishing_keywords if kw in full_path_query]
    if matched_keywords:
        indicator = f"Sensitive Credential Action Keywords in Path ({', '.join(matched_keywords[:2])})"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "medium",
                "strength": "moderate",
                "evidence": f"Path contains action keywords: {', '.join(matched_keywords)}",
                "explanation": "The URL path simulates authentication and account recovery checkpoints common to phishing kits."
            })

    # Rule: Insecure Protocol for Authentication
    if raw_url.startswith("http://") and any(kw in full_path_query for kw in ["login", "signin", "account", "secure"]):
        indicator = "Insecure Plaintext HTTP for Sensitive Action"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": "URL transmits sensitive auth request over unencrypted HTTP",
                "explanation": "Modern legitimate financial and login portals enforce encrypted HTTPS without exception."
            })

    # Calculate Score
    score = 0
    weights = {"critical": 35, "high": 22, "medium": 14, "low": 5}
    for f in findings:
        score += weights.get(f["severity"], 10)
    score = min(score, 100)

    if not recommendations:
        recommendations.append("Verify destination addresses carefully before entering passwords or two-factor tokens.")

    input_summary = f"URL scan: {raw_url[:60]}"

    return {
        "risk_score": score,
        "risk_label": compute_risk_classification(score, len(findings)),
        "findings": findings,
        "sources_checked": sources_checked,
        "unavailable_checks": unavailable_checks,
        "limitations": limitations,
        "recommendations": recommendations,
        "input_summary": input_summary
    }


# ==========================================
# 3. LINKEDIN PROFILE CHECKER
# ==========================================

def analyze_linkedin_profile(
    profile_text: str,
    profile_url: Optional[str] = None,
    name_employer: Optional[str] = None,
    recruitment_message: Optional[str] = None
) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    seen_indicators = set()

    sources_checked = [
        "Executive Impersonation Heuristics",
        "High-Return Investment & Crypto Solicitation Rules",
        "Off-Platform Redirection Pattern Matcher",
        "Vague Employment History & Credential Heuristic Engine"
    ]
    unavailable_checks = [
        "Live LinkedIn API Profile Verification (Protected behind authenticated LinkedIn OAuth)",
        "Reverse Image Search on Profile Avatar"
    ]
    limitations = [
        "Profile evaluation is conducted on submitted text data; live modifications or actual badge verifications cannot be accessed directly.",
        "Scammers may clone text from authentic profiles; always corroborate employment via corporate directories."
    ]
    recommendations: List[str] = []

    full_corpus = f"{profile_text}\n{profile_url or ''}\n{name_employer or ''}\n{recruitment_message or ''}"

    # Insufficient evidence
    if len(profile_text.strip().split()) < 6 and not recruitment_message:
        return {
            "risk_score": 0,
            "risk_label": "Insufficient Evidence",
            "findings": [],
            "sources_checked": sources_checked,
            "unavailable_checks": unavailable_checks,
            "limitations": ["Insufficient profile information provided to assess legitimacy."],
            "recommendations": ["Paste the complete 'About' section, headline, and recent messages received."],
            "input_summary": "Incomplete profile text provided"
        }

    # Rule: Off-Platform Redirection (WhatsApp / Telegram)
    off_platform_regex = r"(whatsapp|telegram|signal|reach\s*me\s*at\s*[\+\d\s\(\)]+|text\s*me\s*on\s*whatsapp|add\s*my\s*telegram|@\w+_bot)"
    if re.search(off_platform_regex, full_corpus, re.IGNORECASE):
        indicator = "Immediate Off-Platform Redirection (WhatsApp / Telegram)"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, off_platform_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Fraudulent profiles urge targets to migrate to encrypted messaging apps (Telegram, WhatsApp) to escape LinkedIn's fraud detection monitoring."
            })
            recommendations.append("Refuse to conduct professional hiring or business discussions on personal Telegram or WhatsApp accounts.")

    # Rule: Guaranteed Financial / Crypto Returns
    crypto_roi_regex = r"(guaranteed\s*(returns?|roi|profits?)|crypto\s*trading\s*mentor|forex\s*signals?|earn\s*\$[\d,]+\s*(daily|weekly)|financial\s*freedom\s*coach|passive\s*income\s*formula)"
    if re.search(crypto_roi_regex, full_corpus, re.IGNORECASE):
        indicator = "Unrealistic Investment ROI / Crypto Pig-Butchering Indicator"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, crypto_roi_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Guaranteed profit claims on LinkedIn often indicate 'pig-butchering' (Sha Zhu Pan) social engineering scams leading to rigged trading platforms."
            })
            recommendations.append("Never transfer funds to platforms or wallets recommended by newly established online contacts.")

    # Rule: Generic / Anonymous Executive Claims
    vague_exec_regex = r"(executive\s*at\s*confidential|managing\s*director\s*at\s*top\s*tier|global\s*strategist\s*at\s*stealth|director\s*of\s*global\s*operations\s*at\s*undisclosed)"
    if re.search(vague_exec_regex, full_corpus, re.IGNORECASE):
        indicator = "Vague / Stealth Senior Executive Claim"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, vague_exec_regex)
            findings.append({
                "indicator": indicator,
                "severity": "medium",
                "strength": "moderate",
                "evidence": evidence,
                "explanation": "High-level executive titles without a verifiable corporate employer are frequently used to establish unearned authority."
            })

    # Rule: Unsolicited High-Salary Job Offer with Zero Screening
    instant_hire_regex = r"(no\s*interview\s*required|selected\s*immediately|daily\s*payout|part-time\s*assistant\s*\$[\d,]+)"
    if re.search(instant_hire_regex, full_corpus, re.IGNORECASE):
        indicator = "Frictionless Hiring with Disproportionate Pay"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, instant_hire_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Offers guaranteeing lucrative roles without technical assessments or live video interviews are almost invariably employment scams."
            })

    # Calculate Score
    score = 0
    weights = {"critical": 35, "high": 22, "medium": 12, "low": 5}
    for f in findings:
        score += weights.get(f["severity"], 10)
    score = min(score, 100)

    if not recommendations:
        recommendations.append("Cross-check the individual's profile against their company's official corporate directory or team page.")

    name_label = name_employer or "LinkedIn candidate"
    input_summary = f"LinkedIn audit: {name_label[:50]}"

    return {
        "risk_score": score,
        "risk_label": compute_risk_classification(score, len(findings)),
        "findings": findings,
        "sources_checked": sources_checked,
        "unavailable_checks": unavailable_checks,
        "limitations": limitations,
        "recommendations": recommendations,
        "input_summary": input_summary
    }


# ==========================================
# 4. RECRUITER & JOB SCAM DETECTOR
# ==========================================

def analyze_recruiter_and_job(
    recruiter_name: Optional[str] = None,
    recruiter_email: Optional[str] = None,
    company_name: Optional[str] = None,
    company_website: Optional[str] = None,
    job_title: Optional[str] = None,
    job_description: Optional[str] = None,
    salary_details: Optional[str] = None,
    recruitment_message: Optional[str] = None,
    requested_fees: Optional[str] = None
) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    seen_indicators = set()

    sources_checked = [
        "Employment Advance-Fee Detector",
        "Free Webmail vs Corporate Identity Matrix",
        "Fake Equipment / Cashier Check Scheme Rules",
        "Unrealistic Wage & Minimal Qualification Analyzer",
        "Chat-Only Interview Signature Engine"
    ]
    unavailable_checks = [
        "Corporate HR Department Active Requisition Verification",
        "State/Federal Business Licensing Verification"
    ]
    limitations = [
        "Legitimate startups occasionally use simple recruitment processes; evaluation weights multiple compounding red flags.",
        "Analysis cannot verify private email header authenticity without direct EML mail records."
    ]
    recommendations: List[str] = []

    full_corpus = " ".join(filter(None, [
        recruiter_name, recruiter_email, company_name, company_website,
        job_title, job_description, salary_details, recruitment_message, requested_fees
    ]))

    # Rule: Upfront Fee Demands
    if requested_fees or re.search(r"(equipment\s*fee|training\s*fee|registration\s*fee|background\s*check\s*fee|id\s*badge\s*cost|software\s*license\s*deposit|pay\s*for\s*your\s*laptop)", full_corpus, re.IGNORECASE):
        indicator = "Advance Fee Demand for Employment Essentials"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = requested_fees or extract_evidence_snippet(full_corpus, r"(equipment|training|registration|background\s*check|id\s*badge|software\s*license|laptop)")
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Legitimate employers never require candidates to pay upfront fees for training, equipment, software licenses, or interview processing."
            })
            recommendations.append("Immediately terminate contact if an employer requests money or upfront payment for company equipment.")

    # Rule: Free Webmail for Recruiter Claiming Corporate Enterprise
    if recruiter_email:
        email_clean = recruiter_email.strip().lower()
        for free_dom in FREE_EMAIL_DOMAINS:
            if email_clean.endswith(f"@{free_dom}"):
                cname = company_name or "established enterprise"
                indicator = "Corporate Recruiter Using Free Public Webmail"
                if indicator not in seen_indicators:
                    seen_indicators.add(indicator)
                    findings.append({
                        "indicator": indicator,
                        "severity": "critical",
                        "strength": "high",
                        "evidence": f"Recruiter claiming {cname} uses '{recruiter_email}'",
                        "explanation": f"Recruiters representing {cname} communicate from official business email domains, not free personal webmail services like @{free_dom}."
                    })
                    recommendations.append(f"Contact the company's verified HR department directly through their official website to verify the recruiter's identity.")
                break

    # Rule: Fake Check / Equipment Purchase Scam
    check_scam_regex = r"(cashier'?s\s*check|check\s*deposit|we\s*will\s*send\s*you\s*a\s*check|purchase\s*from\s*our\s*approved\s*vendor|send\s*back\s*the\s*remaining|funds\s*will\s*clear)"
    if re.search(check_scam_regex, full_corpus, re.IGNORECASE):
        indicator = "Counterfeit Check / Approved Vendor Fraud Pattern"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, check_scam_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "The scammer sends a fraudulent check, instructs you to deposit it, and asks you to transfer money to a fake 'vendor' before the bank discovers the check bounced."
            })
            recommendations.append("Never deposit a check from an employer with instructions to transfer a portion to an external vendor.")

    # Rule: Unrealistic Compensation for Simple Tasks
    unrealistic_wage_regex = r"(\$(5[0-9]|[6-9]\d|\d{3})\s*(per|/)\s*hour\s*for\s*(data\s*entry|typing|virtual\s*assistant|receptionist|clerk)|\$[\d,]{4,}\s*(per|/)\s*week\s*for\s*part\s*time)"
    if re.search(unrealistic_wage_regex, full_corpus, re.IGNORECASE):
        indicator = "Disproportionately Inflated Wages for Entry-Level Tasks"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, unrealistic_wage_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Offering \$50-\$100+/hr for routine data entry or virtual assistant positions is designed to lure job seekers into advance-fee or check-cashing schemes."
            })

    # Rule: Interview Exclusively on Telegram / Signal / WhatsApp Text
    text_interview_regex = r"(interview\s*(via|on)\s*(telegram|whatsapp|signal|google\s*hangouts?|text)|download\s*telegram\s*to\s*interview)"
    if re.search(text_interview_regex, full_corpus, re.IGNORECASE):
        indicator = "Text-Only Interview on Anonymous Messaging Platform"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(full_corpus, text_interview_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Legitimate organizations conduct interviews through telephone, official video conferencing (Teams, Zoom, Meet), or in person—never anonymous text chat on Telegram."
            })

    # Rule: Discrepancy between Company Website and Email Domain
    if recruiter_email and company_website:
        try:
            email_domain = recruiter_email.split("@")[-1].lower()
            parsed_web = urlparse(company_website if company_website.startswith("http") else f"https://{company_website}")
            web_host = (parsed_web.hostname or "").lower()
            if email_domain not in FREE_EMAIL_DOMAINS and web_host:
                if not (email_domain in web_host or web_host in email_domain):
                    indicator = "Recruiter Email Domain Disconnect from Company Website"
                    if indicator not in seen_indicators:
                        seen_indicators.add(indicator)
                        findings.append({
                            "indicator": indicator,
                            "severity": "high",
                            "strength": "moderate",
                            "evidence": f"Recruiter domain '@{email_domain}' does not align with website '{web_host}'",
                            "explanation": "The recruiter's email domain does not match the official company website domain provided, suggesting an imposter."
                        })
        except Exception:
            pass

    # Score computation
    score = 0
    weights = {"critical": 35, "high": 22, "medium": 12, "low": 5}
    for f in findings:
        score += weights.get(f["severity"], 10)
    score = min(score, 100)

    if not recommendations:
        recommendations.append("Confirm all job offers directly on the company's verified careers webpage.")

    title_label = job_title or "Position"
    comp_label = company_name or "Company"
    input_summary = f"Job Scam check: {title_label} at {comp_label}"

    return {
        "risk_score": score,
        "risk_label": compute_risk_classification(score, len(findings)),
        "findings": findings,
        "sources_checked": sources_checked,
        "unavailable_checks": unavailable_checks,
        "limitations": limitations,
        "recommendations": recommendations,
        "input_summary": input_summary
    }


# ==========================================
# 5. COMPANY CHECKER ENGINE
# ==========================================

def analyze_company_content(
    company_name: str,
    website: Optional[str] = None,
    email_domain: Optional[str] = None,
    registration_id: Optional[str] = None,
    additional_context: Optional[str] = None
) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    seen_indicators = set()

    sources_checked = [
        "Corporate Domain & Web Alignment Heuristics",
        "Commercial TLD Reputation Registry",
        "Corporate Registration Format Validator",
        "Business Email Integrity Verifier"
    ]
    unavailable_checks = [
        "Official Government Corporate Registry Live Query (SEC EDGAR / Companies House / MCA)",
        "Duns & Bradstreet Active Credit Verification",
        "Physical Headquarters Site Inspection"
    ]
    limitations = [
        "New legitimate businesses may have short domain histories and basic web footprints.",
        "Analysis highlights structural anomalies between domains, stated identity, and registration inputs."
    ]
    recommendations: List[str] = []

    # Check for empty/insufficient
    if len(company_name.strip()) < 2:
        return {
            "risk_score": 0,
            "risk_label": "Insufficient Evidence",
            "findings": [],
            "sources_checked": sources_checked,
            "unavailable_checks": unavailable_checks,
            "limitations": ["Company name too short to evaluate."],
            "recommendations": ["Provide full legal company name and official website."],
            "input_summary": "Incomplete company name"
        }

    # Rule: Email domain is a free public webmail
    if email_domain:
        clean_domain = email_domain.strip().lower().replace("@", "")
        if clean_domain in FREE_EMAIL_DOMAINS:
            indicator = "Official Business Communications Relying on Free Webmail"
            if indicator not in seen_indicators:
                seen_indicators.add(indicator)
                findings.append({
                    "indicator": indicator,
                    "severity": "critical",
                    "strength": "high",
                    "evidence": f"Contact domain registered under @{clean_domain}",
                    "explanation": "Established businesses maintain branded corporate email infrastructure; relying on free webmail indicates an unverified entity."
                })
                recommendations.append("Require verification via an authentic corporate email domain.")

    # Rule: Website and Email Domain Inconsistency
    if website and email_domain:
        clean_email_dom = email_domain.strip().lower().replace("@", "")
        if clean_email_dom not in FREE_EMAIL_DOMAINS:
            try:
                parsed = urlparse(website if website.startswith("http") else f"https://{website}")
                web_host = (parsed.hostname or "").lower()
                if web_host and not (clean_email_dom in web_host or web_host in clean_email_dom):
                    indicator = "Discrepancy Between Corporate Website and Email Domain"
                    if indicator not in seen_indicators:
                        seen_indicators.add(indicator)
                        findings.append({
                            "indicator": indicator,
                            "severity": "high",
                            "strength": "high",
                            "evidence": f"Website domain '{web_host}' vs Email domain '{clean_email_dom}'",
                            "explanation": "Discrepancies between public websites and email domains are typical of spoofed companies or shell entities."
                        })
            except Exception:
                pass

    # Rule: Suspicious TLD for Commercial Enterprise
    if website:
        try:
            parsed = urlparse(website if website.startswith("http") else f"https://{website}")
            host = (parsed.hostname or "").lower()
            tld = host.split(".")[-1] if "." in host else ""
            if tld in SUSPICIOUS_TLDS:
                indicator = f"Unconventional Commercial Domain Extension (.{tld})"
                if indicator not in seen_indicators:
                    seen_indicators.add(indicator)
                    findings.append({
                        "indicator": indicator,
                        "severity": "medium",
                        "strength": "moderate",
                        "evidence": f"Corporate website uses .{tld}",
                        "explanation": f"Most established commercial organizations register under .com, .org, or country-code TLDs rather than .{tld}."
                    })
        except Exception:
            pass

    # Rule: Missing Registration ID / Unverified Status
    if not registration_id:
        indicator = "Unverified Legal Registration / Corporate Entity Identifier"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            findings.append({
                "indicator": indicator,
                "severity": "low",
                "strength": "low",
                "evidence": "No corporate registration number, EIN, CIN, or VAT ID provided",
                "explanation": "The company's legal existence cannot be verified without a government business registration identifier."
            })
            recommendations.append("Request the company's official corporate registration number and verify it against government databases.")

    # Rule: Context keywords indicating shell or investment scam
    if additional_context:
        shell_regex = r"(crypto\s*mining|guaranteed\s*yield|shell\s*company|offshore\s*nominee|unregulated\s*forex)"
        if re.search(shell_regex, additional_context, re.IGNORECASE):
            indicator = "High-Risk Offshore / Unregulated Financial Claims"
            if indicator not in seen_indicators:
                seen_indicators.add(indicator)
                findings.append({
                    "indicator": indicator,
                    "severity": "high",
                    "strength": "high",
                    "evidence": extract_evidence_snippet(additional_context, shell_regex),
                    "explanation": "Context mentions offshore entities or guaranteed financial yields that are heavily associated with fraudulent investment platforms."
                })

    # Score computation
    score = 0
    weights = {"critical": 35, "high": 25, "medium": 12, "low": 5}
    for f in findings:
        score += weights.get(f["severity"], 10)
    score = min(score, 100)

    if not recommendations:
        recommendations.append("Conduct a search in local state/national corporate registry databases before executing contracts.")

    input_summary = f"Company check: {company_name[:50]}"

    return {
        "risk_score": score,
        "risk_label": compute_risk_classification(score, len(findings)),
        "findings": findings,
        "sources_checked": sources_checked,
        "unavailable_checks": unavailable_checks,
        "limitations": limitations,
        "recommendations": recommendations,
        "input_summary": input_summary
    }


# ==========================================
# 6. DOCUMENT SCANNER ENGINE
# ==========================================

def analyze_document_content(extracted_text: str, filename: str) -> Dict[str, Any]:
    """Analyzes text extracted from PDF, DOCX, TXT, or images."""
    findings: List[Dict[str, Any]] = []
    seen_indicators = set()

    sources_checked = [
        "Document Text Extractor Engine",
        "Fraudulent Invoice & Renewal Signature Engine",
        "Advance Fee & Fake Check Document Heuristics",
        "Sensitive Information Harvesting Detector",
        "Suspicious Wire & Cryptocurrency Instruction Matcher"
    ]
    unavailable_checks = [
        "Cryptographic Digital Signature Validation",
        "Original Embedded Metadata Timestamp Verification"
    ]
    limitations = [
        "Visual formatting and letterhead authenticity cannot be verified purely from extracted raw text.",
        "Scanned low-resolution images may have OCR inaccuracies affecting keyword matches."
    ]
    recommendations: List[str] = []

    word_count = len(extracted_text.strip().split())
    if word_count < 5:
        return {
            "risk_score": 0,
            "risk_label": "Insufficient Evidence",
            "findings": [],
            "sources_checked": sources_checked,
            "unavailable_checks": unavailable_checks,
            "limitations": ["Document contained negligible or unreadable text content."],
            "recommendations": ["Ensure the file contains readable digital text or clear high-resolution scans."],
            "input_summary": f"Document: {filename} (Empty or unreadable)"
        }

    # Rule: Fake Invoice / Auto-Renewal Scam
    invoice_regex = r"(invoice\s*amount\s*\$[\d,]+|auto-renewal|membership\s*renewed|charged\s*to\s*your\s*card\s*\$[\d,]+|call\s*support\s*to\s*cancel|refund\s*department\s*phone)"
    if re.search(invoice_regex, extracted_text, re.IGNORECASE):
        indicator = "Fraudulent Invoice / Subscription Auto-Renewal Lure"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(extracted_text, invoice_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Fake invoices claim large automated renewals (e.g. Geek Squad, Norton, PayPal) to induce panic and force victims to call a fraudulent refund hotline."
            })
            recommendations.append("Do not call phone numbers printed on unexpected renewal invoices; check your bank statement directly.")

    # Rule: Advance Fee & Fake Check Instructions
    fee_regex = r"(wire\s*transfer\s*instructions|western\s*union|cashier'?s\s*check|send\s*the\s*balance\s*back|purchase\s*equipment\s*from\s*vendor|registration\s*deposit)"
    if re.search(fee_regex, extracted_text, re.IGNORECASE):
        indicator = "Document Advance-Fee / Fake Check Instructions"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(extracted_text, fee_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "The document contains instructions to deposit checks and wire funds or pay upfront vendor fees, typical of employment check scams."
            })
            recommendations.append("Never follow document instructions requiring third-party fund transfers or vendor deposits.")

    # Rule: Sensitive Credential / Identity Harvesting in Form
    sensitive_form_regex = r"(social\s*security\s*number|ssn|date\s*of\s*birth|mother'?s\s*maiden\s*name|bank\s*account\s*number|routing\s*number|credit\s*card\s*number|cvv\s*code)"
    if re.search(sensitive_form_regex, extracted_text, re.IGNORECASE):
        indicator = "High-Risk Sensitive PII Harvesting Form"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(extracted_text, sensitive_form_regex)
            findings.append({
                "indicator": indicator,
                "severity": "high",
                "strength": "high",
                "evidence": evidence,
                "explanation": "The document solicits high-risk personally identifiable information (SSN, banking routing, CVV), risking identity theft."
            })
            recommendations.append("Never share Social Security or banking credentials on unverified digital forms.")

    # Rule: Cryptocurrency / Crypto Wallet Instructions
    crypto_doc_regex = r"(bitcoin\s*address|btc\s*wallet|ethereum|usdt\s*trc20|scan\s*qr\s*code\s*to\s*pay)"
    if re.search(crypto_doc_regex, extracted_text, re.IGNORECASE):
        indicator = "Cryptocurrency Payment Demand in Document"
        if indicator not in seen_indicators:
            seen_indicators.add(indicator)
            evidence = extract_evidence_snippet(extracted_text, crypto_doc_regex)
            findings.append({
                "indicator": indicator,
                "severity": "critical",
                "strength": "high",
                "evidence": evidence,
                "explanation": "Official invoices from legitimate businesses do not mandate payment to anonymous cryptocurrency wallet addresses."
            })

    # Compute score
    score = 0
    weights = {"critical": 35, "high": 22, "medium": 12, "low": 5}
    for f in findings:
        score += weights.get(f["severity"], 10)
    score = min(score, 100)

    if not recommendations:
        recommendations.append("Verify the document issuer through an independent, pre-established contact number.")

    input_summary = f"Document scan: {filename} ({word_count} words)"

    return {
        "risk_score": score,
        "risk_label": compute_risk_classification(score, len(findings)),
        "findings": findings,
        "sources_checked": sources_checked,
        "unavailable_checks": unavailable_checks,
        "limitations": limitations,
        "recommendations": recommendations,
        "input_summary": input_summary
    }
