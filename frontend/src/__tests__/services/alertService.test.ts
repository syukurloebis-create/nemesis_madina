// frontend/src/__tests__/services/alertService.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { alertService } from '@/services/alertService';
import { api } from '@/services/api';

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('AlertService', () => {
  const mockCaseId = 'test-case-123';
  const mockUserId = 'user-456';
  const mockAlert = {
    id: 'alert-1',
    case_id: mockCaseId,
    type: 'COLLUSION',
    severity: 'HIGH',
    title: 'Collusion Detected',
    description: 'Suspicious bidding pattern detected',
    timestamp: '2026-06-22T10:00:00Z',
    status: 'NEW',
    source: 'AI_ANALYTICS',
    confidence: 0.85,
    evidence: ['pattern-1', 'pattern-2'],
    metadata: { detected_at: '2026-06-22T10:00:00Z' },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    (api.get as any).mockImplementation((url: string) => {
      if (url.includes('/alerts')) {
        return Promise.resolve({ data: [mockAlert] });
      }
      return Promise.resolve({ data: {} });
    });

    (api.post as any).mockResolvedValue({ data: { success: true } });
  });

  describe('getAlerts', () => {
    it('should fetch all alerts for a case', async () => {
      const alerts = await alertService.getAlerts(mockCaseId);
      
      expect(alerts).toHaveLength(1);
      expect(alerts[0].id).toBe('alert-1');
      expect(alerts[0].title).toBe('Collusion Detected');
      expect(api.get).toHaveBeenCalledWith('/api/v1/alerts', {
        params: { case_id: mockCaseId },
      });
    });

    it('should transform alerts correctly', async () => {
      const alerts = await alertService.getAlerts(mockCaseId);
      const alert = alerts[0];
      
      expect(alert).toHaveProperty('id');
      expect(alert).toHaveProperty('caseId');
      expect(alert).toHaveProperty('type');
      expect(alert).toHaveProperty('severity');
      expect(alert).toHaveProperty('title');
      expect(alert).toHaveProperty('description');
      expect(alert).toHaveProperty('timestamp');
      expect(alert).toHaveProperty('status');
      expect(alert).toHaveProperty('source');
      expect(alert).toHaveProperty('confidence');
      expect(alert).toHaveProperty('evidence');
      expect(alert).toHaveProperty('metadata');
    });
  });

  describe('getActiveAlerts', () => {
    it('should fetch only active (NEW or ACKNOWLEDGED) alerts', async () => {
      const alerts = await alertService.getActiveAlerts(mockCaseId);
      
      expect(alerts).toHaveLength(1);
      expect(alerts[0].status).toBe('NEW');
    });

    it('should filter out resolved alerts', async () => {
      const resolvedAlert = {
        ...mockAlert,
        id: 'alert-2',
        status: 'RESOLVED',
      };
      
      (api.get as any).mockResolvedValueOnce({
        data: [mockAlert, resolvedAlert],
      });
      
      const alerts = await alertService.getActiveAlerts(mockCaseId);
      
      expect(alerts).toHaveLength(1);
      expect(alerts[0].id).toBe('alert-1');
    });
  });

  describe('acknowledgeAlert', () => {
    it('should acknowledge an alert', async () => {
      await alertService.acknowledgeAlert('alert-1', mockUserId);
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/alerts/alert-1/acknowledge', {
        user_id: mockUserId,
      });
    });

    it('should emit acknowledge event', () => {
      const emitSpy = vi.spyOn(alertService, 'emit');
      
      alertService.acknowledgeAlert('alert-1', mockUserId);
      
      // Wait for async operation
      setTimeout(() => {
        expect(emitSpy).toHaveBeenCalledWith('alert-acknowledged', {
          alertId: 'alert-1',
          userId: mockUserId,
        });
      }, 100);
    });
  });

  describe('resolveAlert', () => {
    it('should resolve an alert', async () => {
      await alertService.resolveAlert('alert-1', 'Investigation complete', mockUserId);
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/alerts/alert-1/resolve', {
        resolution: 'Investigation complete',
        user_id: mockUserId,
      });
    });
  });

  describe('escalateAlert', () => {
    it('should escalate an alert', async () => {
      await alertService.escalateAlert('alert-1', 'Needs senior attention', mockUserId);
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/alerts/alert-1/escalate', {
        reason: 'Needs senior attention',
        user_id: mockUserId,
      });
    });
  });

  describe('getActionsForAlert', () => {
    it('should return appropriate actions for NEW alert', async () => {
      const actions = alertService.getActionsForAlert(mockAlert);
      
      expect(actions).toHaveLength(2); // Acknowledge and Escalate
      expect(actions[0].type).toBe('INVESTIGATE');
      expect(actions[1].type).toBe('ESCALATE');
    });

    it('should return resolve action for ACKNOWLEDGED alert', async () => {
      const acknowledgedAlert = {
        ...mockAlert,
        status: 'ACKNOWLEDGED' as const,
      };
      
      const actions = alertService.getActionsForAlert(acknowledgedAlert);
      
      expect(actions).toHaveLength(3); // Acknowledge, Escalate, Resolve
      expect(actions[2].type).toBe('RESOLVE');
    });

    it('should include escalate action for CRITICAL alerts', async () => {
      const criticalAlert = {
        ...mockAlert,
        severity: 'CRITICAL' as const,
      };
      
      const actions = alertService.getActionsForAlert(criticalAlert);
      
      expect(actions.some(a => a.type === 'ESCALATE')).toBe(true);
    });
  });

  describe('checkForAnomalies', () => {
    it('should check for anomalies and emit events', async () => {
      const emitSpy = vi.spyOn(alertService, 'emit');
      
      (api.get as any).mockResolvedValueOnce({
        data: { anomaly_score: 0.85 },
      });
      
      await alertService.checkForAnomalies(mockCaseId);
      
      expect(emitSpy).toHaveBeenCalledWith('anomaly-detected', {
        caseId: mockCaseId,
        score: 0.85,
        timestamp: expect.any(Date),
      });
    });

    it('should not emit event if anomaly score is below threshold', async () => {
      const emitSpy = vi.spyOn(alertService, 'emit');
      
      (api.get as any).mockResolvedValueOnce({
        data: { anomaly_score: 0.4 },
      });
      
      await alertService.checkForAnomalies(mockCaseId);
      
      expect(emitSpy).not.toHaveBeenCalled();
    });
  });

  describe('WebSocket integration', () => {
    it('should handle new alerts from WebSocket', () => {
      const emitSpy = vi.spyOn(alertService, 'emit');
      
      const wsEvent = {
        type: 'alert',
        data: mockAlert,
      };
      
      alertService.emit('ws-event', wsEvent);
      
      expect(emitSpy).toHaveBeenCalledWith('new-alert', expect.any(Object));
    });

    it('should respect cooldown period for duplicate alerts', () => {
      const emitSpy = vi.spyOn(alertService, 'emit');
      
      const wsEvent1 = {
        type: 'alert',
        data: mockAlert,
      };
      
      const wsEvent2 = {
        type: 'alert',
        data: { ...mockAlert, timestamp: new Date(Date.now() + 1000).toISOString() },
      };
      
      alertService.emit('ws-event', wsEvent1);
      alertService.emit('ws-event', wsEvent2);
      
      // Should only emit once due to cooldown
      expect(emitSpy).toHaveBeenCalledTimes(1);
    });

    it('should not exceed max alerts per case', () => {
      const emitSpy = vi.spyOn(alertService, 'emit');
      
      // Create many alerts
      for (let i = 0; i < 60; i++) {
        const wsEvent = {
          type: 'alert',
          data: {
            ...mockAlert,
            id: `alert-${i}`,
            timestamp: new Date(Date.now() + i * 1000).toISOString(),
          },
        };
        alertService.emit('ws-event', wsEvent);
      }
      
      // Should not exceed maxAlertsPerCase (50)
      const alerts = alertService['alerts'].get(mockCaseId) || [];
      expect(alerts.length).toBeLessThanOrEqual(50);
    });
  });
});