import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  DollarSign, 
  FileText,
  Package,
  Clock,
  Search,
  BarChart,
  FileSpreadsheet,
  Zap,
  Eye
} from 'lucide-react';
import { riskApi } from '../../services/api';
import { BaseModal } from '../modals/BaseModal';
import { CaseListModal } from '../modals/CaseListModal';

// --- Sub Components ---
const KPICard = React.memo(({
  label, value, change, icon: Icon, color = 'text-white', onClick
}: any) => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-3 cursor-pointer hover:border-primary-500/30 transition-all active:scale-95 select-none" onClick={onClick} role="button" tabIndex={0}>
    <div className="flex items-center justify-between mb-1">
      <span className="text-xs text-dark-muted">{label}</span>
      <Icon className={`w-4 h-4 ${color}`} />
    </div>
    <div className={`text-lg font-bold ${color}`}>{value}</div>
    <div className="text-[10px] text-dark-muted mt-0.5">{change}</div>
  </div>
));

const IntelligenceSummary = React.memo(({
  riskScore, activeCases, criticalAlerts, getRiskLevelText, getRiskLevelColor
}: any) => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-4">
    <h3 className="text-sm font-semibold text-white mb-3">📊 Ringkasan Intelijen</h3>
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs text-dark-muted">Skor Keseluruhan</span>
        <span className="text-lg font-bold text-primary-400">{Math.round(riskScore || 75)}%</span>
      </div>
      <div className="w-full bg-dark-bg rounded-full h-1.5">
        <div className="bg-primary-500 h-1.5 rounded-full" style={{ width: `${Math.min(riskScore || 75, 100)}%` }} />
      </div>
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="flex justify-between"><span className="text-dark-muted">Tingkat Risiko</span><span className={`font-bold ${getRiskLevelColor(riskScore)}`}>{getRiskLevelText(riskScore)}</span></div>
        <div className="flex justify-between"><span className="text-dark-muted">Keyakinan</span><span className="text-green-400 font-bold">80%</span></div>
        <div className="flex justify-between"><span className="text-dark-muted">Kasus Aktif</span><span className="text-white font-bold">{activeCases}</span></div>
        <div className="flex justify-between"><span className="text-dark-muted">Peringatan Kritis</span><span className={`font-bold ${criticalAlerts > 0 ? 'text-red-400' : 'text-green-400'}`}>{criticalAlerts}</span></div>
      </div>
    </div>
  </div>
));

const QuickActions = React.memo(({ onAction }: any) => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-4">
    <h3 className="text-sm font-semibold text-white mb-3">🎯 Tindakan Cepat</h3>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
      <ActionButton icon={<Search className="w-3.5 h-3.5" />} label="Selidiki Aktor" onClick={() => onAction('investigate_actors')} />
      <ActionButton icon={<BarChart className="w-3.5 h-3.5" />} label="Tinjau Risiko" onClick={() => onAction('review_risk')} />
      <ActionButton icon={<FileSpreadsheet className="w-3.5 h-3.5" />} label="Laporan" onClick={() => onAction('generate_report')} />
      <ActionButton icon={<Zap className="w-3.5 h-3.5" />} label="Analisis AI" onClick={() => onAction('run_ai_analysis')} />
      <ActionButton icon={<Eye className="w-3.5 h-3.5" />} label="Tren Risiko" onClick={() => onAction('view_trends')} className="sm:col-span-2" />
    </div>
  </div>
));

const QuickStatCard = React.memo(({ label, value, icon, color, onClick }: any) => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-3 flex items-center gap-3 cursor-pointer hover:border-primary-500/30 transition-all active:scale-95 select-none" onClick={onClick} role="button" tabIndex={0}>
    <div className={`p-1.5 rounded-lg ${color}`}>{icon}</div>
    <div><div className="text-[10px] text-dark-muted">{label}</div><div className="text-base font-bold text-white">{value}</div></div>
  </div>
));

const ActionButton = React.memo(({ icon, label, onClick, className = '' }: any) => (
  <button className={`w-full text-left px-3 py-1.5 rounded-lg bg-primary-500/5 text-primary-400 border border-primary-500/10 hover:bg-primary-500/10 transition-colors flex items-center gap-2 text-xs active:scale-95 select-none ${className}`} onClick={onClick} type="button">
    {icon}<span>{label}</span>
  </button>
));

// --- Detail Components ---
const ExposureDetail: React.FC<{ data: any }> = ({ data }) => {
  const exposure = data?.exposureValue || 0;
  const formatCurrency = (amount: number) => {
    if (amount === 0) return 'Rp 0';
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(amount);
  };
  return (
    <div className="space-y-4">
      <div className="bg-dark-bg rounded-lg p-4">
        <div className="text-sm text-dark-muted">Total Eksposur</div>
        <div className="text-3xl font-bold text-red-400">{formatCurrency(exposure)}</div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Perubahan</div><div className="text-lg font-bold text-red-400">↑ 18%</div></div>
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Periode</div><div className="text-lg font-bold text-white">Bulan Ini</div></div>
      </div>
      <div className="bg-dark-bg rounded-lg p-3">
        <div className="text-xs text-dark-muted">Detail</div>
        <p className="text-sm text-dark-muted mt-1">Eksposur risiko saat ini berasal dari kasus aktif dengan tingkat risiko tinggi.</p>
      </div>
    </div>
  );
};

const RecoveryDetail: React.FC<{ data: any }> = ({ data }) => {
  const recovery = data?.recoveryValue || 0;
  const formatCurrency = (amount: number) => {
    if (amount === 0) return 'Rp 0';
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(amount);
  };
  return (
    <div className="space-y-4">
      <div className="bg-dark-bg rounded-lg p-4">
        <div className="text-sm text-dark-muted">Total Pemulihan</div>
        <div className="text-3xl font-bold text-green-400">{formatCurrency(recovery)}</div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Perubahan</div><div className="text-lg font-bold text-green-400">↑ 12%</div></div>
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Periode</div><div className="text-lg font-bold text-white">Bulan Ini</div></div>
      </div>
      <div className="bg-dark-bg rounded-lg p-3">
        <div className="text-xs text-dark-muted">Detail</div>
        <p className="text-sm text-dark-muted mt-1">Pemulihan dari kasus yang telah diselesaikan.</p>
      </div>
    </div>
  );
};

const AIAnalysisDetail: React.FC<{ data: any }> = ({ data }) => {
  const score = data?.score || 0;
  const confidence = data?.confidence || 80;
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-dark-bg rounded-lg p-3 text-center"><div className="text-xs text-dark-muted">Skor Risiko</div><div className="text-2xl font-bold text-primary-400">{Math.round(score)}%</div></div>
        <div className="bg-dark-bg rounded-lg p-3 text-center"><div className="text-xs text-dark-muted">Keyakinan</div><div className="text-2xl font-bold text-green-400">{confidence}%</div></div>
        <div className="bg-dark-bg rounded-lg p-3 text-center"><div className="text-xs text-dark-muted">Tingkat</div><div className="text-2xl font-bold text-yellow-400">RENDAH</div></div>
      </div>
      <div className="bg-dark-bg rounded-lg p-4">
        <div className="text-sm text-dark-muted mb-2">Rekomendasi AI</div>
        <p className="text-white">Analisis AI menunjukkan risiko rendah dengan keyakinan tinggi. Tidak ada tindakan segera yang diperlukan.</p>
      </div>
      <div className="bg-dark-bg rounded-lg p-3">
        <div className="text-xs text-dark-muted">Faktor Risiko</div>
        <ul className="mt-2 space-y-1">
          <li className="text-sm text-dark-muted flex items-center gap-2"><span className="w-1.5 h-1.5 bg-yellow-400 rounded-full"></span>Vendor collusion pattern: LOW</li>
          <li className="text-sm text-dark-muted flex items-center gap-2"><span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>Transaction anomaly: NORMAL</li>
          <li className="text-sm text-dark-muted flex items-center gap-2"><span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>Fraud probability: 13%</li>
        </ul>
      </div>
    </div>
  );
};

const ReportDetail: React.FC<{ data: any }> = ({ data }) => {
  const summary = data?.summary || {};
  const generatedAt = data?.generatedAt || new Date();
  return (
    <div className="space-y-4">
      <div className="bg-dark-bg rounded-lg p-3 flex justify-between items-center">
        <div><div className="text-xs text-dark-muted">Tanggal Laporan</div><div className="text-white font-medium">{new Date(generatedAt).toLocaleString('id-ID')}</div></div>
        <button className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 text-sm">📥 Download PDF</button>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Total Kasus</div><div className="text-xl font-bold text-white">{summary.totalCases || 0}</div></div>
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Skor Risiko</div><div className="text-xl font-bold text-orange-400">{Math.round(summary.riskScore || 0)}%</div></div>
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Kasus Aktif</div><div className="text-xl font-bold text-yellow-400">{summary.activeCases || 0}</div></div>
        <div className="bg-dark-bg rounded-lg p-3"><div className="text-xs text-dark-muted">Peringatan Kritis</div><div className="text-xl font-bold text-red-400">{summary.criticalAlerts || 0}</div></div>
      </div>
      <div className="bg-dark-bg rounded-lg p-3">
        <div className="text-xs text-dark-muted">Ringkasan</div>
        <p className="text-sm text-dark-muted mt-1">Laporan ini mencakup {summary.totalCases || 0} kasus dengan skor risiko rata-rata {Math.round(summary.riskScore || 0)}%.</p>
      </div>
    </div>
  );
};

const TrendDetail: React.FC<{ data: any; loading?: boolean }> = ({ data, loading }) => {
  const trend = data?.trend || [];
  
  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-dark-border rounded"></div>
          ))}
        </div>
        <div className="h-40 bg-dark-border rounded"></div>
      </div>
    );
  }
  
  const trendData = trend.length > 0 ? trend : [
    { date: 'Jun 1', value: 12 }, { date: 'Jun 5', value: 15 }, { date: 'Jun 10', value: 10 },
    { date: 'Jun 15', value: 18 }, { date: 'Jun 20', value: 14 }, { date: 'Jun 23', value: 13 },
  ];
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-dark-bg rounded-lg p-3 text-center">
          <div className="text-xs text-dark-muted">Rata-rata</div>
          <div className="text-xl font-bold text-white">14.5%</div>
        </div>
        <div className="bg-dark-bg rounded-lg p-3 text-center">
          <div className="text-xs text-dark-muted">Tertinggi</div>
          <div className="text-xl font-bold text-red-400">18%</div>
        </div>
        <div className="bg-dark-bg rounded-lg p-3 text-center">
          <div className="text-xs text-dark-muted">Terendah</div>
          <div className="text-xl font-bold text-green-400">10%</div>
        </div>
      </div>
      <div className="bg-dark-bg rounded-lg p-4">
        <div className="text-sm text-dark-muted mb-3">Tren 30 Hari Terakhir</div>
        <div className="h-40 flex items-end justify-between gap-2">
          {trendData.map((item: any, i: number) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <div 
                className="w-full bg-primary-500 rounded-t transition-all hover:bg-primary-400"
                style={{ height: `${Math.min((item.value / 20) * 100, 95)}%` }}
              />
              <span className="text-[10px] text-dark-muted">{item.date}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="bg-dark-bg rounded-lg p-3">
        <div className="text-xs text-dark-muted">Analisis Tren</div>
        <p className="text-sm text-dark-muted mt-1">Tren risiko menunjukkan fluktuasi normal dengan kecenderungan stabil di bawah 20%.</p>
      </div>
    </div>
  );
};

// --- Main Component ---
interface OverviewTabProps {
  data: any;
  onAction?: (action: string, payload?: any) => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ data, onAction }) => {
  const isProcessingRef = useRef(false);
  const actionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [trendLoading, setTrendLoading] = useState(true);

  const [modalState, setModalState] = useState<{
    type: 'cases' | 'exposure' | 'recovery' | 'analysis' | 'report' | 'trend' | null;
    isOpen: boolean;
    data: any;
  }>({
    type: null,
    isOpen: false,
    data: null,
  });

  // Load trend data
  useEffect(() => {
    const loadTrendData = async () => {
      try {
        setTrendLoading(true);
        const response = await riskApi.getTrend();
        const data = response?.data ?? response ?? [];
        setTrendData(Array.isArray(data) ? data : []);
      } catch (error) {
        console.error('Failed to load trend data:', error);
        setTrendData([]);
      } finally {
        setTrendLoading(false);
      }
    };
    loadTrendData();
  }, []);

  const handleLocalAction = useCallback((action: string, payload?: any) => {
    if (actionTimeoutRef.current) {
      clearTimeout(actionTimeoutRef.current);
    }

    if (isProcessingRef.current) {
      return;
    }
    
    console.log(`[OverviewTab] 🎯 Action: ${action}`, payload);
    isProcessingRef.current = true;
    
    switch (action) {
      case 'view_cases':
        setModalState({
          type: 'cases',
          isOpen: true,
          data: Array.isArray(payload) ? payload : [],
        });
        break;
      case 'view_exposure':
        setModalState({
          type: 'exposure',
          isOpen: true,
          data: {
            exposureValue: data?.executive?.exposureValue || 0,
          },
        });
        break;
      case 'view_recovery':
        setModalState({
          type: 'recovery',
          isOpen: true,
          data: {
            recoveryValue: data?.executive?.recoveryValue || 0,
          },
        });
        break;
      case 'run_ai_analysis':
        setModalState({
          type: 'analysis',
          isOpen: true,
          data: {
            score: data?.executive?.riskScore || 0,
            confidence: 80,
            recommendation: 'Analisis AI menunjukkan risiko rendah dengan keyakinan tinggi.',
          },
        });
        break;
      case 'generate_report':
        setModalState({
          type: 'report',
          isOpen: true,
          data: {
            generatedAt: new Date(),
            summary: data?.executive || {},
          },
        });
        break;
      case 'view_trends':
        setModalState({
          type: 'trend',
          isOpen: true,
          data: {
            trend: trendData,
          },
        });
        break;
      default:
        if (onAction) {
          onAction(action, payload);
        }
    }
  onAction?.(action,payload);

    actionTimeoutRef.current = setTimeout(() => {
      isProcessingRef.current = false;
      actionTimeoutRef.current = null;
    }, 600);
  }, [data, onAction, trendData]);

  const closeModal = useCallback(() => {
    setModalState(prev => ({ ...prev, isOpen: false }));
    setTimeout(() => {
      setModalState(prev => ({ ...prev, type: null, data: null }));
    }, 300);
  }, []);

  // Data
  const executive = data?.executive || {};
  const alerts = data?.alerts || {};
  const vendors = data?.vendors || [];
  const casesData = data?.cases || [];

  const totalCases = executive.totalCases || 0;
  const riskScore = executive.riskScore || 0;
  const activeCases = executive.activeCases || 0;
  const criticalAlerts = executive.criticalAlerts || 0;
  const exposureValue = executive.exposureValue || 0;
  const recoveryValue = executive.recoveryValue || 0;
  const cases = Array.isArray(casesData) ? casesData : [];

  const formatCurrency = (amount: number) => {
    if (amount === 0) return 'Rp 0';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getRiskLevelText = (score: number) => {
    if (score >= 80) return 'KRITIS';
    if (score >= 60) return 'TINGGI';
    if (score >= 40) return 'SEDANG';
    return 'RENDAH';
  };

  const getRiskLevelColor = (score: number) => {
    if (score >= 80) return 'text-red-400';
    if (score >= 60) return 'text-orange-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-green-400';
  };

  if (!data) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center">
        <div className="animate-pulse">
          <div className="h-32 bg-dark-border rounded mb-4"></div>
          <div className="h-4 bg-dark-border rounded w-1/2 mx-auto"></div>
        </div>
        <p className="text-dark-muted mt-4">Memuat data dashboard...</p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {/* 5 KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          <KPICard
            label="Total Kasus"
            value={totalCases}
            change={`${activeCases} aktif`}
            icon={FileText}
            color="text-blue-400"
            onClick={() => handleLocalAction('view_cases', cases)}
          />
          <KPICard
            label="Skor Risiko"
            value={`${Math.round(riskScore)}%`}
            change={getRiskLevelText(riskScore)}
            icon={TrendingUp}
            color={getRiskLevelColor(riskScore)}
            onClick={() => handleLocalAction('review_risk')}
          />
          <KPICard
            label="Eksposur"
            value={formatCurrency(exposureValue)}
            change="↑ 18%"
            icon={DollarSign}
            color="text-red-400"
            onClick={() => handleLocalAction('view_exposure')}
          />
          <KPICard
            label="Pemulihan"
            value={formatCurrency(recoveryValue)}
            change="↑ 12%"
            icon={Shield}
            color="text-green-400"
            onClick={() => handleLocalAction('view_recovery')}
          />
          <KPICard
            label="Peringatan"
            value={`${criticalAlerts} aktif`}
            change={`${alerts.new || 0} baru`}
            icon={AlertTriangle}
            color={criticalAlerts > 0 ? 'text-yellow-400' : 'text-green-400'}
            onClick={() => handleLocalAction('view_alerts')}
          />
        </div>

        {/* 2 Kolom */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <IntelligenceSummary
            riskScore={riskScore}
            activeCases={activeCases}
            criticalAlerts={criticalAlerts}
            getRiskLevelText={getRiskLevelText}
            getRiskLevelColor={getRiskLevelColor}
          />
          <QuickActions onAction={handleAction} />
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <QuickStatCard
            label="Total Kasus"
            value={totalCases}
            icon={<FileText className="w-3.5 h-3.5" />}
            color="bg-blue-500/10 text-blue-400"
            onClick={() => handleLocalAction('view_cases', cases)}
          />
          <QuickStatCard
            label="Investigasi Aktif"
            value={activeCases}
            icon={<Clock className="w-3.5 h-3.5" />}
            color="bg-yellow-500/10 text-yellow-400"
            onClick={() => handleLocalAction('view_investigations')}
          />
          <QuickStatCard
            label="Vendor Mencurigakan"
            value={vendors.length || 0}
            icon={<Package className="w-3.5 h-3.5" />}
            color="bg-orange-500/10 text-orange-400"
            onClick={() => handleLocalAction('view_vendors')}
          />
          <QuickStatCard
            label="Peringatan Kritis"
            value={criticalAlerts}
            icon={<AlertTriangle className="w-3.5 h-3.5" />}
            color="bg-red-500/10 text-red-400"
            onClick={() => handleLocalAction('view_alerts')}
          />
        </div>
      </div>

      {/* Modals */}
      <CaseListModal
        isOpen={modalState.type === 'cases' && modalState.isOpen}
        onClose={closeModal}
        cases={modalState.data || []}
        title="📋 Daftar Kasus"
      />

      <BaseModal
        isOpen={modalState.type === 'exposure' && modalState.isOpen}
        onClose={closeModal}
        title="💰 Detail Eksposur"
      >
        <ExposureDetail data={modalState.data} />
      </BaseModal>

      <BaseModal
        isOpen={modalState.type === 'recovery' && modalState.isOpen}
        onClose={closeModal}
        title="📊 Detail Pemulihan"
      >
        <RecoveryDetail data={modalState.data} />
      </BaseModal>

      <BaseModal
        isOpen={modalState.type === 'analysis' && modalState.isOpen}
        onClose={closeModal}
        title="🧠 Analisis AI"
        size="xl"
      >
        <AIAnalysisDetail data={modalState.data} />
      </BaseModal>

      <BaseModal
        isOpen={modalState.type === 'report' && modalState.isOpen}
        onClose={closeModal}
        title="📋 Laporan"
        size="xl"
      >
        <ReportDetail data={modalState.data} />
      </BaseModal>

      <BaseModal
        isOpen={modalState.type === 'trend' && modalState.isOpen}
        onClose={closeModal}
        title="📈 Tren Risiko"
        size="xl"
      >
        <TrendDetail data={modalState.data} loading={trendLoading} />
      </BaseModal>
    </>
  );
};

export default OverviewTab;
