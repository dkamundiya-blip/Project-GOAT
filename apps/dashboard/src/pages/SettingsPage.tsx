import React from 'react';
import { Card } from '../components/ui/Card';
import { useThemeStore } from '../stores/themeStore';
import { Button } from '../components/ui/Button';

export const SettingsPage: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-100">Operator Platform Settings</h2>
        <p className="text-xs text-slate-400 mt-1">
          Configure operator workspace preferences, themes, and layout defaults.
        </p>
      </div>

      <Card title="Appearance & Themes">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm font-semibold text-slate-200">Current Theme: {theme.toUpperCase()}</div>
            <p className="text-xs text-slate-400">Toggle between dark mode and light mode aesthetics.</p>
          </div>
          <Button variant="outline" size="sm" onClick={toggleTheme}>
            Toggle Theme 🌙/☀️
          </Button>
        </div>
      </Card>
    </div>
  );
};
export default SettingsPage;
