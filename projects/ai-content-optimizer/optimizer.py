"""
Optimization Suggestion Engine for AI Content Optimizer
Generates rule-based improvement suggestions, alternative headlines,
alternative CTAs, and before/after sentence rewrites.
"""

import re
import random
from analyzer import (
    _tokenize_sentences, _tokenize_words, _syllable_count,
    POWER_WORDS, POSITIVE_WORDS, PASSIVE_PATTERNS,
)


# ---------------------------------------------------------------------------
# Headline generation helpers
# ---------------------------------------------------------------------------

HEADLINE_POWER_PREFIXES = [
    "Discover How to", "The Ultimate Guide to", "Unlock the Secret to",
    "Transform Your", "{number} Proven Ways to", "How to Instantly",
    "The Surprising Truth About", "Why Smart Marketers",
    "Stop Wasting Time:", "Finally:",
]

HEADLINE_POWER_SUFFIXES = [
    "(Backed by Data)", "- Here's How", "That Actually Works",
    "[Step-by-Step]", "in {timeframe}", "Without the Hassle",
    "(Free Guide)", "- Results Guaranteed", "Today",
]


def generate_alternative_headlines(text: str, analysis: dict) -> list[dict]:
    """
    Generate 3 alternative headline suggestions based on the content.
    Each suggestion includes the headline and a rationale.
    """
    sentences = _tokenize_sentences(text)
    first_sentence = sentences[0] if sentences else text[:80]
    # Extract a core topic phrase (first noun-heavy chunk)
    core = _extract_core_topic(first_sentence)

    headlines = []

    # Strategy 1: Power-word prefix + core topic
    prefix = random.choice(HEADLINE_POWER_PREFIXES[:5])
    prefix = prefix.replace("{number}", str(random.choice([3, 5, 7, 10])))
    h1 = f"{prefix} {core}"
    if len(h1) > 70:
        h1 = h1[:67] + "..."
    headlines.append({
        "headline": h1,
        "strategy": "Power Word Opening",
        "rationale": "Leading with a power phrase grabs attention and promises value immediately.",
    })

    # Strategy 2: Number-driven / listicle
    num = random.choice([5, 7, 10])
    h2 = f"{num} {core} Strategies That Drive Real Results"
    if len(h2) > 70:
        h2 = h2[:67] + "..."
    headlines.append({
        "headline": h2,
        "strategy": "Number-Driven Headline",
        "rationale": "Numbered headlines increase click-through rates by setting clear expectations.",
    })

    # Strategy 3: Question / curiosity gap
    h3 = f"Are You Making These {core} Mistakes?"
    if len(h3) > 70:
        h3 = h3[:67] + "..."
    headlines.append({
        "headline": h3,
        "strategy": "Curiosity Gap Question",
        "rationale": "Questions trigger curiosity and personally engage the reader.",
    })

    return headlines


def _extract_core_topic(sentence: str) -> str:
    """Pull out a 2-4 word topic phrase from the sentence."""
    # Remove common leading words
    cleaned = re.sub(
        r"^(?:the|a|an|this|that|our|your|my|we|i|it|here|there)\s+",
        "", sentence.strip(), flags=re.IGNORECASE,
    )
    words = _tokenize_words(cleaned)
    # Take first 3-4 meaningful words
    meaningful = [w for w in words if len(w) > 2][:4]
    if meaningful:
        return " ".join(meaningful).title()
    return " ".join(words[:3]).title() if words else "Your Content"


# ---------------------------------------------------------------------------
# CTA generation
# ---------------------------------------------------------------------------

CTA_TEMPLATES = [
    {"cta": "Get Your Free {benefit} Now", "style": "Urgency + Value"},
    {"cta": "Start Your {benefit} Journey Today", "style": "Aspirational"},
    {"cta": "Claim Your Exclusive {benefit}", "style": "Exclusivity"},
    {"cta": "Yes! I Want to {action}", "style": "First-Person Agreement"},
    {"cta": "Unlock Instant Access", "style": "Instant Gratification"},
    {"cta": "Join {number}+ Happy Customers", "style": "Social Proof"},
    {"cta": "Try It Free for 30 Days", "style": "Risk Reversal"},
    {"cta": "See {benefit} in Action", "style": "Demo-Oriented"},
    {"cta": "Get Started in 60 Seconds", "style": "Low Friction"},
]


def generate_alternative_ctas(text: str, analysis: dict) -> list[dict]:
    """Generate 3 alternative CTA suggestions with rationales."""
    core = _extract_core_topic(_tokenize_sentences(text)[0] if text.strip() else "")
    benefit_word = core.split()[0] if core else "Results"

    templates = random.sample(CTA_TEMPLATES, min(3, len(CTA_TEMPLATES)))
    ctas = []
    for t in templates:
        cta_text = (t["cta"]
                    .replace("{benefit}", benefit_word)
                    .replace("{action}", f"Improve My {benefit_word}")
                    .replace("{number}", str(random.choice([1000, 5000, 10000]))))
        ctas.append({
            "cta": cta_text,
            "style": t["style"],
            "rationale": _cta_rationale(t["style"]),
        })
    return ctas


def _cta_rationale(style: str) -> str:
    rationales = {
        "Urgency + Value": "Combines time pressure with a clear value proposition to drive immediate action.",
        "Aspirational": "Frames the action as the start of a transformation, appealing to goals.",
        "Exclusivity": "Creates a sense of privilege that makes the offer feel special.",
        "First-Person Agreement": "Using 'I want' language increases psychological commitment.",
        "Instant Gratification": "Promises immediate results, reducing perceived effort.",
        "Social Proof": "Leveraging crowd behavior builds trust and reduces hesitation.",
        "Risk Reversal": "A free trial eliminates risk, lowering the barrier to conversion.",
        "Demo-Oriented": "Showing rather than telling builds confidence in the product.",
        "Low Friction": "Emphasising speed removes objections about time investment.",
    }
    return rationales.get(style, "Proven CTA pattern for higher conversions.")


# ---------------------------------------------------------------------------
# Sentence-level improvement suggestions (before/after)
# ---------------------------------------------------------------------------

def generate_sentence_improvements(text: str, analysis: dict) -> list[dict]:
    """
    Identify the weakest sentences and produce before/after rewrites.
    Returns up to 3 improvement pairs.
    """
    sentences = _tokenize_sentences(text)
    if not sentences:
        return []

    scored = []
    for s in sentences:
        score = _score_sentence(s)
        scored.append((score, s))
    scored.sort(key=lambda x: x[0])

    improvements = []
    for score, sentence in scored[:3]:
        improved = _improve_sentence(sentence)
        if improved != sentence:
            reason = _diagnose_sentence(sentence)
            improvements.append({
                "before": sentence,
                "after": improved,
                "reason": reason,
            })

    return improvements


def _score_sentence(sentence: str) -> float:
    """Score a sentence 0-100 (higher = better). Low scores = weak sentences."""
    words = _tokenize_words(sentence)
    n = max(len(words), 1)
    score = 50.0

    # Length penalty (too long or too short)
    if n > 25:
        score -= (n - 25) * 2
    elif n < 5:
        score -= (5 - n) * 3

    # Passive voice penalty
    for pat in PASSIVE_PATTERNS:
        if re.search(pat, sentence, re.IGNORECASE):
            score -= 15
            break

    # Power word bonus
    pw = sum(1 for w in words if w.lower() in POWER_WORDS)
    score += pw * 5

    # Positive word bonus
    pos = sum(1 for w in words if w.lower() in POSITIVE_WORDS)
    score += pos * 3

    # Starts with weak opener
    weak_openers = ["it is", "there is", "there are", "this is", "that is"]
    for opener in weak_openers:
        if sentence.lower().startswith(opener):
            score -= 10
            break

    return max(0, min(100, score))


def _improve_sentence(sentence: str) -> str:
    """Apply rule-based improvements to a weak sentence."""
    improved = sentence

    # 1. Remove passive voice (simple cases)
    # "X was created by Y" -> "Y created X"  (too complex for regex, skip)
    # Instead, flag and suggest active rewrites for simple patterns
    improved = re.sub(
        r"\bIt is (\w+) that\b",
        lambda m: m.group(1).capitalize() + ",",
        improved, flags=re.IGNORECASE,
    )

    # 2. Remove weak openers
    improved = re.sub(r"^There (?:is|are) ", "", improved, flags=re.IGNORECASE)
    improved = re.sub(r"^It is ", "", improved, flags=re.IGNORECASE)

    # 3. Add power words where missing
    words = _tokenize_words(improved)
    has_power = any(w.lower() in POWER_WORDS for w in words)
    if not has_power and len(words) > 3:
        # Prepend an appropriate intensifier
        intensifiers = ["Instantly", "Easily", "Quickly", "Effortlessly"]
        first_word = words[0] if words else ""
        # Only prepend if sentence starts with a verb-like word
        if first_word and first_word[0].islower():
            improved = random.choice(intensifiers) + " " + improved

    # 4. Ensure first letter is capitalised
    if improved and improved[0].islower():
        improved = improved[0].upper() + improved[1:]

    # 5. Trim excessive length
    imp_words = _tokenize_words(improved)
    if len(imp_words) > 25:
        # Try to split at a natural break
        mid = len(improved) // 2
        for i in range(mid - 10, mid + 10):
            if i < len(improved) and improved[i] in ",;:":
                improved = improved[:i+1].rstrip(",;:") + "."
                break

    return improved


def _diagnose_sentence(sentence: str) -> str:
    """Return the primary weakness of a sentence."""
    words = _tokenize_words(sentence)
    n = len(words)

    for pat in PASSIVE_PATTERNS:
        if re.search(pat, sentence, re.IGNORECASE):
            return "Passive voice weakens impact. Active voice is more direct and persuasive."

    if n > 25:
        return f"At {n} words, this sentence is too long. Break it up for better readability."

    weak_openers = ["it is", "there is", "there are", "this is"]
    for opener in weak_openers:
        if sentence.lower().startswith(opener):
            return "Weak opener delays the main point. Lead with the subject or action."

    pw = sum(1 for w in words if w.lower() in POWER_WORDS)
    if pw == 0:
        return "No power words detected. Adding emotional or action-oriented language increases engagement."

    return "This sentence could be more impactful with stronger, benefit-focused language."


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------

def generate_recommendations(analysis: dict) -> list[dict]:
    """
    Produce a prioritised list of improvement recommendations
    based on the weakest dimensions.
    """
    recs = []
    read = analysis["readability"]
    seo = analysis["seo"]
    conv = analysis["conversion"]

    # --- Readability recs ---
    if read["flesch_ease"] < 50:
        recs.append({
            "category": "Readability",
            "priority": "high",
            "icon": "fa-book-reader",
            "title": "Simplify your language",
            "detail": f"Flesch score is {read['flesch_ease']}. Use shorter words and sentences. "
                      f"Target a score of 60-70 for marketing copy.",
        })
    if read["passive_voice_pct"] > 15:
        recs.append({
            "category": "Readability",
            "priority": "high",
            "icon": "fa-pen-fancy",
            "title": "Reduce passive voice",
            "detail": f"{read['passive_voice_pct']}% of sentences use passive voice. "
                      f"Rewrite in active voice for stronger, more direct copy.",
        })
    if read["avg_sentence_length"] > 22:
        recs.append({
            "category": "Readability",
            "priority": "medium",
            "icon": "fa-cut",
            "title": "Shorten your sentences",
            "detail": f"Average sentence length is {read['avg_sentence_length']} words. "
                      f"Aim for 15-20 words per sentence.",
        })

    # --- SEO recs ---
    if seo["word_count_status"] == "too_short":
        recs.append({
            "category": "SEO",
            "priority": "high",
            "icon": "fa-expand-arrows-alt",
            "title": "Expand your content",
            "detail": seo["word_count_msg"],
        })
    if seo["keyword_status"] in ("missing", "low"):
        recs.append({
            "category": "SEO",
            "priority": "high" if seo["keyword_status"] == "missing" else "medium",
            "icon": "fa-key",
            "title": "Improve keyword usage",
            "detail": seo["keyword_msg"],
        })
    if seo["keyword_status"] == "high":
        recs.append({
            "category": "SEO",
            "priority": "medium",
            "icon": "fa-exclamation-triangle",
            "title": "Reduce keyword stuffing",
            "detail": seo["keyword_msg"],
        })
    if not seo["has_headings"]:
        recs.append({
            "category": "SEO",
            "priority": "medium",
            "icon": "fa-heading",
            "title": "Add subheadings",
            "detail": seo["heading_msg"],
        })

    # --- Conversion recs ---
    if conv["cta_count"] == 0:
        recs.append({
            "category": "Conversion",
            "priority": "high",
            "icon": "fa-bullhorn",
            "title": "Add a call-to-action",
            "detail": conv["cta_msg"],
        })
    if conv["power_word_density"] < 1.0:
        recs.append({
            "category": "Conversion",
            "priority": "medium",
            "icon": "fa-bolt",
            "title": "Use more power words",
            "detail": f"Power word density is {conv['power_word_density']}%. "
                      f"Aim for 2-3% to make copy more compelling.",
        })
    if conv["tone"] == "negative":
        recs.append({
            "category": "Conversion",
            "priority": "high",
            "icon": "fa-smile",
            "title": "Shift to a positive tone",
            "detail": conv["tone_msg"],
        })
    if conv["tone"] == "neutral":
        recs.append({
            "category": "Conversion",
            "priority": "medium",
            "icon": "fa-heart",
            "title": "Add emotional language",
            "detail": conv["tone_msg"],
        })
    if conv["benefit_ratio"] < 40:
        recs.append({
            "category": "Conversion",
            "priority": "high",
            "icon": "fa-gift",
            "title": "Focus on benefits over features",
            "detail": conv["benefit_msg"],
        })
    if conv["social_proof_count"] == 0:
        recs.append({
            "category": "Conversion",
            "priority": "medium",
            "icon": "fa-users",
            "title": "Add social proof",
            "detail": conv["social_proof_msg"],
        })

    # Add a positive note if the content is strong
    if not recs:
        recs.append({
            "category": "Overall",
            "priority": "low",
            "icon": "fa-trophy",
            "title": "Great work!",
            "detail": "Your content scores well across all dimensions. "
                      "Consider A/B testing variations to further optimise.",
        })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 1))

    return recs


# ---------------------------------------------------------------------------
# Master optimization function
# ---------------------------------------------------------------------------

def generate_optimizations(text: str, analysis: dict) -> dict:
    """Run all optimization generators and return a combined result."""
    return {
        "headlines": generate_alternative_headlines(text, analysis),
        "ctas": generate_alternative_ctas(text, analysis),
        "sentence_improvements": generate_sentence_improvements(text, analysis),
        "recommendations": generate_recommendations(analysis),
    }
