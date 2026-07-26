import React from 'react';
import { Outlet } from 'react-router-dom';

const WorkspaceLayout = () => {
  return (
    <div className="min-h-screen bg-gray-900">
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-white font-bold">NEMESIS Workspace</h1>
          <span className="text-gray-400 text-sm">Connected</span>
        </div>
      </header>
      <main className="p-6">
        <Outlet />
      </main>
    </div>
  );
};

export { WorkspaceLayout };
export default WorkspaceLayout;
