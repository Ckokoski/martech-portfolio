import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', icon: '\u{1F4CA}', label: 'Overview' },
  { to: '/campaigns', icon: '\u{1F4E8}', label: 'Campaigns' },
  { to: '/email-metrics', icon: '\u{1F4E7}', label: 'Email Metrics' },
  { to: '/funnel', icon: '\u{1F50D}', label: 'Funnel' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>CampaignView</h1>
        <p>Marketing Dashboard</p>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => (isActive ? 'active' : '')}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        Portfolio Project &middot; Synthetic Data
      </div>
    </aside>
  );
}
