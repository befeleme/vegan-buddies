import React, { useState, useEffect } from 'react';

const ConfigError = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/health`);
      const data = await response.json();
      setHealthData(data);
    } catch (error) {
      setHealthData({
        status: 'unhealthy',
        environment: 'not_configured',
        admin_users: 0,
        error: 'Unable to connect to backend'
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card" style={{ maxWidth: '600px', margin: '100px auto', textAlign: 'center' }}>
          <h2>Checking Configuration...</h2>
          <p>Please wait while we verify your setup.</p>
        </div>
      </div>
    );
  }

  const needsEnvSetup = healthData?.environment === 'not_configured';
  const needsAdminUser = healthData?.admin_users === 0;

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '600px', margin: '100px auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ color: '#dc3545', marginBottom: '10px' }}>⚠️ Configuration Required</h1>
          <p style={{ color: '#666' }}>Your Vegan Buddies application needs to be configured before you can use it.</p>
        </div>

        {needsEnvSetup && (
          <div style={{ 
            backgroundColor: '#f8d7da', 
            border: '1px solid #f5c6cb', 
            borderRadius: '4px', 
            padding: '20px', 
            marginBottom: '20px' 
          }}>
            <h3 style={{ color: '#721c24', marginTop: 0 }}>🔐 Environment Not Configured</h3>
            <p style={{ color: '#721c24', marginBottom: '15px' }}>
              The application needs secure environment variables to be generated.
            </p>
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '4px', marginBottom: '15px' }}>
              <h4 style={{ marginTop: 0, color: '#495057' }}>Run this command:</h4>
              <code style={{ 
                backgroundColor: '#e9ecef', 
                padding: '8px 12px', 
                borderRadius: '4px', 
                display: 'block',
                fontFamily: 'monospace',
                fontSize: '14px'
              }}>
                python setup_env.py
              </code>
            </div>
            <p style={{ color: '#721c24', fontSize: '14px', margin: 0 }}>
              This will generate secure database credentials and JWT secret keys.
            </p>
          </div>
        )}

        {needsAdminUser && (
          <div style={{ 
            backgroundColor: '#fff3cd', 
            border: '1px solid #ffeaa7', 
            borderRadius: '4px', 
            padding: '20px', 
            marginBottom: '20px' 
          }}>
            <h3 style={{ color: '#856404', marginTop: 0 }}>👤 No Admin Users Found</h3>
            <p style={{ color: '#856404', marginBottom: '15px' }}>
              You need to create an admin user to access the application.
            </p>
            <div style={{ backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '4px', marginBottom: '15px' }}>
              <h4 style={{ marginTop: 0, color: '#495057' }}>Run this command:</h4>
              <code style={{ 
                backgroundColor: '#e9ecef', 
                padding: '8px 12px', 
                borderRadius: '4px', 
                display: 'block',
                fontFamily: 'monospace',
                fontSize: '14px'
              }}>
                python create_admin.py
              </code>
            </div>
            <p style={{ color: '#856404', fontSize: '14px', margin: 0 }}>
              This will create an admin user with auto-generated credentials.
            </p>
          </div>
        )}

        <div style={{ 
          backgroundColor: '#d1ecf1', 
          border: '1px solid #bee5eb', 
          borderRadius: '4px', 
          padding: '20px' 
        }}>
          <h3 style={{ color: '#0c5460', marginTop: 0 }}>🚀 Next Steps</h3>
          <ol style={{ color: '#0c5460', paddingLeft: '20px' }}>
            {needsEnvSetup && <li>Run <code>python setup_env.py</code> to configure environment</li>}
            <li>Run <code>docker-compose up</code> to start the services</li>
            {needsAdminUser && <li>Run <code>python create_admin.py</code> to create an admin user</li>}
            <li>Refresh this page to continue</li>
          </ol>
        </div>

        <div style={{ textAlign: 'center', marginTop: '30px' }}>
          <button 
            onClick={checkHealth}
            className="btn"
            style={{ marginRight: '10px' }}
          >
            🔄 Check Again
          </button>
          <button 
            onClick={() => window.location.reload()}
            className="btn btn-secondary"
          >
            🔄 Refresh Page
          </button>
        </div>

        {healthData?.error && (
          <div style={{ 
            backgroundColor: '#f8d7da', 
            border: '1px solid #f5c6cb', 
            borderRadius: '4px', 
            padding: '15px', 
            marginTop: '20px' 
          }}>
            <h4 style={{ color: '#721c24', marginTop: 0 }}>Error Details:</h4>
            <pre style={{ 
              color: '#721c24', 
              fontSize: '12px', 
              margin: 0,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {JSON.stringify(healthData.error, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfigError;
