import { api } from './api';
import { EventEmitter } from 'events';

export class AlertService extends EventEmitter {
  private alerts: Map<string, any[]> = new Map();

  async getAlerts(caseId: string): Promise<any[]> {
    try {
      const response = await api.get('/api/v1/alerts', {
        params: { case_id: caseId },
      });
      const alerts = response.data || [];
      this.alerts.set(caseId, alerts);
      return alerts;
    } catch (error) {
      console.error('[AlertService] Error:', error);
      return [];
    }
  }

  async getActiveAlerts(caseId: string): Promise<any[]> {
    const all = await this.getAlerts(caseId);
    return all.filter((a: any) => a.status === 'NEW' || a.status === 'ACKNOWLEDGED');
  }

  async acknowledgeAlert(id: string, userId: string): Promise<void> {
    await api.post(`/api/v1/alerts/${id}/acknowledge`, { user_id: userId });
    this.emit('alert-acknowledged', { id, userId });
  }

  async resolveAlert(id: string, resolution: string, userId: string): Promise<void> {
    await api.post(`/api/v1/alerts/${id}/resolve`, { resolution, user_id: userId });
    this.emit('alert-resolved', { id, userId });
  }

  async escalateAlert(id: string, reason: string, userId: string): Promise<void> {
    await api.post(`/api/v1/alerts/${id}/escalate`, { reason, user_id: userId });
    this.emit('alert-escalated', { id, userId });
  }

  getActionsForAlert(alert: any): any[] {
    const actions = [];

    if (alert.status === 'NEW') {
      actions.push({
        id: `ack-${alert.id}`,
        type: 'INVESTIGATE',
        label: 'Acknowledge & Investigate',
        description: 'Start investigating this alert',
        priority: 1,
        handler: async (a: any) => {
          await this.acknowledgeAlert(a.id, 'system');
        },
      });
    }

    if (alert.severity === 'CRITICAL' || alert.severity === 'HIGH') {
      actions.push({
        id: `esc-${alert.id}`,
        type: 'ESCALATE',
        label: 'Escalate to Supervisor',
        description: 'Escalate this alert to higher authority',
        priority: 2,
        handler: async (a: any) => {
          await this.escalateAlert(a.id, 'High severity alert needs attention', 'system');
        },
      });
    }

    if (alert.status === 'ACKNOWLEDGED') {
      actions.push({
        id: `res-${alert.id}`,
        type: 'RESOLVE',
        label: 'Mark as Resolved',
        description: 'Alert has been addressed',
        priority: 3,
        handler: async (a: any) => {
          await this.resolveAlert(a.id, 'Resolved after investigation', 'system');
        },
      });
    }

    return actions.sort((a, b) => a.priority - b.priority);
  }

  async checkForAnomalies(caseId: string): Promise<void> {
    try {
      const response = await api.get(`/api/v1/intelligence/graph-risk/${caseId}`);
      const data = response.data;
      if (data.anomaly_score > 0.7) {
        this.emit('anomaly-detected', {
          caseId,
          score: data.anomaly_score,
          timestamp: new Date(),
        });
      }
    } catch (error) {
      console.error('[AlertService] Anomaly check failed:', error);
    }
  }
}

export const alertService = new AlertService();
