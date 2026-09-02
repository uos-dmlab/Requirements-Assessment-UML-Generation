"""
Requirement smell dictionaries based on:
- ISO/IEC/IEEE 29148:2018 quality characteristics
- Berry, Kamsties & Krieger (2003) vague terms
- Femmer et al. (2017) Smella framework
- QuARS tool (CNR-ISTI) ambiguity indicators
"""

# VAGUENESS: words without specific meaning
VAGUE_WORDS = {
    # Adjectives (ISO 29148: "avoid subjective language")
    "adequate", "appropriate", "efficient", "effective",
    "user-friendly", "flexible", "robust", "scalable",
    "easy", "simple", "complex", "good", "bad",
    "fast", "slow", "quick", "reasonable", "sufficient",
    "proper", "suitable", "optimal", "significant",
    "intuitive", "seamless", "smart", "powerful",
    "lightweight", "heavy", "modern", "advanced",
    "relevant", "important", "critical", "major", "minor",

    # Verbs (Berry et al.: "underspecified actions")
    "handle", "manage", "process", "support",
    "deal with", "take care of", "address",
    "improve", "enhance", "optimize", "facilitate",
    "ensure", "maintain", "provide", "perform",
}

# WEAK MODALS: optionality
WEAK_MODALS = {
    "may", "might", "could", "would",
    "should",   # "should" != "shall" (shall = mandatory)
    "can",      # "can" = ability, not requirement
    "ought to",
    "be able to",
    "capability to",
}

# LOOPHOLES: escape clauses
LOOPHOLE_PHRASES = [
    "if applicable", "if possible", "if necessary",
    "as appropriate", "as needed", "as required",
    "when possible", "when necessary", "when needed",
    "as deemed", "as determined", "where applicable",
    "typically", "normally", "usually", "generally",
    "in most cases", "under normal conditions",
    "to the extent possible", "as far as possible",
]

# INCOMPLETE MARKERS: explicit gaps
INCOMPLETE_MARKERS = [
    "tbd", "tbs", "tbr", "tbc",
    "to be defined", "to be specified", "to be resolved",
    "to be determined", "to be confirmed",
    "etc", "etc.", "and so on", "and so forth",
    "...", "among others", "and more",
    "not yet defined", "pending", "n/a",
]

# SUPERLATIVES & COMPARATIVES
SUPERLATIVES = {
    "best", "worst", "fastest", "slowest",
    "most", "least", "maximum", "minimum",
    "highest", "lowest", "greatest", "fewest",
}

COMPARATIVES = {
    "better", "worse", "faster", "slower",
    "more", "less", "higher", "lower",
    "greater", "fewer", "improved", "reduced",
}

# AMBIGUOUS PRONOUNS
AMBIGUOUS_PRONOUNS = {
    "it", "they", "them", "this", "that",
    "these", "those", "its", "their",
    "which", "the system",
}
