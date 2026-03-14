import { useState, useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import '../chartSetup';
import { defaultBarOptions } from '../chartSetup';
import { campaigns } from '../data';
import { fmtNum, fmtCurrency, fmtDate } from '../utils';

const STATUS_FILTERS = ['all', 'active', 'completed', 'draft'];

const SORTABLE_COLS = [
  { key: 'name', label: 'Campaign' },
  { key: 'sendDate', label: 'Send Date' },
  { key: 'sent', label: 'Sent' },
  { key: 'delivered', label: 'Delivered' },
  { key: 'opens', label: 'Opens' },
  { key: 'clicks', label: 'Clicks' },
  { key: 'conversions', label: 'Conv.' },
  { key: 'revenue', label: 'Revenue' },
];

export default function Campaigns() {
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortKey, setSortKey] = useState('sendDate');
  const [sortDir, setSortDir] = useState('desc');
  const [selectedId, setSelectedId] = useState(null);

  const filtered = useMemo(() => {
    let list = [...campaigns];
    if (statusFilter !== 'all') {
      list = list.filter((c) => c.status === statusFilter);
    }
    list.sort((a, b) => {
      let aVal = a[sortKey];
      let bVal = b[sortKey];
      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
    return list;
  }, [statusFilter, sortKey, sortDir]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const selected = selectedId != null ? campaigns.find((c) => c.id === selectedId) : null;

  return (
    <>
      <div className="page-header">
        <h2>Campaign Detail View</h2>
        <p>Drill into individual campaign performance and compare results</p>
      </div>

      <div className="table-card">
        <div className="table-header">
          <h3>All Campaigns ({filtered.length})</h3>
          <div className="table-filters">
            {STATUS_FILTERS.map((s) => (
              <button
                key={s}
                className={`filter-btn ${statusFilter === s ? 'active' : ''}`}
                onClick={() => setStatusFilter(s)}
              >
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: 40 }}>#</th>
                {SORTABLE_COLS.map((col) => (
                  <th key={col.key} onClick={() => handleSort(col.key)}>
                    {col.label}
                    <span
                      className={`sort-arrow ${sortKey === col.key ? 'active' : ''}`}
                    >
                      {sortKey === col.key ? (sortDir === 'asc' ? ' \u25B2' : ' \u25BC') : ' \u25BC'}
                    </span>
                  </th>
                ))}
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c, i) => (
                <tr key={c.id} onClick={() => setSelectedId(c.id)}>
                  <td style={{ color: '#9ca3af' }}>{i + 1}</td>
                  <td style={{ fontWeight: 600 }}>{c.name}</td>
                  <td>{fmtDate(c.sendDate)}</td>
                  <td>{fmtNum(c.sent)}</td>
                  <td>{fmtNum(c.delivered)}</td>
                  <td>{fmtNum(c.opens)}</td>
                  <td>{fmtNum(c.clicks)}</td>
                  <td>{fmtNum(c.conversions)}</td>
                  <td style={{ fontWeight: 600 }}>{fmtCurrency(c.revenue)}</td>
                  <td>
                    <span className={`status-badge ${c.status}`}>
                      {c.status === 'active' && '\u25CF '}
                      {c.status.charAt(0).toUpperCase() + c.status.slice(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selected && <CampaignDetail campaign={selected} onClose={() => setSelectedId(null)} />}
    </>
  );
}

function CampaignDetail({ campaign, onClose }) {
  const c = campaign;
  const openRate = c.delivered > 0 ? ((c.opens / c.delivered) * 100).toFixed(1) : 0;
  const clickRate = c.delivered > 0 ? ((c.clicks / c.delivered) * 100).toFixed(1) : 0;
  const convRate = c.clicks > 0 ? ((c.conversions / c.clicks) * 100).toFixed(1) : 0;
  const cto = c.opens > 0 ? ((c.clicks / c.opens) * 100).toFixed(1) : 0;

  const miniBarData = {
    labels: ['Sent', 'Delivered', 'Opened', 'Clicked', 'Converted'],
    datasets: [
      {
        data: [c.sent, c.delivered, c.opens, c.clicks, c.conversions],
        backgroundColor: ['#4361ee', '#3a86ff', '#6c83f7', '#10b981', '#f59e0b'],
        borderRadius: 4,
      },
    ],
  };

  const miniBarOpts = {
    ...defaultBarOptions,
    scales: {
      ...defaultBarOptions.scales,
      y: {
        ...defaultBarOptions.scales.y,
        ticks: {
          ...defaultBarOptions.scales.y.ticks,
          callback: (val) => (val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val),
        },
      },
    },
  };

  return (
    <div className="detail-overlay" onClick={onClose}>
      <div className="detail-card" onClick={(e) => e.stopPropagation()}>
        <div className="detail-card-header">
          <div>
            <h3>{c.name}</h3>
            <span
              className={`status-badge ${c.status}`}
              style={{ marginTop: 6, display: 'inline-flex' }}
            >
              {c.status.charAt(0).toUpperCase() + c.status.slice(1)}
            </span>
          </div>
          <button className="detail-close-btn" onClick={onClose}>
            {'\u2715'}
          </button>
        </div>

        <div className="detail-card-body">
          <div className="detail-metrics-grid">
            <div className="detail-metric">
              <div className="metric-val">{fmtNum(c.sent)}</div>
              <div className="metric-label">Sent</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{fmtNum(c.delivered)}</div>
              <div className="metric-label">Delivered</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{openRate}%</div>
              <div className="metric-label">Open Rate</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{clickRate}%</div>
              <div className="metric-label">Click Rate</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{cto}%</div>
              <div className="metric-label">Click-to-Open</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{convRate}%</div>
              <div className="metric-label">Conv. Rate</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{fmtCurrency(c.revenue)}</div>
              <div className="metric-label">Revenue</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{fmtDate(c.sendDate)}</div>
              <div className="metric-label">Send Date</div>
            </div>
          </div>

          <h3 style={{ marginBottom: 12 }}>Campaign Funnel</h3>
          <div style={{ height: 220 }}>
            <Bar data={miniBarData} options={miniBarOpts} />
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr 1fr',
              gap: 12,
              marginTop: 20,
            }}
          >
            <div className="detail-metric">
              <div className="metric-val">{c.bounceRate}%</div>
              <div className="metric-label">Bounce Rate</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{c.unsubscribeRate}%</div>
              <div className="metric-label">Unsub Rate</div>
            </div>
            <div className="detail-metric">
              <div className="metric-val">{c.spamRate}%</div>
              <div className="metric-label">Spam Rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
