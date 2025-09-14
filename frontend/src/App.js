import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import UserManagement from './components/UserManagement';
import PasswordChange from './components/PasswordChange';
import ConfigError from './components/ConfigError';
import { usersAPI } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [needsPasswordChange, setNeedsPasswordChange] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [configError, setConfigError] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    // First check if the backend is properly configured
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/health`);
      const healthData = await response.json();
      
      if (healthData.status === 'unhealthy' || healthData.environment === 'not_configured' || healthData.admin_users === 0) {
        setConfigError(true);
        setLoading(false);
        return;
      }
    } catch (error) {
      setConfigError(true);
      setLoading(false);
      return;
    }

    // If backend is healthy, proceed with normal auth check
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const user = await usersAPI.getMe();
        setCurrentUser(user);
        setIsAuthenticated(true);
        setNeedsPasswordChange(user.password_change_required);
      } catch (err) {
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  };

  const handleLogin = async () => {
    try {
      const user = await usersAPI.getMe();
      setCurrentUser(user);
      setIsAuthenticated(true);
      setNeedsPasswordChange(user.password_change_required);
    } catch (err) {
      console.error('Error getting user info after login:', err);
    }
  };

  const handlePasswordChanged = () => {
    setNeedsPasswordChange(false);
    // Refresh user data
    checkAuth();
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setNeedsPasswordChange(false);
    setCurrentUser(null);
  };

  if (loading) {
    return <div style={{ textAlign: 'center', marginTop: '50px' }}>Loading...</div>;
  }

  return (
    <div className="App">
      {configError ? (
        <ConfigError />
      ) : isAuthenticated ? (
        needsPasswordChange ? (
          <PasswordChange onPasswordChanged={handlePasswordChanged} />
        ) : (
          <UserManagement onLogout={handleLogout} />
        )
      ) : (
        <Login onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
