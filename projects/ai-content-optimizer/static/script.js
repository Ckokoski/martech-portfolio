/**
 * AI Content Optimizer - Client-side JavaScript
 * Handles word/character counting, form submission UX, and results animations.
 */

document.addEventListener('DOMContentLoaded', () => {

    // =========================================================================
    // Textarea live stats (index page)
    // =========================================================================

    const textarea = document.getElementById('contentInput');
    const charCount = document.getElementById('charCount');
    const wordCount = document.getElementById('wordCount');
    const sentenceCount = document.getElementById('sentenceCount');

    if (textarea && charCount) {
        const updateStats = () => {
            const text = textarea.value;
            const chars = text.length;
            const words = text.trim() === '' ? 0 :
                text.trim().split(/\s+/).length;
            const sentences = text.trim() === '' ? 0 :
                (text.match(/[.!?]+/g) || []).length || (words > 0 ? 1 : 0);

            charCount.textContent = `${chars.toLocaleString()} character${chars !== 1 ? 's' : ''}`;
            wordCount.textContent = `${words.toLocaleString()} word${words !== 1 ? 's' : ''}`;
            sentenceCount.textContent = `${sentences.toLocaleString()} sentence${sentences !== 1 ? 's' : ''}`;
        };

        textarea.addEventListener('input', updateStats);
        updateStats(); // initial state
    }


    // =========================================================================
    // Form submission loading state
    // =========================================================================

    const form = document.getElementById('analyzeForm');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (form && analyzeBtn) {
        form.addEventListener('submit', () => {
            analyzeBtn.classList.add('btn-loading');
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        });
    }


    // =========================================================================
    // Results page animations
    // =========================================================================

    // Animate the score counter
    const scoreNumber = document.querySelector('.score-number');
    if (scoreNumber) {
        const target = parseInt(scoreNumber.getAttribute('data-target'), 10);
        animateCounter(scoreNumber, 0, target, 1200);

        // Set gauge colour based on score
        const gaugeFill = document.querySelector('.gauge-fill');
        if (gaugeFill) {
            if (target >= 70) {
                gaugeFill.style.stroke = '#22c55e';
            } else if (target >= 40) {
                gaugeFill.style.stroke = '#eab308';
            } else {
                gaugeFill.style.stroke = '#ef4444';
            }
        }
    }

    // Fade-in dimension cards on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll(
        '.dimension-card, .recommendation-item, .alternative-card, .improvement-item'
    ).forEach((el) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
});


/**
 * Animate a number counter from `start` to `end` over `duration` ms.
 */
function animateCounter(element, start, end, duration) {
    const range = end - start;
    const startTime = performance.now();

    function step(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease-out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + range * eased);
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}
