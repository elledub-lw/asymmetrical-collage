"""
Sources and queries for Market Watch newsletter.
Category definitions, priority sources, and discovery queries.
"""

# Category slugs and display names
CATEGORY_LABELS: dict[str, str] = {
    "bitcoin": "BITCOIN & BITCOIN STACK",
    "opensource": "OPEN SOURCE & SELF-HOSTING",
    "fintech": "FINTECH & PAYMENTS",
    "regulatory": "REGULATORY & COMPLIANCE",
    "privacy": "PRIVACY & DIGITAL RIGHTS",
    "ai-finance": "AI IN FINANCE & COMPLIANCE",
}

# All valid category slugs
VALID_CATEGORIES = list(CATEGORY_LABELS.keys())

# Bitcoin priority sources (highest priority - check first)
BITCOIN_PRIORITY_SOURCES = [
    "https://bitcoinops.org",
    "https://delvingbitcoin.org",
    "https://spiral.xyz/blog",
    "https://lightning.engineering/posts",
    "https://arkdev.info",
    "https://fedimint.org",
    "https://cashu.space",
    "https://lnp-bp.org",
    "https://stacker.news",
    "https://brink.dev",
]

# Bitcoin secondary sources
BITCOIN_SECONDARY_SOURCES = [
    "https://bitcoinmagazine.com",
    "https://theblock.co",
    "https://coindesk.com",  # Bitcoin section only - filter aggressively
]

# Bitcoin discovery queries for Perplexity
BITCOIN_QUERIES = [
    "Bitcoin Core release update site:bitcoinops.org OR site:delvingbitcoin.org",
    "Bitcoin protocol development BIP proposal site:delvingbitcoin.org",
    "Lightning Network update release site:lightning.engineering",
    "Ark protocol update site:arkdev.info",
    "Fedimint Cashu ecash update site:fedimint.org OR site:cashu.space",
    "RGB Taproot Assets Bitcoin L2 update site:lnp-bp.org OR site:lightning.engineering",
    "Bitcoin self-custody hardware wallet release site:spiral.xyz OR site:brink.dev",
    "Bitcoin developer funding grant announcement site:spiral.xyz OR site:brink.dev",
    "Bitcoin stablecoin Lightning payment rail announcement",
    "Bitcoin news site:bitcoinmagazine.com OR site:theblock.co",
    "new Bitcoin tool release announcement site:stacker.news",
]

# Placeholder queries for non-Bitcoin categories (v1)
# These will be expanded in future versions
PLACEHOLDER_QUERIES = {
    "opensource": [
        "open source self-hosting privacy software release announcement",
        "self-hosted infrastructure NAS home lab new release",
    ],
    "fintech": [
        "fintech payments startup funding product launch news",
        "Visa Mastercard Stripe embedded finance announcement",
    ],
    "regulatory": [
        "EU financial regulation AMF EBA ESMA FINMA announcement",
        "MiCA DORA ECB digital euro regulatory update",
        "FINMA BIS Swiss DLT Act announcement",
    ],
    "privacy": [
        "GDPR privacy surveillance data protection news Europe",
        "encryption policy privacy-enhancing technology release",
    ],
    "ai-finance": [
        "AI compliance risk management regulatory technology fintech",
        "AI fraud detection regulatory reporting automation",
    ],
}


def get_all_queries() -> list[tuple[str, str]]:
    """
    Get all discovery queries with their category.
    Returns list of (query, category) tuples.
    """
    queries = []

    # Bitcoin queries
    for query in BITCOIN_QUERIES:
        queries.append((query, "bitcoin"))

    # Placeholder queries for other categories
    for category, category_queries in PLACEHOLDER_QUERIES.items():
        for query in category_queries:
            queries.append((query, category))

    return queries


def get_priority_sources_text() -> str:
    """Format priority sources for inclusion in prompts."""
    sources = BITCOIN_PRIORITY_SOURCES + BITCOIN_SECONDARY_SOURCES
    return "\n".join(f"- {source}" for source in sources)
