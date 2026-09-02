/**
 * App Component
 * Root application component with authentication
 */

import { useState, useEffect } from 'react';
import { useAuthStore } from './store/useAuthStore';
import { useProjectStore } from './store/useProjectStore';
import { UmlGeneratorPage } from './pages/UmlGeneratorPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { SettingsPage } from './pages/SettingsPage';

type AuthView = 'login' | 'register';
type AppView = 'main' | 'settings';

function App() {
  const { isAuthenticated, initializeAuth } = useAuthStore();
  const fetchProjects = useProjectStore((s) => s.fetchProjects);
  const [authView, setAuthView] = useState<AuthView>('login');
  const [appView, setAppView] = useState<AppView>('main');
  const [initialized, setInitialized] = useState(false);

  // Initialize auth on mount (refresh token if returning user)
  useEffect(() => {
    initializeAuth().finally(() => setInitialized(true));
  }, [initializeAuth]);

  // Fetch projects when authenticated
  useEffect(() => {
    if (isAuthenticated && initialized) {
      fetchProjects();
    }
  }, [isAuthenticated, initialized, fetchProjects]);

  // Show login/register pages if not authenticated
  if (!isAuthenticated) {
    if (authView === 'login') {
      return <LoginPage onSwitchToRegister={() => setAuthView('register')} />;
    }
    return <RegisterPage onSwitchToLogin={() => setAuthView('login')} />;
  }

  // Show settings page
  if (appView === 'settings') {
    return <SettingsPage onBack={() => setAppView('main')} />;
  }

  // Show main app if authenticated
  return <UmlGeneratorPage onOpenSettings={() => setAppView('settings')} />;
}

export default App;
