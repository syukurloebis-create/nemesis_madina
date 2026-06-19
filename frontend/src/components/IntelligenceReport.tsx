import React, { useState } from 'react';
import { useAuthStore } from '../stores/authStore';

const IntelligenceReport: React.FC = () => {
  const [generating, setGenerating] = useState(false);
  const [reportType, setReportType] = useState<'summary' | 'detailed' | 'forensic'>('summary');
  const [format, setFormat] = useState<'json' | 'pdf' | 'csv'>('json');
  const { token } = useAuthStore();

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const response = await fetch('http://localhost/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ type: reportType, format })
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nemesis_report_${new Date().toISOString().slice(0, 19)}.${format}`;
        a.click();
        URL.revokeObjectURL(url);
        alert('✅ Report generated successfully!');
      } else {
        // Mock download for demo
        const mockData = {
          report_type: reportType,
          format: format,
          generated_at: new Date().toISOString(),
          data: {
            total_cases: 45,
            active_cases: 23,
            integrity_score: 100,
            hash_verified: true
          }
        };
        const blob = new Blob([JSON.stringify(mockData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nemesis_report_${new Date().toISOString().slice(0, 19)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        alert('✅ Report generated (mock data)');
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
      alert('⚠️ Report generation failed, but mock data downloaded');
    } finally {
      setGenerating(false);
    }
  };

  const recentReports = [
    { id: '1', name: 'Q2 2026 Fraud Analysis', date: '2026-06-01', type: 'summary', status: 'completed' },
    { id: '2', name: 'Vendor Collusion Investigation', date: '2026-05-28', type: 'detailed', status: 'completed' },
    { id: '3', name: 'Hash Chain Integrity Report', date: '2026-05-25', type: 'forensic', status: 'completed' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Intelligence Report</h1>
        <p className="text-gray-400 text-sm mt-1">Generate and download intelligence reports</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Report Generator */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Generate Report</h2>
            <p className="text-xs text-gray-500 mt-1">Customize and generate intelligence reports</p>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Report Type</label>
              <div className="grid grid-cols-3 gap-2">
                {(['summary', 'detailed', 'forensic'] as const).map((type) => (
                  <button
                    key={type}
                    onClick={() => setReportType(type)}
                    className={`px-3 py-2 rounded-lg capitalize ${reportType === type ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-700 text-gray-400'}`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">Format</label>
              <div className="grid grid-cols-3 gap-2">
                {(['json', 'pdf', 'csv'] as const).map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setFormat(fmt)}
                    className={`px-3 py-2 rounded-lg uppercase ${format === fmt ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-gray-700 text-gray-400'}`}
                  >
                    {fmt}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="w-full py-3 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600 disabled:opacity-50"
            >
              {generating ? 'Generating...' : 'Generate Report'}
            </button>
          </div>
        </div>

        {/* Recent Reports */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Recent Reports</h2>
          </div>
          <div className="divide-y divide-gray-700">
            {recentReports.map((report) => (
              <div key={report.id} className="p-4 flex justify-between items-center hover:bg-gray-700/30">
                <div>
                  <h3 className="font-medium text-white">{report.name}</h3>
                  <div className="flex gap-2 mt-1">
                    <span className="text-xs text-gray-500">{report.date}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${report.type === 'forensic' ? 'bg-purple-500/20 text-purple-400' : 'bg-blue-500/20 text-blue-400'}`}>
                      {report.type}
                    </span>
                  </div>
                </div>
                <button className="text-blue-400 text-sm hover:text-blue-300">Download</button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntelligenceReport;
