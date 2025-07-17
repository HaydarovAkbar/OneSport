# OneSport Frontend Integration Guide

## Overview

This guide provides comprehensive instructions for integrating your frontend application with the OneSport API. The guide covers authentication, API calls, real-time features, and best practices.

## Quick Start

### 1. Environment Setup

Create a `.env` file in your frontend project:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_WS_BASE_URL=ws://localhost:8000/ws
REACT_APP_MEDIA_BASE_URL=http://localhost:8000/media
```

### 2. Install Dependencies

```bash
npm install axios
npm install socket.io-client  # For WebSocket connections
npm install react-query       # For API state management
npm install @tanstack/react-query  # v4 alternative
```

### 3. API Client Setup

Create an API client (`src/api/client.js`):

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        
        const { access } = response.data;
        localStorage.setItem('accessToken', access);
        
        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

For complete frontend integration guide, authentication setup, real-time features, and best practices, please refer to the full documentation.
