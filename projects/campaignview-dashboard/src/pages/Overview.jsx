import { Line, Bar, Doughnut } from 'react-chartjs-2';
import '../chartSetup';
import { defaultLineOptions, defaultBarOptions, defaultDoughnutOptions } from '../chartSetup';
import {
  getKPISummary,
  getTopCampaignsByRevenue,
  monthlyTrends,
  engagementSegments,
} from '../data';
import { fmtNum, fmtCurrency, fmtPct } from '../utils';

export default function Overview() {
  const kpi = getKPISummary();
  const topCampaigns = getTopCampaignsByRevenue(5);

  // --- Chart data ---
  const trendData = {
    labels: monthlyTrends.labels,
    datasets: [
      {
        label: 'Opens',
        data: monthlyTrends.opens,
        borderColor: '#4361ee',
        backgroundColor: 'rgba(67, 97, 238, 0.08)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
      {
        label: 'Clicks',
        data: monthlyTrends.clicks,
        borderColor: '#3a86ff',
        backgroundColor: 'rgba(58, 134, 255, 0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
      {
        label: 'Conversions',
        data: monthlyTrends.conversions,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
    ],
  };

  const trendOptions = {
    ...defaultLineOptions,
    scales: {
      ...defaultLineOptions.scales,
      y: {
        ...defaultLineOptions.scales.y,
        ticks: {
          ...defaultLineOptions.scales.y.ticks,
          callback: (val) => (val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val),
        },
      },
    },
  };

  const revenueData = {
    labels: topCampaigns.map((c) => c.name.length > 22 ? c.name.slice(0, 22) + '...' : c.name),
    datasets: [
      {
        data: topCampaigns.map((c) => c.revenue),
        backgroundColor: ['#4361ee', '#3a86ff', '#6c83f7', '#93a8fb', '#bcc8fd'],
        borderRadius: 6,
        barThickness: 32,
      },
    ],
  };

  const revenueOptions = {
    ...defaultBarOptions,
    indexAxis: 'y',
    scales: {
      ...defaultBarOptions.scales,
      x: {
        ...defaultBarOptions.scales.x,
        ticks: {
          ...defaultBarOptions.scales.x.ticks,
          callback: (val) => '$' + (val / 1000).toFixed(0) + 'k',
        },
      },
      y: {
        ...defaultBarOptions.scales.y,
        grid: { display: false },
      },
    },
    plugins: {
      ...defaultBarOptions.plugins,
      tooltip: {
        ...defaultBarOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => ' $' + ctx.raw.toLocaleString(),
        },
      },
    },
  };

  const engagementData = {
    labels: engagementSegments.labels,
    datasets: [
      {
        data: engagementSegments.values,
        backgroundColor: engagementSegments.colors,
        borderWidth: 0,
        hoverOffset: 6,
      },
    ],
  };

  const engagementOptions = {
    ...defaultDoughnutOptions,
    plugins: {
      ...defaultDoughnutOptions.plugins,
      tooltip: {
        ...defaultDoughnutOptions.plugins.tooltip,
        callbacks: {
          label: (ctx) => ' ' + ctx.label + ': ' + ctx.raw + '%',
        },
      },
    },
  };

  return (
    <>
      <div className="page-header">
        <h2>Overview Dashboard</h2>
        <p>Campaign performance summary across all active programs</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon">{'\u{1F4E8}'}</div>
          <div className="kpi-label">Total Sent</div>
          <div className="kpi-value">{fmtNum(kpi.totalSent)}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon">{'\u{1F4EC}'}</div>
          <div className="kpi-label">Avg Open Rate</div>
          <div className="kpi-value">{fmtPct(kpi.avgOpenRate)}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon">{'\u{1F517}'}</div>
          <div className="kpi-label">Avg Click Rate</div>
          <div className="kpi-value">{fmtPct(kpi.avgClickRate)}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon">{'\u{1F4B0}'}</div>
          <div className="kpi-label">Total Revenue</div>
          <div className="kpi-value">{fmtCurrency(kpi.totalRevenue)}</div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon">{'\u{1F680}'}</div>
          <div className="kpi-label">Active Campaigns</div>
          <div className="kpi-value">{kpi.activeCampaigns}</div>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="chart-grid">
        <div className="chart-card" style={{ gridColumn: 'span 2' }}>
          <h3>Email Performance Trends (12 Months)</h3>
          <div className="chart-wrapper" style={{ height: 320 }}>
            <Line data={trendData} options={trendOptions} />
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>Top 5 Campaigns by Revenue</h3>
          <div className="chart-wrapper" style={{ height: 280 }}>
            <Bar data={revenueData} options={revenueOptions} />
          </div>
        </div>
        <div className="chart-card">
          <h3>Subscriber Engagement Breakdown</h3>
          <div className="chart-wrapper" style={{ height: 280 }}>
            <Doughnut data={engagementData} options={engagementOptions} />
          </div>
        </div>
      </div>
    </>
  );
}
