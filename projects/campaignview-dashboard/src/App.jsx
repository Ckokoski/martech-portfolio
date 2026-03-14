import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import Campaigns from './pages/Campaigns';
import EmailMetrics from './pages/EmailMetrics';
import Funnel from './pages/Funnel';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Overview />} />
          <Route path="campaigns" element={<Campaigns />} />
          <Route path="email-metrics" element={<EmailMetrics />} />
          <Route path="funnel" element={<Funnel />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
