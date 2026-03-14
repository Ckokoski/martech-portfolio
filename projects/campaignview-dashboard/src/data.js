// ============================================================
// CampaignView - Sample Marketing Data
// All data is synthetic. No real company or customer data used.
// ============================================================

export const months = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

// --- Monthly Email Performance Trends (12 months) ---
export const monthlyTrends = {
  labels: months,
  opens: [18200, 19500, 21000, 22800, 21400, 23600, 25100, 24300, 26800, 27500, 29100, 30200],
  clicks: [4100, 4600, 5200, 5800, 5400, 6100, 6700, 6400, 7200, 7600, 8000, 8500],
  conversions: [820, 920, 1040, 1160, 1080, 1220, 1340, 1280, 1440, 1520, 1600, 1700],
};

// --- Campaigns ---
export const campaigns = [
  {
    id: 1,
    name: 'Spring Product Launch',
    status: 'completed',
    sendDate: '2025-03-15',
    sent: 45000,
    delivered: 44100,
    opens: 15435,
    clicks: 4410,
    conversions: 882,
    revenue: 52920,
    bounceRate: 2.0,
    unsubscribeRate: 0.3,
    spamRate: 0.02,
  },
  {
    id: 2,
    name: 'Q2 Nurture Series',
    status: 'completed',
    sendDate: '2025-04-01',
    sent: 32000,
    delivered: 31360,
    opens: 12544,
    clicks: 3762,
    conversions: 564,
    revenue: 33840,
    bounceRate: 2.0,
    unsubscribeRate: 0.4,
    spamRate: 0.01,
  },
  {
    id: 3,
    name: 'Summer Webinar Invite',
    status: 'completed',
    sendDate: '2025-06-10',
    sent: 28000,
    delivered: 27440,
    opens: 10976,
    clicks: 3293,
    conversions: 659,
    revenue: 26360,
    bounceRate: 2.0,
    unsubscribeRate: 0.2,
    spamRate: 0.01,
  },
  {
    id: 4,
    name: 'Customer Loyalty Reward',
    status: 'completed',
    sendDate: '2025-07-20',
    sent: 18000,
    delivered: 17820,
    opens: 8910,
    clicks: 3564,
    conversions: 1069,
    revenue: 74830,
    bounceRate: 1.0,
    unsubscribeRate: 0.1,
    spamRate: 0.01,
  },
  {
    id: 5,
    name: 'Fall Feature Announcement',
    status: 'completed',
    sendDate: '2025-09-05',
    sent: 52000,
    delivered: 50960,
    opens: 20384,
    clicks: 6115,
    conversions: 917,
    revenue: 45850,
    bounceRate: 2.0,
    unsubscribeRate: 0.3,
    spamRate: 0.02,
  },
  {
    id: 6,
    name: 'Black Friday Promo',
    status: 'completed',
    sendDate: '2025-11-25',
    sent: 65000,
    delivered: 63700,
    opens: 28665,
    clicks: 10192,
    conversions: 2548,
    revenue: 178360,
    bounceRate: 2.0,
    unsubscribeRate: 0.5,
    spamRate: 0.03,
  },
  {
    id: 7,
    name: 'Year-End Review',
    status: 'completed',
    sendDate: '2025-12-15',
    sent: 40000,
    delivered: 39200,
    opens: 17640,
    clicks: 4704,
    conversions: 706,
    revenue: 28240,
    bounceRate: 2.0,
    unsubscribeRate: 0.2,
    spamRate: 0.01,
  },
  {
    id: 8,
    name: 'New Year Re-Engagement',
    status: 'active',
    sendDate: '2026-01-10',
    sent: 35000,
    delivered: 34300,
    opens: 13720,
    clicks: 4116,
    conversions: 617,
    revenue: 30850,
    bounceRate: 2.0,
    unsubscribeRate: 0.3,
    spamRate: 0.01,
  },
  {
    id: 9,
    name: 'Q1 Product Update',
    status: 'active',
    sendDate: '2026-02-14',
    sent: 48000,
    delivered: 47040,
    opens: 18816,
    clicks: 5645,
    conversions: 847,
    revenue: 42350,
    bounceRate: 2.0,
    unsubscribeRate: 0.2,
    spamRate: 0.01,
  },
  {
    id: 10,
    name: 'Spring Webinar Series',
    status: 'active',
    sendDate: '2026-03-01',
    sent: 30000,
    delivered: 29400,
    opens: 11760,
    clicks: 3528,
    conversions: 529,
    revenue: 21160,
    bounceRate: 2.0,
    unsubscribeRate: 0.2,
    spamRate: 0.01,
  },
  {
    id: 11,
    name: 'Partner Co-Marketing Blast',
    status: 'draft',
    sendDate: '2026-04-01',
    sent: 0,
    delivered: 0,
    opens: 0,
    clicks: 0,
    conversions: 0,
    revenue: 0,
    bounceRate: 0,
    unsubscribeRate: 0,
    spamRate: 0,
  },
  {
    id: 12,
    name: 'Earth Day Sustainability',
    status: 'draft',
    sendDate: '2026-04-22',
    sent: 0,
    delivered: 0,
    opens: 0,
    clicks: 0,
    conversions: 0,
    revenue: 0,
    bounceRate: 0,
    unsubscribeRate: 0,
    spamRate: 0,
  },
];

// --- Subscriber Engagement Segments ---
export const engagementSegments = {
  labels: ['Highly Engaged', 'Active', 'At-Risk', 'Dormant'],
  values: [28, 35, 22, 15],
  colors: ['#4361ee', '#3a86ff', '#f4a261', '#e76f51'],
};

// --- Send Time Heatmap Data (hour x day-of-week) ---
// Values represent relative engagement score 0-100
const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const hours = [
  '6am', '7am', '8am', '9am', '10am', '11am', '12pm',
  '1pm', '2pm', '3pm', '4pm', '5pm', '6pm', '7pm', '8pm',
];

export const sendTimeHeatmap = {
  days,
  hours,
  // data[hourIndex][dayIndex]
  data: [
    [12, 14, 10, 15, 11,  5,  3], // 6am
    [25, 28, 22, 30, 24, 10,  6], // 7am
    [48, 55, 50, 58, 45, 18, 10], // 8am
    [72, 82, 78, 85, 70, 25, 15], // 9am
    [90, 95, 92, 98, 88, 30, 18], // 10am
    [78, 80, 82, 84, 75, 28, 16], // 11am
    [55, 58, 60, 62, 52, 22, 14], // 12pm
    [65, 70, 68, 72, 60, 20, 12], // 1pm
    [60, 65, 62, 68, 55, 18, 11], // 2pm
    [50, 55, 52, 58, 48, 15,  9], // 3pm
    [40, 42, 38, 45, 35, 12,  8], // 4pm
    [30, 32, 28, 35, 25, 10,  7], // 5pm
    [22, 24, 20, 26, 18,  8,  6], // 6pm
    [15, 18, 14, 20, 12,  7,  5], // 7pm
    [10, 12,  8, 14,  8,  5,  4], // 8pm
  ],
};

// --- Deliverability Metrics (12 months) ---
export const deliverabilityTrends = {
  labels: months,
  deliveryRate: [97.8, 97.9, 98.0, 98.1, 97.9, 98.2, 98.0, 98.3, 98.1, 98.4, 98.2, 98.5],
  bounceRate: [2.2, 2.1, 2.0, 1.9, 2.1, 1.8, 2.0, 1.7, 1.9, 1.6, 1.8, 1.5],
  spamRate: [0.03, 0.02, 0.02, 0.01, 0.02, 0.01, 0.02, 0.01, 0.01, 0.01, 0.02, 0.01],
};

// --- Engagement Metrics (12 months) ---
export const engagementTrends = {
  labels: months,
  openRate: [32.5, 33.1, 34.2, 35.8, 34.5, 36.2, 37.1, 36.5, 38.2, 39.0, 39.8, 40.5],
  clickToOpenRate: [22.5, 23.6, 24.8, 25.4, 25.2, 25.9, 26.7, 26.4, 26.9, 27.6, 27.5, 28.1],
  unsubscribeRate: [0.35, 0.32, 0.30, 0.28, 0.30, 0.25, 0.22, 0.24, 0.20, 0.18, 0.22, 0.19],
};

// --- Funnel Data ---
export const funnelData = {
  stages: ['Sent', 'Delivered', 'Opened', 'Clicked', 'Converted'],
  // Overall funnel
  overall: {
    values: [393000, 385140, 154056, 46217, 9234],
    revenue: 534760,
  },
  // Per-campaign funnels for comparison
  campaignFunnels: [
    {
      id: 6,
      name: 'Black Friday Promo',
      values: [65000, 63700, 28665, 10192, 2548],
      revenue: 178360,
    },
    {
      id: 4,
      name: 'Customer Loyalty Reward',
      values: [18000, 17820, 8910, 3564, 1069],
      revenue: 74830,
    },
    {
      id: 5,
      name: 'Fall Feature Announcement',
      values: [52000, 50960, 20384, 6115, 917],
      revenue: 45850,
    },
  ],
};

// --- KPI Summary (computed helpers) ---
export function getKPISummary() {
  const activeCampaigns = campaigns.filter(
    (c) => c.status === 'active' || c.status === 'completed'
  );
  const totalSent = activeCampaigns.reduce((sum, c) => sum + c.sent, 0);
  const totalOpens = activeCampaigns.reduce((sum, c) => sum + c.opens, 0);
  const totalClicks = activeCampaigns.reduce((sum, c) => sum + c.clicks, 0);
  const totalRevenue = activeCampaigns.reduce((sum, c) => sum + c.revenue, 0);
  const totalDelivered = activeCampaigns.reduce((sum, c) => sum + c.delivered, 0);

  return {
    totalSent,
    avgOpenRate: totalDelivered > 0 ? ((totalOpens / totalDelivered) * 100).toFixed(1) : 0,
    avgClickRate: totalDelivered > 0 ? ((totalClicks / totalDelivered) * 100).toFixed(1) : 0,
    totalRevenue,
    activeCampaigns: campaigns.filter((c) => c.status === 'active').length,
  };
}

// --- Top campaigns by revenue ---
export function getTopCampaignsByRevenue(count = 5) {
  return [...campaigns]
    .filter((c) => c.revenue > 0)
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, count);
}
