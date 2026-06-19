import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface ReportConfig {
  type: 'summary' | 'detailed' | 'forensic';
  format: 'pdf' | 'json' | 'csv';
  dateRange: { start: string; end: string };
  includeCharts: boolean;
}

const ReportGenerator: React.FC = () => {
  const [config, setConfig] = useState<ReportConfig>({
    type: 'summary',
    format: 'pdf',
    dateRange: { start: new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10), end: new Date().toISOString().slice(0, 10) },
    includeCharts: true
  });
  const [generating, setGenerating] = useState(false);
  const { token } = useAuthStore();

  const generateReport = async () => {
    setGenerating(true);
    try {
      const response = await fetch('http://localhost/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(config)
      });
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nemesis_report_${new Date().toISOString().slice(0, 19)}.${config.format}`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        alert('Report generation failed. Please try again.');
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
      alert('Error generating report');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-400 mb-1">Report Type</label>
        <div className="grid grid-cols-3 gap-2">
          {(['summary', 'detailed', 'forensic'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setConfig({ ...config, type })}
              className={`px-3 py-2 rounded-lg capitalize ${config.type === type ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-700 text-gray-400'}`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-400 mb-1">Format</label>
        <div className="grid grid-cols-3 gap-2">
          {(['pdf', 'json', 'csv'] as const).map((format) => (
            <button
              key={format}
              onClick={() => setConfig({ ...config, format })}
              className={`px-3 py-2 rounded-lg uppercase ${config.format === format ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-700 text-gray-400'}`}
            >
              {format}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1">Start Date</label>
          <input
            type="date"
            value={config.dateRange.start}
            onChange={(e) => setConfig({ ...config, dateRange: { ...config.dateRange, start: e.target.value } })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1">End Date</label>
          <input
            type="date"
            value={config.dateRange.end}
            onChange={(e) => setConfig({ ...config, dateRange: { ...config.dateRange, end: e.target.value } })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          />
        </div>
      </div>

      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={config.includeCharts}
          onChange={(e) => setConfig({ ...config, includeCharts: e.target.checked })}
          className="w-4 h-4 accent-green-500"
        />
        <span className="text-sm text-gray-400">Include charts and visualizations</span>
      </label>

      <button
        onClick={generateReport}
        disabled={generating}
        className="w-full py-3 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 disabled:opacity-50"
      >
        {generating ? 'Generating...' : 'Generate Report'}
      </button>
    </div>
  );
};

export default ReportGenerator;
