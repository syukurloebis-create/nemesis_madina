// AICopilot.tsx - AI Assistant for Intelligence Analysis
import React, { useState } from 'react';
import { Send, Sparkles, Bot, Loader2, Zap, Shield, TrendingUp, Users } from 'lucide-react';

interface Message {
  id: number;
  type: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export const AICopilot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      type: 'ai',
      text: '👋 Selamat datang di NEMESIS AI Copilot. Saya siap membantu analisis risiko dan deteksi fraud. Apa yang ingin Anda ketahui?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Quick action buttons
  const quickActions = [
    { label: 'Risk Analysis', icon: Shield, prompt: 'Analisis risiko vendor dengan skor tertinggi' },
    { label: 'Fraud Detection', icon: Zap, prompt: 'Deteksi pola fraud pada data procurement' },
    { label: 'Network Insights', icon: Users, prompt: 'Analisis jaringan kolusi antar vendor' },
    { label: 'Trend Analysis', icon: TrendingUp, prompt: 'Analisis tren risiko procurement' },
  ];

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: 'user',
      text: input,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        '🔍 Berdasarkan analisis AI, vendor dengan risiko tertinggi adalah PT. Dexa Medica dengan skor 85. Faktor utama: hubungan kepemilikan yang tidak jelas dan pola harga abnormal.',
        '📊 Tren risiko menunjukkan peningkatan 15% pada procurement di sektor kesehatan. Rekomendasi: audit mendalam pada 3 vendor dengan skor tertinggi.',
        '🚨 Deteksi pola fraud: Teridentifikasi 2 kasus collusion dengan confidence 92%. Disarankan investigasi lebih lanjut pada hubungan PT. Bernofarm dan CV. Anugrah.',
        '💡 Insight: Jaringan kolusi menunjukkan 3 cluster utama. Cluster dengan risiko tertinggi melibatkan vendor farmasi dan pejabat pengadaan.'
      ];
      
      const aiMessage: Message = {
        id: messages.length + 2,
        type: 'ai',
        text: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleQuickAction = (prompt: string) => {
    setInput(prompt);
    // Auto-send after setting
    setTimeout(() => {
      handleSend();
    }, 100);
  };

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4 flex flex-col h-[400px]">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-semibold text-white">🤖 AI COPILOT</h3>
          <span className="text-xs text-green-400 animate-pulse">● ONLINE</span>
        </div>
        <span className="text-xs text-gray-500">Powered by NEMESIS AI</span>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            onClick={() => handleQuickAction(action.prompt)}
            className="flex items-center gap-1.5 px-2.5 py-1 bg-blue-500/10 hover:bg-blue-500/20 rounded-lg border border-blue-500/20 transition-colors text-xs text-gray-300"
          >
            <action.icon className="w-3 h-3 text-blue-400" />
            {action.label}
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                msg.type === 'user'
                  ? 'bg-blue-500/20 border border-blue-500/30 text-white'
                  : 'bg-gray-800/50 border border-gray-700 text-gray-300'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2">
              <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about risk, fraud, or network..."
          className="flex-1 bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500/50"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 rounded-lg transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default AICopilot;
