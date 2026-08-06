/**
 * Project GOAT v1.0 — Institutional Layout Container Shell
 * Step 1.4 Presentation Layer Upgrade
 */

import React, { useState } from 'react';
import { TopNav } from './TopNav';
import { LeftSidebar } from './LeftSidebar';
import { RightInspector } from './RightInspector';
import { BottomStatusBar } from './BottomStatusBar';
import { NotificationCenter } from './NotificationCenter';
import { GlobalSearchModal } from '../widgets/GlobalSearchModal';
import { EntityInspectorModal } from '../widgets/EntityInspectorModal';
import { ThemeProvider } from '../../theme/ThemeContext';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShellContent: React.FC<AppShellProps> = ({ children }) => {
  const [notificationCenterOpen, setNotificationCenterOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen w-screen bg-[#06090e] text-slate-100 font-sans overflow-hidden">
      {/* Top Header Navigation */}
      <TopNav onToggleNotificationCenter={() => setNotificationCenterOpen((prev) => !prev)} />

      {/* Main Workstation Body */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar Navigation */}
        <LeftSidebar />

        {/* Center Main Workspace Canvas */}
        <main className="flex-1 overflow-y-auto bg-[#06090e] border-r border-slate-800/80">
          {children}
        </main>

        {/* Right Event Inspector Panel */}
        <RightInspector />

        {/* Notification Center Slide-over */}
        <NotificationCenter
          isOpen={notificationCenterOpen}
          onClose={() => setNotificationCenterOpen(false)}
        />
      </div>

      {/* Operational Footer Status Bar */}
      <BottomStatusBar />

      {/* Modals & Inspectors */}
      <GlobalSearchModal />
      <EntityInspectorModal />
    </div>
  );
};

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <ThemeProvider>
      <AppShellContent>{children}</AppShellContent>
    </ThemeProvider>
  );
};
