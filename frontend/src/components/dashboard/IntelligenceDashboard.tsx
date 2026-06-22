// src/components/dashboard/IntelligenceDashboard.tsx
import React, { useState, useEffect } from 'react';
import { useIntelligence } from '@/hooks/useIntelligence';
import { useWebSocket } from '@/hooks/useWebSocket';
import { alertService } from '@/services/alertService';
import { decisionService } from '@/services/decisionService';
import { IntelligencePanel } from './IntelligencePanel';
import { AlertPanel } from './AlertPanel';
import { DecisionPanel } from './DecisionPanel';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Bell, AlertTriangle, TrendingUp, Users, FileText } from 'lucide-react';

interface IIntelligenceDashboardProps {
  caseId: string;
  userId: string;
}

export const IntelligenceDashboard: React.FC<IIntelligenceDashboardProps> = ({ 
  caseId, 
  userId 
}) => {
  const { data, loading, error, refresh, isStale } = useIntelligence(caseId);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [pendingDecisions, setPendingDecisions] = useState([]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // WebSocket connection for real-time updates
  const { isConnected, lastEvent } = useWebSocket(caseId);

  // Load alerts and decisions
  useEffect(() => {
    const loadAlertsAndDecisions = async () => {
      try {
        const [alerts, decisions] = await Promise.all([
          alertService.getActiveAlerts(caseId),
          decisionService.getDecisions(caseId),
        ]);
        setActiveAlerts(alerts);
        setPendingDecisions(decisions.filter(d => d.status === 'PENDING'));
      } catch (err) {
        console.error('Failed to load alerts/decisions:', err);
      }
    };
    
    loadAlertsAndDecisions();
  }, [caseId]);

  // Handle real-time updates
  useEffect(() => {
    if (lastEvent) {
      if (lastEvent.type === 'alert') {
        setActiveAlerts(prev => [lastEvent.data, ...prev]);
      } else if (lastEvent.type === 'decision_update') {
        // Refresh decisions
        decisionService.getDecisions(caseId).then(setPendingDecisions);
      }
      setLastUpdate(new Date());
    }
  }, [lastEvent, caseId]);

  if (loading) {
    return <LoadingSpinner text="Loading intelligence data..." />;
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 rounded-lg">
        <h3 className="text-red-800 font-semibold">Error Loading Intelligence</h3>
        <p className="text-red-600">{error.message}</p>
        <button 
          onClick={refresh}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-6 bg-yellow-50 rounded-lg">
        <p>No intelligence data available for this case.</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Intelligence Dashboard</h1>
            <p className="text-muted-foreground">
              Case: {caseId} • Last updated: {lastUpdate.toLocaleTimeString()}
              {isStale && (
                <Badge variant="outline" className="ml-2">
                  <span className="animate-pulse">●</span> Updating...
                </Badge>
              )}
              {isConnected ? (
                <Badge className="ml-2 bg-green-500">Live</Badge>
              ) : (
                <Badge className="ml-2 bg-red-500">Disconnected</Badge>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={refresh}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Intelligence Panel */}
        <IntelligencePanel intelligence={data} />

        {/* Tabs for Alerts and Decisions */}
        <Tabs defaultValue="alerts" className="w-full">
          <TabsList>
            <TabsTrigger value="alerts" className="flex items-center">
              <Bell className="mr-2 h-4 w-4" />
              Alerts
              {activeAlerts.length > 0 && (
                <Badge className="ml-2 bg-red-500">{activeAlerts.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="decisions" className="flex items-center">
              <FileText className="mr-2 h-4 w-4" />
              Decisions
              {pendingDecisions.length > 0 && (
                <Badge className="ml-2 bg-yellow-500">{pendingDecisions.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center">
              <TrendingUp className="mr-2 h-4 w-4" />
              Analysis
            </TabsTrigger>
          </TabsList>

          <TabsContent value="alerts">
            <AlertPanel 
              alerts={activeAlerts} 
              userId={userId}
              onAlertAction={(alert, action) => {
                action.handler(alert);
                // Refresh alerts after action
                alertService.getActiveAlerts(caseId).then(setActiveAlerts);
              }}
            />
          </TabsContent>

          <TabsContent value="decisions">
            <DecisionPanel 
              decisions={pendingDecisions}
              userId={userId}
              onDecisionUpdate={() => {
                decisionService.getDecisions(caseId).then(setPendingDecisions);
              }}
            />
          </TabsContent>

          <TabsContent value="analysis">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg">
                <h3 className="font-semibold mb-2">Key Actors</h3>
                <ul className="space-y-2">
                  {data.graph.keyActors.slice(0, 5).map(actor => (
                    <li key={actor.id} className="flex justify-between items-center">
                      <span>{actor.name}</span>
                      <Badge variant={actor.riskScore > 70 ? 'destructive' : 'default'}>
                        Risk: {actor.riskScore}%
                      </Badge>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-4 border rounded-lg">
                <h3 className="font-semibold mb-2">Risk Factors</h3>
                <ul className="space-y-2">
                  {data.risk.factors.slice(0, 5).map(factor => (
                    <li key={factor.id} className="flex justify-between items-center">
                      <span>{factor.description}</span>
                      <Badge variant={factor.score > 70 ? 'destructive' : 'default'}>
                        {factor.score}%
                      </Badge>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-4 border rounded-lg col-span-2">
                <h3 className="font-semibold mb-2">Recommendations</h3>
                <ul className="space-y-4">
                  {data.reasoning.recommendations.map(rec => (
                    <li key={rec.id} className="p-3 bg-gray-50 rounded">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium">{rec.title}</h4>
                          <p className="text-sm text-muted-foreground">{rec.description}</p>
                        </div>
                        <Badge variant={rec.priority === 'CRITICAL' ? 'destructive' : 'default'}>
                          {rec.priority}
                        </Badge>
                      </div>
                      <div className="mt-2 flex gap-4 text-sm">
                        <span>Confidence: {rec.confidence}%</span>
                        <span>Impact: {rec.impact}%</span>
                        <span>Effort: {rec.effort}%</span>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </ErrorBoundary>
  );
};