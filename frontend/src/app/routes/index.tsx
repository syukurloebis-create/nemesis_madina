/**
 * Application Routes
 * Central route configuration
 */

import React from 'react';
import { RouteObject } from 'react-router-dom';

// Import all pages
import Dashboard from '../../pages/Dashboard';
import Login from '../../pages/Login';
import ExecutiveDashboard from '../../pages/ExecutiveDashboard';
import IntelligenceDashboard from '../../pages/IntelligenceDashboard';
import ProcurementIntelligence from './ProcurementIntelligence';
import VendorIntelligence from '../../pages/vendor/VendorIntelligence';
import RecoveryIntelligence from '../../pages/RecoveryIntelligence';
import CollusionGraphPage from '../../pages/CollusionGraphPage';
import GraphIntelligence from '../../pages/GraphIntelligence';

// Define routes
export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Dashboard />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/executive-dashboard',
    element: <ExecutiveDashboard />,
  },
  {
    path: '/intelligence-dashboard',
    element: <IntelligenceDashboard />,
  },
  {
    path: '/procurement-intelligence',
    element: <ProcurementIntelligence />,
  },
  {
    path: '/vendor-intelligence',
    element: <VendorIntelligence />,
  },
  {
    path: '/recovery-intelligence',
    element: <RecoveryIntelligence />,
  },
  {
    path: '/collusion-graph',
    element: <CollusionGraphPage />,
  },
  {
    path: '/graph-intelligence',
    element: <GraphIntelligence />,
  },
  {
    path: '/forensic-dashboard',
  },
];

export default routes;
