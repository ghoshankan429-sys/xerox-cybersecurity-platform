import { ThreatReport, ScanHistoryItem, StatsSummary } from "@/types";

export const SAMPLE_PHISHING_REPORT: ThreatReport = {
  scan_id: "scan_7f8a92bc10de",
  target_type: "URL",
  raw_target: "https://apple-id-verify.support-secure.live/auth",
  defanged_target: "hxxps://apple-id-verify[.]support-secure[.]live/auth",
  risk_score: 87,
  risk_level: "HIGH RISK",
  confidence_score: 94,
  layman_verdict: "Phishing suspected — Do not provide credentials",
  executive_summary:
    "This link is masquerading as Apple ID account verification. The domain was registered 3 days ago through an anonymous registrar, possesses no legitimate affiliation with Apple Inc., and routes directly to a credential harvesting form.",
  evidence_items: [
    {
      category: "IDENTITY",
      severity: "CRITICAL",
      title: "Brand Impersonation (Apple ID)",
      description: "Target domain combines trademarked brand name with deceptive security keywords.",
      technical_proof: "Keywords matched: 'apple-id', 'verify', 'support-secure'",
      why_this_matters: "Attackers commonly use legitimate brand names in third-party subdomains to deceive victims into entering credentials.",
    },
    {
      category: "INFRASTRUCTURE",
      severity: "HIGH",
      title: "Newly Registered Domain (Age < 7 days)",
      description: "WHOIS telemetry indicates domain creation 72 hours prior to scan timestamp.",
      technical_proof: "Created Date: 2026-09-09T14:22:00Z | Registrar: NameSilo LLC (Proxy Protected)",
      why_this_matters: "Over 85% of malicious phishing infrastructure is operational within the first 14 days of registration.",
    },
    {
      category: "CRYPTOGRAPHY",
      severity: "MEDIUM",
      title: "Free Automated SSL Certificate",
      description: "SSL issued by Let's Encrypt with no Organizational Validation (DV only).",
      technical_proof: "Issuer: Let's Encrypt Authority X3 | SAN: *.support-secure.live",
      why_this_matters: "Phishing kits routinely leverage free automated certificates to produce a deceptive padlock icon in browser address bars.",
    },
  ],
  recommended_actions: [
    {
      priority: "IMMEDIATE",
      action: "Do not enter any Apple credentials or personal data",
      rationale: "Any inputs submitted on this domain are captured directly by adversary command-and-control servers.",
      action_type: "DO_NOT_CLICK",
    },
    {
      priority: "PREVENTATIVE",
      action: "Reset your Apple ID password if previously entered",
      rationale: "Promptly invalidate session tokens and revoke unauthorized device access via appleid.apple.com.",
      action_type: "CHANGE_PASSWORD",
    },
    {
      priority: "REPORTING",
      action: "Submit abuse report to hosting provider and Apple Anti-Phishing",
      rationale: "Facilitates global domain takedown and browser blacklist flagging (Google Safe Browsing / Microsoft SmartScreen).",
      action_type: "REPORT_PHISHING",
    },
  ],
  technical_metadata: {
    domain: "support-secure.live",
    subdomain: "apple-id-verify",
    registered_domain: "support-secure.live",
    tld: "live",
    ip_addresses: ["198.51.100.42", "203.0.113.89"],
    dns: {
      a: ["198.51.100.42"],
      aaaa: [],
      mx: ["mail.support-secure.live"],
      ns: ["ns1.offshoredns.cc", "ns2.offshoredns.cc"],
      txt: ["v=spf1 ~all"],
    },
    ssl: {
      issuer: "Let's Encrypt",
      subject: "support-secure.live",
      valid_from: "2026-09-09",
      valid_until: "2026-12-08",
      is_valid: true,
      is_self_signed: false,
      days_remaining: 87,
    },
    redirect_hops: [
      {
        hop_number: 1,
        from_url: "https://apple-id-verify.support-secure.live/auth",
        to_url: "https://apple-id-verify.support-secure.live/auth/login.php?session=active",
        status_code: 302,
        ip_address: "198.51.100.42",
        response_time_ms: 140,
      },
    ],
    entropy: 4.82,
    detected_brands: ["Apple"],
    extracted_urls: ["https://apple-id-verify.support-secure.live/auth"],
    social_engineering_flags: ["Urgent Action Required", "Account Suspension Threat"],
  },
  analyzed_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
};

export const SAMPLE_SMISHING_REPORT: ThreatReport = {
  scan_id: "scan_3e5b61aa89fc",
  target_type: "MESSAGE",
  raw_target:
    "USPS Alert: Your package has an unpaid customs charge of $2.49. Delivery will be cancelled within 12 hours: https://usps-redelivery-support.xyz",
  defanged_target:
    "USPS Alert: Your package has an unpaid customs charge of $2.49. Delivery will be cancelled within 12 hours: hxxps://usps-redelivery-support[.]xyz",
  risk_score: 92,
  risk_level: "CRITICAL",
  confidence_score: 96,
  layman_verdict: "High-Risk Smishing / Package Customs Fee Fraud",
  executive_summary:
    "This SMS lure attempts to instill artificial urgency around a fraudulent $2.49 fee to extract credit card data. The United States Postal Service does not charge redelivery fees via unauthenticated short links.",
  evidence_items: [
    {
      category: "CONTENT",
      severity: "CRITICAL",
      title: "Urgency and Financial Extraction Pattern",
      description: "Message induces panic with an arbitrary 12-hour expiration window.",
      technical_proof: "Keywords: 'unpaid customs charge', 'delivery cancelled within 12 hours'",
      why_this_matters: "Classic social engineering lure designed to prevent rational verification before credit card entry.",
    },
    {
      category: "IDENTITY",
      severity: "CRITICAL",
      title: "Postal Brand Spoofing",
      description: "Impersonates United States Postal Service (USPS) on non-governmental domain.",
      technical_proof: "Actual registered domain: usps-redelivery-support.xyz (not usps.com)",
      why_this_matters: "Government services operate strictly on .gov or verified commercial domains like usps.com.",
    },
  ],
  recommended_actions: [
    {
      priority: "IMMEDIATE",
      action: "Do not visit the link or provide payment card numbers",
      rationale: "This infrastructure is an automated financial data siphon.",
      action_type: "DO_NOT_CLICK",
    },
    {
      priority: "REPORTING",
      action: "Forward message to 7726 (SPAM) on your mobile carrier",
      rationale: "Helps telecom carriers identify and block malicious SMS origins across the network.",
      action_type: "REPORT_PHISHING",
    },
  ],
  technical_metadata: {
    domain: "usps-redelivery-support.xyz",
    subdomain: "www",
    registered_domain: "usps-redelivery-support.xyz",
    tld: "xyz",
    ip_addresses: ["192.0.2.144"],
    redirect_hops: [],
    entropy: 4.65,
    detected_brands: ["USPS"],
    extracted_urls: ["https://usps-redelivery-support.xyz"],
    social_engineering_flags: ["Imminent deadline", "Low financial fee pretext", "Delivery disruption"],
  },
  analyzed_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
};

export const SAMPLE_BENIGN_REPORT: ThreatReport = {
  scan_id: "scan_1a2b3c4d5e6f",
  target_type: "URL",
  raw_target: "https://github.com",
  defanged_target: "https://github.com",
  risk_score: 5,
  risk_level: "BENIGN",
  confidence_score: 99,
  layman_verdict: "Verified Safe — Known Authentic Domain",
  executive_summary:
    "The target domain is a verified, established developer platform operated by GitHub, Inc. It holds an authentic High-Assurance Extended Validation SSL certificate and clean reputation across all global threat feeds.",
  evidence_items: [
    {
      category: "REPUTATION",
      severity: "INFO",
      title: "Clean Global Reputation",
      description: "Domain listed in top 100 global authority indexes with zero security incidents.",
      technical_proof: "Alexa Rank: #42 | Clean across 70+ threat telemetry providers",
      why_this_matters: "Domain possesses multi-year established provenance and cryptographic signing.",
    },
  ],
  recommended_actions: [
    {
      priority: "IMMEDIATE",
      action: "Safe to proceed",
      rationale: "Target exhibits authentic infrastructure and no deceptive heuristic indicators.",
      action_type: "SAFE_TO_PROCEED",
    },
  ],
  technical_metadata: {
    domain: "github.com",
    subdomain: "",
    registered_domain: "github.com",
    tld: "com",
    ip_addresses: ["140.82.121.4"],
    redirect_hops: [],
    entropy: 3.12,
    detected_brands: ["GitHub"],
    extracted_urls: ["https://github.com"],
    social_engineering_flags: [],
  },
  analyzed_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
};

export const MOCK_RECENT_SCANS: ScanHistoryItem[] = [
  {
    scan_id: "scan_7f8a92bc10de",
    target_type: "URL",
    defanged_target: "hxxps://apple-id-verify[.]support-secure[.]live/auth",
    risk_level: "HIGH RISK",
    risk_score: 87,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
    executive_summary: "Phishing suspected — Masquerades as Apple ID verification form.",
  },
  {
    scan_id: "scan_3e5b61aa89fc",
    target_type: "MESSAGE",
    defanged_target: "USPS Alert: Your package has an unpaid customs charge of $2.49...",
    risk_level: "CRITICAL",
    risk_score: 92,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
    executive_summary: "High-risk Smishing — Fake postal customs fee with urgent countdown.",
  },
  {
    scan_id: "scan_1a2b3c4d5e6f",
    target_type: "URL",
    defanged_target: "https://github.com",
    risk_level: "BENIGN",
    risk_score: 5,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    executive_summary: "Verified Safe — Known authentic developer portal.",
  },
  {
    scan_id: "scan_9c8d7e6f5a4b",
    target_type: "URL",
    defanged_target: "hxxp://secure-bank-login[.]online/portal",
    risk_level: "HIGH RISK",
    risk_score: 79,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 240).toISOString(),
    executive_summary: "Phishing suspected — Unencrypted banking login impersonation.",
  },
  {
    scan_id: "scan_4a3b2c1d0e9f",
    target_type: "MESSAGE",
    defanged_target: "Your Microsoft 365 license will expire in 2 hours: hxxps://m365-renewal[.]club",
    risk_level: "SUSPICIOUS",
    risk_score: 64,
    analyzed_at: new Date(Date.now() - 1000 * 60 * 360).toISOString(),
    executive_summary: "Suspicious credential lure with urgency signals.",
  },
];

export const MOCK_DASHBOARD_STATS: StatsSummary = {
  total_scans: 148,
  threats_blocked: 42,
  benign_verified: 91,
  suspicious_flagged: 15,
  scans_by_type: {
    URL: 104,
    MESSAGE: 44,
  },
};
