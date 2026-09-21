import axios from 'axios';
import authService from '../auth';

// Use environment variable with fallback
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

console.log(`🔗 API Base URL: ${API_BASE_URL} (${import.meta.env.PROD ? 'production' : 'development'})`);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    console.log('🔑 Token from authService:', token ? token.substring(0, 30) + '...' : 'null');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ Added Authorization header');
    } else {
      console.log('❌ No token found');
    }
    
    console.log('📤 Request:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
    });
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ Response: ${response.status} ${response.config.url}`);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = authService.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        const response = await axios.post(
          `${API_BASE_URL}/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );
        
        authService.setTokens(response.data.access_token, refreshToken);
        originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
        authService.clearTokens();
        // Guard for non-browser environments (e.g. contract tests)
        if (typeof window !== 'undefined' && window.location) {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }
    
    console.error(`❌ Response error: ${error.response?.status} ${error.response?.config?.url}`);
    return Promise.reject(error);
  }
);

export { apiClient };
export default apiClient;
