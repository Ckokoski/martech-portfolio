"""
Content Analysis Engine for AI Content Optimizer
Provides readability, SEO, and conversion analysis using regex-based
text processing (no heavy NLP dependencies required).
"""

import re
import math
from collections import Counter


# ---------------------------------------------------------------------------
# Word lists used across analyses
# ---------------------------------------------------------------------------

POWER_WORDS = {
    # Urgency
    "now", "today", "hurry", "instant", "immediately", "fast", "quick",
    "limited", "deadline", "urgent", "rush", "final", "last chance",
    "don't miss", "expires", "act now", "before it's gone",
    # Exclusivity
    "exclusive", "premium", "vip", "members-only", "insider", "secret",
    "private", "elite", "invitation", "handpicked", "rare", "unique",
    # Value
    "free", "bonus", "save", "discount", "deal", "bargain", "guaranteed",
    "proven", "results", "best", "top", "ultimate", "essential",
    "revolutionary", "breakthrough", "transform", "unlock", "discover",
    # Trust
    "certified", "official", "trusted", "authentic", "verified", "secure",
    "risk-free", "money-back", "no obligation", "cancel anytime",
    # Emotion
    "amazing", "incredible", "stunning", "powerful", "remarkable",
    "extraordinary", "phenomenal", "spectacular", "unbelievable",
    "effortless", "simple", "easy",
}

POSITIVE_WORDS = {
    "good", "great", "best", "excellent", "amazing", "wonderful", "fantastic",
    "perfect", "love", "happy", "beautiful", "brilliant", "outstanding",
    "incredible", "awesome", "superb", "success", "successful", "win",
    "winning", "benefit", "improve", "growth", "profit", "gain", "boost",
    "enhance", "thrive", "enjoy", "delight", "remarkable", "impressive",
    "exciting", "innovative", "powerful", "effective", "efficient",
    "superior", "premium", "top", "leading", "trusted", "proven",
    "guaranteed", "free", "easy", "simple", "fast", "secure", "safe",
}

NEGATIVE_WORDS = {
    "bad", "worst", "terrible", "horrible", "awful", "poor", "fail",
    "failure", "loss", "lose", "losing", "problem", "issue", "risk",
    "danger", "warning", "mistake", "error", "wrong", "difficult",
    "hard", "complex", "complicated", "expensive", "costly", "slow",
    "weak", "boring", "painful", "frustrating", "annoying", "stress",
    "struggle", "suffer", "worry", "fear", "threat", "crisis",
}

CTA_PATTERNS = [
    r"\bget started\b", r"\bsign up\b", r"\bstart (?:your |a )?free",
    r"\btry (?:it )?(?:now|today|free)\b", r"\blearn more\b",
    r"\bdownload (?:now|today|free)\b", r"\bsubscribe\b",
    r"\bjoin (?:now|today|us|free)\b", r"\bbuy now\b", r"\bshop now\b",
    r"\border (?:now|today)\b", r"\bclaim\b", r"\bregister\b",
    r"\bbook (?:now|today|a |your )\b", r"\brequest\b",
    r"\bschedule\b", r"\bcontact us\b", r"\bcall (?:now|today|us)\b",
    r"\badd to cart\b", r"\bget (?:your |a )?(?:free|quote|demo|copy)\b",
    r"\bunlock\b", r"\bdiscover\b", r"\bexplore\b",
    r"\bclick here\b", r"\bact now\b", r"\bdon'?t (?:miss|wait)\b",
    r"\bgrab\b", r"\bseize\b",
]

BENEFIT_PATTERNS = [
    r"\byou(?:'ll| will) (?:get|receive|enjoy|experience|discover|achieve)\b",
    r"\bsave (?:time|money|hours)\b", r"\bincrease your\b",
    r"\bboost your\b", r"\bimprove your\b", r"\bgrow your\b",
    r"\breduce (?:your )?\b", r"\beliminate\b", r"\bno more\b",
    r"\bwithout (?:the )?(?:hassle|worry|stress)\b",
    r"\bimagine\b", r"\bpicture this\b",
    r"\bso (?:you|that you) can\b", r"\bwhich means\b",
    r"\bresulting in\b", r"\benabling you\b",
]

FEATURE_PATTERNS = [
    r"\bincludes?\b", r"\bfeatures?\b", r"\bbuilt[- ]in\b",
    r"\bequipped with\b", r"\bpowered by\b", r"\bintegrates? with\b",
    r"\bcompatible with\b", r"\bsupports?\b", r"\b\d+[- ]?(?:gb|mb|tb|ghz|mhz|mp|px|fps|rpm)\b",
    r"\bmade (?:of|from|with)\b", r"\bcomes with\b",
    r"\bspecifications?\b", r"\bdimensions?\b",
]

SOCIAL_PROOF_PATTERNS = [
    r"\b\d{1,3}(?:,\d{3})*\+?\s*(?:customers?|users?|people|clients?|subscribers?|members?)\b",
    r"\b(?:rated|rating)\s*\d", r"\bstars?\b",
    r"\btestimonials?\b", r"\breview(?:s|ed)?\b",
    r"\bas (?:seen|featured) (?:in|on)\b", r"\btrusted by\b",
    r"\bcase stud(?:y|ies)\b", r"\bsuccess stor(?:y|ies)\b",
    r"\baward[- ]winning\b", r"\b#1\b", r"\bbest[- ]selling\b",
    r"\bmost popular\b", r"\bover \d+\b",
    r"\bjoin \d+", r"\b\d+%\s*(?:of|increase|improvement|growth)\b",
]

PASSIVE_PATTERNS = [
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+\s+)*?(?:ed|en)\b",
    r"\b(?:has|have|had)\s+been\s+\w+ed\b",
    r"\bget(?:s|ting)?\s+\w+ed\b",
]


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _tokenize_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _tokenize_words(text: str) -> list[str]:
    """Extract words (letters/apostrophes only)."""
    return re.findall(r"[a-zA-Z']+", text)


def _syllable_count(word: str) -> int:
    """Estimate syllable count for a word using a simple heuristic."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    # Remove trailing silent-e
    word = re.sub(r"e$", "", word)
    vowel_groups = re.findall(r"[aeiouy]+", word)
    count = len(vowel_groups)
    return max(1, count)


# ---------------------------------------------------------------------------
# Readability Analysis
# ---------------------------------------------------------------------------

def analyze_readability(text: str) -> dict:
    """
    Compute readability metrics:
      - Flesch Reading Ease / Grade Level
      - Average sentence & word length
      - Passive voice percentage
      - Overall readability grade (A-F)
    """
    sentences = _tokenize_sentences(text)
    words = _tokenize_words(text)

    num_sentences = max(len(sentences), 1)
    num_words = max(len(words), 1)
    num_syllables = sum(_syllable_count(w) for w in words)

    avg_sentence_length = num_words / num_sentences
    avg_word_length = sum(len(w) for w in words) / num_words
    avg_syllables_per_word = num_syllables / num_words

    # Flesch Reading Ease
    flesch_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    flesch_ease = max(0, min(100, round(flesch_ease, 1)))

    # Flesch-Kincaid Grade Level
    grade_level = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
    grade_level = max(0, round(grade_level, 1))

    # Passive voice detection
    passive_count = 0
    for s in sentences:
        for pat in PASSIVE_PATTERNS:
            if re.search(pat, s, re.IGNORECASE):
                passive_count += 1
                break
    passive_pct = round(passive_count / num_sentences * 100, 1)

    # Grade assignment (optimised for marketing: target Flesch 60-70, grade 6-8)
    if flesch_ease >= 70 and passive_pct <= 10:
        grade = "A"
    elif flesch_ease >= 60 and passive_pct <= 15:
        grade = "B"
    elif flesch_ease >= 50 and passive_pct <= 20:
        grade = "C"
    elif flesch_ease >= 40:
        grade = "D"
    else:
        grade = "F"

    # Numeric score 0-100
    score = _readability_score(flesch_ease, passive_pct, avg_sentence_length)

    return {
        "score": score,
        "grade": grade,
        "flesch_ease": flesch_ease,
        "grade_level": grade_level,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_word_length": round(avg_word_length, 1),
        "passive_voice_pct": passive_pct,
        "num_sentences": num_sentences,
        "num_words": num_words,
        "passive_count": passive_count,
    }


def _readability_score(flesch: float, passive_pct: float, avg_sent_len: float) -> int:
    """Compute a 0-100 readability sub-score."""
    # Flesch component (target 60-70 for marketing)
    if 60 <= flesch <= 80:
        f_score = 100
    elif flesch > 80:
        f_score = max(60, 100 - (flesch - 80) * 1.5)
    else:
        f_score = max(0, flesch * 100 / 60)

    # Passive voice penalty
    p_score = max(0, 100 - passive_pct * 4)

    # Sentence length (target 15-20 words)
    if 12 <= avg_sent_len <= 22:
        s_score = 100
    elif avg_sent_len < 12:
        s_score = max(50, 100 - (12 - avg_sent_len) * 5)
    else:
        s_score = max(0, 100 - (avg_sent_len - 22) * 4)

    return round(f_score * 0.5 + p_score * 0.25 + s_score * 0.25)


# ---------------------------------------------------------------------------
# SEO Analysis
# ---------------------------------------------------------------------------

# Ideal word counts per content type
CONTENT_TYPE_RANGES = {
    "blog_post":     (800, 2500),
    "landing_page":  (300, 1000),
    "email":         (50, 300),
    "ad_copy":       (15, 150),
    "general":       (100, 2000),
}


def analyze_seo(text: str, content_type: str = "general",
                target_keyword: str = "") -> dict:
    """
    SEO-focused analysis:
      - Word count assessment vs content type
      - Keyword density
      - Heading structure hints
      - Meta description length check
    """
    words = _tokenize_words(text)
    num_words = len(words)
    word_lower = [w.lower() for w in words]

    # --- Word count assessment ---
    lo, hi = CONTENT_TYPE_RANGES.get(content_type, CONTENT_TYPE_RANGES["general"])
    if num_words < lo:
        word_count_status = "too_short"
        word_count_msg = f"Content is short for {content_type.replace('_', ' ')} ({num_words} words). Aim for {lo}-{hi} words."
    elif num_words > hi:
        word_count_status = "too_long"
        word_count_msg = f"Content is long for {content_type.replace('_', ' ')} ({num_words} words). Aim for {lo}-{hi} words."
    else:
        word_count_status = "good"
        word_count_msg = f"Word count ({num_words}) is appropriate for {content_type.replace('_', ' ')}."

    # --- Keyword density ---
    keyword_density = 0.0
    keyword_count = 0
    keyword_status = "no_keyword"
    keyword_msg = "No target keyword specified."
    if target_keyword:
        kw = target_keyword.lower().strip()
        kw_tokens = kw.split()
        if len(kw_tokens) == 1:
            keyword_count = word_lower.count(kw)
        else:
            keyword_count = text.lower().count(kw)
        keyword_density = round(keyword_count / max(num_words, 1) * 100, 2)
        if keyword_density == 0:
            keyword_status = "missing"
            keyword_msg = f'Target keyword "{target_keyword}" not found in content.'
        elif keyword_density < 0.5:
            keyword_status = "low"
            keyword_msg = f'Keyword density ({keyword_density}%) is low. Aim for 1-2%.'
        elif keyword_density <= 2.5:
            keyword_status = "good"
            keyword_msg = f'Keyword density ({keyword_density}%) is in the ideal range.'
        else:
            keyword_status = "high"
            keyword_msg = f'Keyword density ({keyword_density}%) is high \u2014 risk of keyword stuffing.'

    # --- Heading structure ---
    has_heading_markers = bool(re.search(r"(?m)^(?:#{1,6}\s|[A-Z][A-Z\s]{4,}$)", text))
    heading_msg = ("Heading structure detected." if has_heading_markers
                   else "No headings detected. Consider adding H2/H3 subheadings to improve scannability and SEO.")

    # --- Meta description ---
    first_sentence = _tokenize_sentences(text)[0] if text.strip() else ""
    first_sent_len = len(first_sentence)
    if first_sent_len <= 160:
        meta_status = "good"
        meta_msg = f"First sentence ({first_sent_len} chars) works as a meta description."
    else:
        meta_status = "long"
        meta_msg = f"First sentence is {first_sent_len} chars \u2014 trim to 155-160 for a meta description."

    # Composite score
    score = _seo_score(word_count_status, keyword_status, has_heading_markers, meta_status)

    return {
        "score": score,
        "word_count": num_words,
        "word_count_status": word_count_status,
        "word_count_msg": word_count_msg,
        "keyword_density": keyword_density,
        "keyword_count": keyword_count,
        "keyword_status": keyword_status,
        "keyword_msg": keyword_msg,
        "has_headings": has_heading_markers,
        "heading_msg": heading_msg,
        "meta_status": meta_status,
        "meta_msg": meta_msg,
    }


def _seo_score(wc_status, kw_status, has_headings, meta_status) -> int:
    s = 0
    # Word count (30 pts)
    s += {"good": 30, "too_short": 10, "too_long": 15}.get(wc_status, 15)
    # Keyword (30 pts)
    s += {"good": 30, "low": 15, "high": 10, "missing": 0, "no_keyword": 20}.get(kw_status, 10)
    # Headings (20 pts)
    s += 20 if has_headings else 5
    # Meta (20 pts)
    s += {"good": 20, "long": 10}.get(meta_status, 10)
    return min(100, s)


# ---------------------------------------------------------------------------
# Conversion Analysis
# ---------------------------------------------------------------------------

def analyze_conversion(text: str) -> dict:
    """
    Conversion-focused metrics:
      - CTA detection & strength
      - Power word density
      - Emotional tone
      - Benefit vs feature ratio
      - Social proof signals
    """
    text_lower = text.lower()
    words = _tokenize_words(text)
    num_words = max(len(words), 1)
    word_lower = [w.lower() for w in words]

    # --- CTAs ---
    ctas_found = []
    for pat in CTA_PATTERNS:
        for m in re.finditer(pat, text_lower):
            ctas_found.append(m.group())
    cta_count = len(ctas_found)
    ctas_unique = list(dict.fromkeys(ctas_found))[:10]

    if cta_count == 0:
        cta_strength = "none"
        cta_msg = "No call-to-action detected. Add a clear CTA to drive conversions."
    elif cta_count == 1:
        cta_strength = "weak"
        cta_msg = "One CTA found. Consider reinforcing with a secondary CTA."
    elif cta_count <= 3:
        cta_strength = "good"
        cta_msg = f"{cta_count} CTAs detected \u2014 good CTA presence."
    else:
        cta_strength = "strong"
        cta_msg = f"{cta_count} CTAs detected \u2014 strong call-to-action presence."

    # --- Power words ---
    pw_found = [w for w in word_lower if w in POWER_WORDS]
    pw_count = len(pw_found)
    pw_density = round(pw_count / num_words * 100, 2)
    pw_unique = list(dict.fromkeys(pw_found))[:15]

    # --- Emotional tone ---
    pos_count = sum(1 for w in word_lower if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in word_lower if w in NEGATIVE_WORDS)
    neutral_count = num_words - pos_count - neg_count
    if pos_count > neg_count * 2:
        tone = "positive"
    elif neg_count > pos_count * 2:
        tone = "negative"
    else:
        tone = "neutral"
    tone_msg = {
        "positive": "Content has a positive, encouraging tone \u2014 great for marketing.",
        "negative": "Content leans negative. Consider reframing around benefits and solutions.",
        "neutral": "Tone is neutral. Adding emotional language can boost engagement.",
    }[tone]

    # --- Benefits vs Features ---
    benefit_count = sum(1 for p in BENEFIT_PATTERNS if re.search(p, text_lower))
    feature_count = sum(1 for p in FEATURE_PATTERNS if re.search(p, text_lower))
    total_bf = benefit_count + feature_count or 1
    benefit_ratio = round(benefit_count / total_bf * 100, 1)
    if benefit_ratio >= 60:
        bf_msg = f"Benefit-focused ({benefit_ratio}% benefits) \u2014 excellent for conversions."
    elif benefit_ratio >= 40:
        bf_msg = f"Balanced benefits/features ({benefit_ratio}% benefits). Try emphasising benefits more."
    else:
        bf_msg = f"Feature-heavy ({benefit_ratio}% benefits). Rewrite features as customer benefits."

    # --- Social proof ---
    sp_found = []
    for pat in SOCIAL_PROOF_PATTERNS:
        for m in re.finditer(pat, text_lower):
            sp_found.append(m.group())
    sp_count = len(sp_found)
    sp_unique = list(dict.fromkeys(sp_found))[:10]
    if sp_count == 0:
        sp_msg = "No social proof detected. Add testimonials, stats, or trust signals."
    else:
        sp_msg = f"{sp_count} social proof signal(s) found."

    # Composite
    score = _conversion_score(cta_count, pw_density, tone, benefit_ratio, sp_count)

    return {
        "score": score,
        "cta_count": cta_count,
        "cta_strength": cta_strength,
        "cta_msg": cta_msg,
        "ctas_found": ctas_unique,
        "power_word_count": pw_count,
        "power_word_density": pw_density,
        "power_words_found": pw_unique,
        "tone": tone,
        "tone_msg": tone_msg,
        "positive_count": pos_count,
        "negative_count": neg_count,
        "neutral_count": neutral_count,
        "benefit_count": benefit_count,
        "feature_count": feature_count,
        "benefit_ratio": benefit_ratio,
        "benefit_msg": bf_msg,
        "social_proof_count": sp_count,
        "social_proof_msg": sp_msg,
        "social_proof_found": sp_unique,
    }


def _conversion_score(cta_count, pw_density, tone, benefit_ratio, sp_count) -> int:
    s = 0
    # CTAs (25 pts)
    s += min(25, cta_count * 10)
    # Power words (20 pts)
    if pw_density >= 3:
        s += 20
    elif pw_density >= 1.5:
        s += 15
    elif pw_density >= 0.5:
        s += 10
    else:
        s += 3
    # Tone (20 pts)
    s += {"positive": 20, "neutral": 10, "negative": 5}[tone]
    # Benefit ratio (20 pts)
    s += round(benefit_ratio * 0.2)
    # Social proof (15 pts)
    s += min(15, sp_count * 5)
    return min(100, s)


# ---------------------------------------------------------------------------
# Overall Score & Orchestration
# ---------------------------------------------------------------------------

def compute_overall_score(readability: dict, seo: dict, conversion: dict) -> int:
    """Weighted average of dimension scores (readability 30%, SEO 30%, conversion 40%)."""
    return round(
        readability["score"] * 0.30
        + seo["score"] * 0.30
        + conversion["score"] * 0.40
    )


def analyze_content(text: str, content_type: str = "general",
                    target_keyword: str = "") -> dict:
    """Run full analysis pipeline and return all results."""
    readability = analyze_readability(text)
    seo = analyze_seo(text, content_type, target_keyword)
    conversion = analyze_conversion(text)
    overall = compute_overall_score(readability, seo, conversion)

    return {
        "overall_score": overall,
        "readability": readability,
        "seo": seo,
        "conversion": conversion,
        "text": text,
        "content_type": content_type,
        "target_keyword": target_keyword,
    }
