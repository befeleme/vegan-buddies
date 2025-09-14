import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (username, password) => {
    console.log('Sending login request with:', { username, password: password ? '[REDACTED]' : 'undefined' });
    try {
      const response = await api.post('/auth/login', { username, password });
      console.log('Login response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Login error:', error.response?.data || error.message);
      throw error;
    }
  },
};

export const usersAPI = {
  getUsers: async () => {
    const response = await api.get('/users');
    return response.data;
  },
  createAdminUser: async (userData) => {
    const response = await api.post('/users', userData);
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/me');
    return response.data;
  },
  changePassword: async (passwordData) => {
    const response = await api.post('/change-password', passwordData);
    return response.data;
  },
};

export default api;
