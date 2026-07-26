/**
 * Continuous Improvement Dashboard
 */
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface FeedbackStats {
  total: number;
  avg_overall: number;
  by_type: Record<string, { count: number; avg: number }>;
}

interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  drift_score: number;
  last_trained: string;
}

export const ContinuousImprovement: React.FC = () => {
  const [feedbackStats, setFeedbackStats] = useState<FeedbackStats | null>(null);
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [feedbackResponse, modelResponse] = await Promise.all([
        api.get('/feedback/stats'),
        api.get('/models/metrics')
      ]);
      setFeedbackStats(feedbackResponse.data);
      setModelMetrics(modelResponse.data);
    } catch (error) {
      console.error('Failed to fetch improvement data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="continuous-improvement">
      <h2>🔄 Continuous Improvement Dashboard</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>User Feedback</h3>
          <p className="metric-value">{feedbackStats?.avg_overall.toFixed(2)} / 5</p>
          <p className="metric-label">Average Rating</p>
          <p className="metric-sub">{feedbackStats?.total} total feedback</p>
        </div>

        <div className="metric-card">
          <h3>Model Accuracy</h3>
          <p className="metric-value">{(modelMetrics?.accuracy || 0) * 100}%</p>
          <p className="metric-label">Current Model</p>
          <p className="metric-sub">Last trained: {new Date(modelMetrics?.last_trained || '').toLocaleDateString()}</p>
        </div>

        <div className="metric-card">
          <h3>Model Drift</h3>
          <p className="metric-value">{(modelMetrics?.drift_score || 0) * 100}%</p>
          <p className="metric-label">Drift Score</p>
          <p className={`metric-sub ${(modelMetrics?.drift_score || 0) > 0.1 ? 'text-warning' : 'text-success'}`}>
            {(modelMetrics?.drift_score || 0) > 0.1 ? '⚠️ Retraining recommended' : '✅ Stable'}
          </p>
        </div>

        <div className="metric-card">
          <h3>F1 Score</h3>
          <p className="metric-value">{(modelMetrics?.f1_score || 0) * 100}%</p>
          <p className="metric-label">Model Performance</p>
        </div>
      </div>

      <div className="feedback-details">
        <h3>📊 Feedback by Type</h3>
        <ul>
          {feedbackStats?.by_type && Object.entries(feedbackStats.by_type).map(([type, data]) => (
            <li key={type}>
              <span className="feedback-type">{type}:</span>
              <span className="feedback-rating">{data.avg.toFixed(2)} / 5</span>
              <span className="feedback-count">({data.count} responses)</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};