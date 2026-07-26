import axios from 'axios';
import authService from '../auth';
import retryInterceptor from './retryInterceptor';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

retryInterceptor.setup(apiClient);

apiClient.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// SIMPLE RESPONSE INTERCEPTOR - NO DATA TRANSFORM
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = authService.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/auth/refresh`,
            { refresh_token: refreshToken }
          );
          authService.setTokens(response.data.access_token, refreshToken);
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
          return apiClient(originalRequest);
        }
      } catch {
        authService.clearTokens();
        authService.clearUser();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
export { apiClient };
