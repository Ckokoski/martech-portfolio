import { Line } from 'react-chartjs-2';
import '../chartSetup';
import { defaultLineOptions } from '../chartSetup';
import { deliverabilityTrends, engagementTrends, sendTimeHeatmap } from '../data';

export default function EmailMetrics() {
  // --- Latest values for highlight cards ---
  const latestIdx = deliverabilityTrends.deliveryRate.length - 1;
  const deliveryRate = deliverabilityTrends.deliveryRate[latestIdx];
  const bounceRate = deliverabilityTrends.bounceRate[latestIdx];
  const spamRate = deliverabilityTrends.spamRate[latestIdx];
  const openRate = engagementTrends.openRate[latestIdx];
  const ctoRate = engagementTrends.clickToOpenRate[latestIdx];
  const unsubRate = engagementTrends.unsubscribeRate[latestIdx];

  // --- Deliverability chart ---
  const deliverabilityData = {
    labels: deliverabilityTrends.labels,
    datasets: [
      {
        label: 'Delivery Rate %',
        data: deliverabilityTrends.deliveryRate,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
      {
        label: 'Bounce Rate %',
        data: deliverabilityTrends.bounceRate,
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245,158,11,0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
    ],
  };

  const deliverabilityOpts = {
    ...defaultLineOptions,
    scales: {
      ...defaultLineOptions.scales,
      y: {
        ...defaultLineOptions.scales.y,
        min: 0,
        suggestedMax: 100,
        ticks: {
          ...defaultLineOptions.scales.y.ticks,
          callback: (v) => v + '%',
        },
      },
    },
  };

  // --- Engagement chart ---
  const engagementData = {
    labels: engagementTrends.labels,
    datasets: [
      {
        label: 'Open Rate %',
        data: engagementTrends.openRate,
        borderColor: '#4361ee',
        backgroundColor: 'rgba(67,97,238,0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
      {
        label: 'Click-to-Open Rate %',
        data: engagementTrends.clickToOpenRate,
        borderColor: '#3a86ff',
        backgroundColor: 'rgba(58,134,255,0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
      {
        label: 'Unsubscribe Rate %',
        data: engagementTrends.unsubscribeRate,
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239,68,68,0.06)',
        fill: true,
        tension: 0.35,
        pointRadius: 3,
        pointHoverRadius: 6,
      },
    ],
  };

  const engagementOpts = {
    ...defaultLineOptions,
    scales: {
      ...defaultLineOptions.scales,
      y: {
        ...defaultLineOptions.scales.y,
        ticks: {
          ...defaultLineOptions.scales.y.ticks,
          callback: (v) => v + '%',
        },
      },
    },
  };

  return (
    <>
      <div className="page-header">
        <h2>Email Metrics</h2>
        <p>Deliverability, engagement performance, and optimal send times</p>
      </div>

      {/* Highlight Cards */}
      <div className="metric-highlight-grid">
        <div className="metric-highlight">
          <div className="mh-value good">{deliveryRate}%</div>
          <div className="mh-label">Delivery Rate</div>
        </div>
        <div className="metric-highlight">
          <div className="mh-value warn">{bounceRate}%</div>
          <div className="mh-label">Bounce Rate</div>
        </div>
        <div className="metric-highlight">
          <div className="mh-value good">{spamRate}%</div>
          <div className="mh-label">Spam Complaint Rate</div>
        </div>
        <div className="metric-highlight">
          <div className="mh-value neutral">{openRate}%</div>
          <div className="mh-label">Open Rate</div>
        </div>
        <div className="metric-highlight">
          <div className="mh-value neutral">{ctoRate}%</div>
          <div className="mh-label">Click-to-Open Rate</div>
        </div>
        <div className="metric-highlight">
          <div className="mh-value good">{unsubRate}%</div>
          <div className="mh-label">Unsubscribe Rate</div>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="chart-card">
          <h3>Deliverability Trends</h3>
          <div className="chart-wrapper" style={{ height: 280 }}>
            <Line data={deliverabilityData} options={deliverabilityOpts} />
          </div>
        </div>
        <div className="chart-card">
          <h3>Engagement Trends</h3>
          <div className="chart-wrapper" style={{ height: 280 }}>
            <Line data={engagementData} options={engagementOpts} />
          </div>
        </div>
      </div>

      {/* Send Time Heatmap */}
      <div className="chart-card" style={{ marginTop: 0 }}>
        <h3>Best Send Times (Engagement Score by Hour &amp; Day)</h3>
        <div className="heatmap-container">
          <Heatmap />
        </div>
      </div>
    </>
  );
}

function Heatmap() {
  const { days, hours, data } = sendTimeHeatmap;

  const getColor = (val) => {
    // 0 = cool grey, 100 = vivid blue
    if (val >= 85) return '#1d3a8a';
    if (val >= 70) return '#2b52c9';
    if (val >= 55) return '#4361ee';
    if (val >= 40) return '#6c83f7';
    if (val >= 25) return '#93a8fb';
    if (val >= 15) return '#bcc8fd';
    return '#e0e5fd';
  };

  return (
    <table className="heatmap-table">
      <thead>
        <tr>
          <th></th>
          {days.map((d) => (
            <th key={d}>{d}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {hours.map((hour, hIdx) => (
          <tr key={hour}>
            <td className="hour-label">{hour}</td>
            {days.map((day, dIdx) => {
              const val = data[hIdx][dIdx];
              return (
                <td
                  key={day}
                  className="heatmap-cell"
                  style={{ backgroundColor: getColor(val) }}
                  title={`${day} ${hour}: ${val}`}
                >
                  {val}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
