/**
 * Format a number with commas: 12345 => "12,345"
 */
export function fmtNum(n) {
  if (n == null) return '0';
  return Number(n).toLocaleString('en-US');
}

/**
 * Format currency: 52920 => "$52,920"
 */
export function fmtCurrency(n) {
  if (n == null) return '$0';
  return '$' + Number(n).toLocaleString('en-US');
}

/**
 * Format percentage: 35.8 => "35.8%"
 */
export function fmtPct(n) {
  if (n == null) return '0%';
  return n + '%';
}

/**
 * Format date string: "2025-03-15" => "Mar 15, 2025"
 */
export function fmtDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
