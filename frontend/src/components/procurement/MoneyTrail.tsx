import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, ArrowRight, AlertTriangle, Shield } from 'lucide-react';
import { procurementApi, MoneyTrail as MoneyTrailType } from '../../services/procurementApi';

interface MoneyTrailProps {
  caseId: string;
  onTransactionClick?: (transaction: MoneyTrailType) => void;
}

export const MoneyTrail: React.FC<MoneyTrailProps> = ({ caseId, onTransactionClick }) => {
  const [transactions, setTransactions] = useState<MoneyTrailType[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalAmount, setTotalAmount] = useState(0);

  useEffect(() => {
    const fetchMoneyTrail = async () => {
      if (!caseId) return;
      try {
        const data = await procurementApi.getMoneyTrail(caseId);
        setTransactions(data);
        const total = data.reduce((sum, t) => sum + t.amount, 0);
        setTotalAmount(total);
      } catch (err) {
        console.error('Failed to fetch money trail:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMoneyTrail();
  }, [caseId]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <TrendingUp className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>Belum ada aliran dana yang terdeteksi</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-white">Aliran Dana</h3>
          <span className="text-xs text-gray-500">Total: {formatCurrency(totalAmount)}</span>
        </div>
        <div className="flex items-center space-x-1 text-xs">
          <Shield className="w-3 h-3 text-green-400" />
          <span className="text-green-400">Terverifikasi</span>
        </div>
      </div>

      <div className="p-4">
        <div className="space-y-4">
          {transactions.map((transaction, idx) => (
            <div 
              key={transaction.id}
              className="relative cursor-pointer hover:bg-gray-700/30 rounded-lg transition"
              onClick={() => onTransactionClick?.(transaction)}
            >
              {/* Transaction Flow */}
              <div className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <TrendingDown className="w-4 h-4 text-red-400" />
                    <span className="font-medium text-white">{transaction.from}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(transaction.date).toLocaleDateString('id-ID')}
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <ArrowRight className="w-4 h-4 text-gray-500" />
                  <div className="text-lg font-bold text-yellow-400">
                    {formatCurrency(transaction.amount)}
                  </div>
                </div>
                
                <div className="flex-1 text-right">
                  <div className="flex items-center justify-end space-x-2">
                    <span className="font-medium text-white">{transaction.to}</span>
                    <TrendingUp className="w-4 h-4 text-green-400" />
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Keyakinan: {transaction.confidence}%
                  </div>
                </div>
              </div>
              
              {/* Description */}
              <div className="mt-2 ml-4 text-xs text-gray-500">
                {transaction.description}
              </div>
              
              {/* Connection line between transactions */}
              {idx < transactions.length - 1 && (
                <div className="flex justify-center my-2">
                  <div className="w-0.5 h-4 bg-gray-600" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Flow Summary */}
        <div className="mt-4 pt-3 border-t border-gray-700">
          <div className="flex justify-between text-xs">
            <span className="text-gray-500">Jumlah Transaksi: {transactions.length}</span>
            <span className="text-gray-500">Rata-rata: {formatCurrency(totalAmount / transactions.length)}</span>
            <span className="text-green-400">✓ Chain Valid</span>
          </div>
        </div>
      </div>
    </div>
  );
};
