// Dashboard.tsx - Fixed version

import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from "react-toastify";
import { MainLayout } from "../components/layout/MainLayout";
import { useIntelligenceDashboard } from "../hooks/useIntelligenceDashboard";
import { normalizeIntelligence } from "../services/intelligenceAdapter";
import authService from "../services/auth";
import { apiClient } from "../services/api/client";
import ExecutiveHeader from "../components/Intelligence/ExecutiveHeader";
import ExecutiveKPIRow from "../components/Intelligence/ExecutiveKPIRow";
import IntelligenceTabs from "../components/Intelligence/IntelligenceTabs";
import "react-toastify/dist/ReactToastify.css";
import axios from 'axios';
import type {
  AppRouteId,
  DashboardActionId,
  IntelligenceTabId,
} from '../types/navigation';

const CASE_ID = "b4897392-87ab-4e7a-84b6-90228f3d1eb9";
const USER_ID = "user-123";

export default function Dashboard() {
  const navigate = useNavigate();

  // Auth check
  useEffect(() => {
    const token = authService.getAccessToken();
    if (!token) {
      console.log('🔑 No token found, redirecting to login');
      navigate('/login', { replace: true });
    }
  }, [navigate]);

  // Data fetching
  const {
    data,
    loading,
    error,
    refresh
  } = useIntelligenceDashboard(CASE_ID);

  const intelligence = data ? normalizeIntelligence(data) : null;
  const [activeTab, setActiveTab] = useState<IntelligenceTabId>("overview");

  const handleTabChange = useCallback((tab: IntelligenceTabId) => {
    setActiveTab(tab);
  }, []);

  const handleAction = useCallback((action: DashboardActionId) => {
    console.log("[Dashboard Action]", action);
    toast.info(action);

    switch (action) {
      // Overview contextual actions stay inside the intelligence tabs.
      case "fraud":
      case "graph":
      case "overview":
      case "risk":
      case "evidence":
      case "timeline":
        setActiveTab(action);
        return;

      // Existing application routes retain their navigation behavior.
      case "alerts":
        navigate("/alerts");
        return;

      case "investigation":
        navigate("/investigation");
        return;

      case "recovery":
        navigate("/recovery");
        return;

      case "procurement":
        navigate("/procurement");
        return;

    }
  }, [navigate]);

  // Test API connection - use a known valid endpoint
  useEffect(() => {
    const testApi = async () => {
      try {
        console.log('🔗 Testing API connection...');
        // Health check bypasses /api — nginx serves /health at root
        const response = await axios.get('/health');
        console.log('✅ API connection test:', response.status);
      } catch (err) {
        console.error('❌ API connection test failed:', err);
      }
    };
    testApi();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080f1d] flex items-center justify-center text-white">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 mx-auto rounded-full border-4 border-primary-500 border-t-transparent animate-spin" />
          <p className="text-gray-400">Loading Intelligence Command Center...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="m-10 rounded-xl border border-red-500 bg-red-900/20 p-6 text-red-300">
        <h2 className="text-xl font-bold mb-3">Intelligence Engine Failure</h2>
        <p>{error}</p>
        <button onClick={refresh} className="mt-4 px-4 py-2 bg-red-600 rounded-lg text-white hover:bg-red-700 transition-colors">
          Retry
        </button>
      </div>
    );
  }

  if (!intelligence) {
    return <div className="p-10 text-center text-gray-400">No Intelligence Data</div>;
  }

  return (
    <MainLayout>
      <ToastContainer position="top-right" theme="dark" />
      <div className="p-6">
        <ExecutiveHeader intelligence={intelligence} />
        <ExecutiveKPIRow intelligence={intelligence} />
        <div className="mt-6">
          <IntelligenceTabs 
            intelligence={intelligence}
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            caseId={CASE_ID}
            userId={USER_ID}
            onAction={handleAction}
          />
        </div>
      </div>
    </MainLayout>
  );
}
