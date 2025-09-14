import React, { useState, useEffect } from 'react';
import { usersAPI } from '../services/api';

const UserManagement = ({ onLogout }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: ''
  });
  const [generatedPassword, setGeneratedPassword] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await usersAPI.getUsers();
      setUsers(response);
    } catch (err) {
      setError('Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await usersAPI.createAdminUser(formData);
      setGeneratedPassword(response.generated_password);
      setFormData({ username: '', email: '' });
      setShowAddForm(false);
      setError(''); // Clear any previous errors
      fetchUsers();
    } catch (err) {
      // Show the actual error message from the backend
      const errorMessage = err.response?.data?.detail || 'Failed to create admin user';
      setError(errorMessage);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    onLogout();
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Vegan Buddies Admin Panel</h1>
        <button onClick={handleLogout} className="btn btn-secondary">
          Logout
        </button>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Admin Users</h2>
          <button 
            onClick={() => setShowAddForm(!showAddForm)} 
            className="btn"
          >
            {showAddForm ? 'Cancel' : 'Add New Admin'}
          </button>
        </div>

        {showAddForm && (
          <form onSubmit={handleSubmit} style={{ marginBottom: '20px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
            <h3>Add New Admin User</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              A secure password will be automatically generated for this user.
            </p>
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            <button type="submit" className="btn">
              Create Admin User
            </button>
          </form>
        )}

        {generatedPassword && (
          <div style={{ marginBottom: '20px', padding: '20px', backgroundColor: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '4px' }}>
            <h4>Admin User Created Successfully!</h4>
            <p><strong>Generated Password:</strong> <code style={{ backgroundColor: '#f8f9fa', padding: '2px 4px', borderRadius: '3px' }}>{generatedPassword}</code></p>
            <p style={{ color: '#666', fontSize: '14px' }}>
              <strong>Important:</strong> Save this password securely. The user will be required to change it on first login.
            </p>
            <button 
              onClick={() => setGeneratedPassword('')} 
              className="btn btn-secondary"
              style={{ marginTop: '10px' }}
            >
              Close
            </button>
          </div>
        )}

        {error && <div className="error">{error}</div>}

        <ul className="user-list">
          {users.map(user => (
            <li key={user.id} className="user-item">
              <div className="user-info">
                <strong>{user.username}</strong>
                <div style={{ color: '#666', fontSize: '14px' }}>
                  {user.email} • Created: {new Date(user.created_at).toLocaleDateString()}
                </div>
              </div>
            </li>
          ))}
        </ul>

        {users.length === 0 && (
          <p style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
            No admin users found. Create the first admin user above.
          </p>
        )}
      </div>
    </div>
  );
};

export default UserManagement;
