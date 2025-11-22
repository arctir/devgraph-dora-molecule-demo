/**
 * DORA Metrics RemotePlugin Component
 *
 * Self-hosted JS component for rendering DORA metrics in the devgraph UI.
 */

(function() {
  'use strict';

  const RATING_COLORS = {
    elite: '#22c55e',
    high: '#3b82f6',
    medium: '#f59e0b',
    low: '#ef4444',
  };

  const RATING_BG = {
    elite: '#dcfce7',
    high: '#dbeafe',
    medium: '#fef3c7',
    low: '#fee2e2',
  };

  function formatValue(value, unit) {
    if (unit === 'deployments_per_day') return `${value}/day`;
    if (unit === 'hours') return value < 1 ? `${Math.round(value * 60)}min` : `${value}h`;
    if (unit === 'percent') return `${value}%`;
    return String(value);
  }

  function createMetricCard(label, icon, data) {
    const rating = data.rating || 'medium';
    return `
      <div style="padding:12px;background:${RATING_BG[rating]};border-radius:6px;border-left:3px solid ${RATING_COLORS[rating]}">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
          <span style="font-size:16px">${icon}</span>
          <span style="font-size:12px;font-weight:500;color:#374151">${label}</span>
        </div>
        <div style="font-size:24px;font-weight:700;color:${RATING_COLORS[rating]};margin-bottom:4px">
          ${formatValue(data.value, data.unit)}
        </div>
        <span style="font-size:10px;font-weight:600;text-transform:uppercase;padding:2px 6px;border-radius:4px;background:${RATING_COLORS[rating]};color:white">
          ${rating}
        </span>
      </div>
    `;
  }

  function render(props) {
    const container = document.createElement('div');
    container.style.cssText = 'font-family:system-ui,sans-serif;padding:16px;background:#fff;border-radius:8px;border:1px solid #e5e7eb';

    const metrics = [
      ['deployment_frequency', 'Deployment Frequency', '🚀'],
      ['lead_time_for_changes', 'Lead Time', '⏱️'],
      ['mean_time_to_recovery', 'MTTR', '🔧'],
      ['change_failure_rate', 'Change Failure Rate', '⚠️'],
    ];

    const cards = metrics
      .filter(([key]) => props[key])
      .map(([key, label, icon]) => createMetricCard(label, icon, props[key]))
      .join('');

    container.innerHTML = `
      <h2 style="margin:0 0 16px;font-size:18px;font-weight:600;color:#111827">
        DORA Metrics: ${props.service || 'Service'}
      </h2>
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px">
        ${cards}
      </div>
    `;

    return container;
  }

  // Initialize for iframe communication
  window.addEventListener('message', function(e) {
    if (e.data?.type === 'RENDER_PROPS') {
      const root = document.getElementById('dora-root');
      if (root) {
        root.innerHTML = '';
        root.appendChild(render(e.data.props));
      }
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      const root = document.createElement('div');
      root.id = 'dora-root';
      document.body.appendChild(root);
      window.parent?.postMessage({ type: 'RENDERER_READY' }, '*');
    });
  }

  window.DoraMetricsComponent = render;
})();
