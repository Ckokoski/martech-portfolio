import { funnelData } from '../data';
import { fmtNum, fmtCurrency } from '../utils';

const STAGE_COLORS = ['#4361ee', '#3a86ff', '#6c83f7', '#10b981', '#f59e0b'];

export default function Funnel() {
  const { stages, overall, campaignFunnels } = funnelData;

  return (
    <>
      <div className="page-header">
        <h2>Funnel View</h2>
        <p>Visualize the journey from send to conversion and compare campaign funnels</p>
      </div>

      {/* Overall Funnel */}
      <div className="chart-card" style={{ marginBottom: 28 }}>
        <h3>Overall Marketing Funnel</h3>
        <div className="funnel-container">
          {stages.map((stage, idx) => {
            const val = overall.values[idx];
            const maxVal = overall.values[0];
            const pct = ((val / maxVal) * 100).toFixed(1);
            const widthPct = Math.max(30, (val / maxVal) * 100);

            return (
              <div key={stage}>
                <div
                  className="funnel-stage"
                  style={{
                    width: `${widthPct}%`,
                    backgroundColor: STAGE_COLORS[idx],
                    minWidth: 200,
                  }}
                >
                  <div>
                    <div className="stage-name">{stage}</div>
                    <div className="stage-value">{fmtNum(val)}</div>
                    <div className="stage-pct">{pct}% of sent</div>
                  </div>
                </div>
                {idx < stages.length - 1 && (
                  <DropOff from={overall.values[idx]} to={overall.values[idx + 1]} />
                )}
              </div>
            );
          })}
          <div
            className="funnel-stage"
            style={{
              width: '25%',
              minWidth: 200,
              backgroundColor: '#e76f51',
              marginTop: 4,
            }}
          >
            <div>
              <div className="stage-name">Revenue</div>
              <div className="stage-value">{fmtCurrency(overall.revenue)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Funnel Comparison */}
      <div className="chart-card">
        <h3>Campaign Funnel Comparison</h3>
        <div className="funnel-comparison">
          {campaignFunnels.map((cf) => (
            <div key={cf.id} className="funnel-comparison-col">
              <h4>{cf.name}</h4>
              {stages.map((stage, idx) => {
                const val = cf.values[idx];
                const maxVal = cf.values[0];
                const widthPct = Math.max(40, (val / maxVal) * 100);
                return (
                  <div key={stage}>
                    <div
                      className="mini-funnel-stage"
                      style={{
                        width: `${widthPct}%`,
                        backgroundColor: STAGE_COLORS[idx],
                      }}
                    >
                      {fmtNum(val)}
                    </div>
                    {idx < stages.length - 1 && (
                      <div className="mini-funnel-dropoff">
                        {'\u2193'}{' '}
                        {((1 - cf.values[idx + 1] / cf.values[idx]) * 100).toFixed(1)}% drop
                      </div>
                    )}
                  </div>
                );
              })}
              <div
                className="mini-funnel-stage"
                style={{ width: '40%', backgroundColor: '#e76f51', marginTop: 4 }}
              >
                {fmtCurrency(cf.revenue)}
              </div>
              <div style={{ marginTop: 8, fontSize: '0.75rem', color: '#6b7280' }}>
                Conv. Rate:{' '}
                <strong>
                  {((cf.values[4] / cf.values[0]) * 100).toFixed(2)}%
                </strong>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function DropOff({ from, to }) {
  const dropPct = ((1 - to / from) * 100).toFixed(1);
  return (
    <div className="funnel-dropoff">
      <span className="dropoff-arrow">{'\u25BC'}</span>
      {dropPct}% drop-off ({fmtNum(from - to)} lost)
    </div>
  );
}
