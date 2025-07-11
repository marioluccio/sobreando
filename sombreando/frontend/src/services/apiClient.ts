import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { secureStorage } from '@/utils/secureStorage';
import { store } from '@/store';
import { refreshToken, resetAuth } from '@/store/slices/authSlice';

// API base URL - adjust for your environment
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://your-production-api.com/api/v1';

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config: AxiosRequestConfig) => {
    try {
      const tokens = await secureStorage.getTokens();
      
      if (tokens.access && config.headers) {
        config.headers.Authorization = `Bearer ${tokens.access}`;
      }
      
      return config;
    } catch (error) {
      console.error('Error adding auth token to request:', error);
      return config;
    }
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh token
        const resultAction = await store.dispatch(refreshToken());
        
        if (refreshToken.fulfilled.match(resultAction)) {
          // Retry original request with new token
          const tokens = await secureStorage.getTokens();
          if (tokens.access && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${tokens.access}`;
          }
          
          return apiClient(originalRequest);
        } else {
          // Refresh failed, logout user
          store.dispatch(resetAuth());
          return Promise.reject(error);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        store.dispatch(resetAuth());
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

// API client wrapper with error handling
export class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = apiClient;
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.get<T>(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async post<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async put<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async patch<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<T> {
    try {
      const response = await this.client.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.client.delete<T>(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any) {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      return {
        message: data.message || data.detail || 'Erro no servidor',
        status,
        errors: data.errors || {},
        isNetworkError: false,
      };
    } else if (error.request) {
      // Network error
      return {
        message: 'Erro de conexão. Verifique sua internet.',
        status: 0,
        errors: {},
        isNetworkError: true,
      };
    } else {
      // Other error
      return {
        message: error.message || 'Erro desconhecido',
        status: 0,
        errors: {},
        isNetworkError: false,
      };
    }
  }

  // Upload file with progress
  async uploadFile<T = any>(
    url: string,
    file: FormData,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<T> {
    try {
      const response = await this.client.post<T>(url, file, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Download file
  async downloadFile(url: string, filename?: string): Promise<void> {
    try {
      const response = await this.client.get(url, {
        responseType: 'blob',
      });

      // Create blob link to download
      const blob = new Blob([response.data]);
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = filename || 'download';
      link.click();
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Check if client is online
  async checkConnection(): Promise<boolean> {
    try {
      await this.client.get('/health/', { timeout: 5000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  // Set auth token manually
  setAuthToken(token: string): void {
    this.client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // Remove auth token
  removeAuthToken(): void {
    delete this.client.defaults.headers.common['Authorization'];
  }

  // Get current base URL
  getBaseURL(): string {
    return this.client.defaults.baseURL || '';
  }

  // Update base URL
  setBaseURL(baseURL: string): void {
    this.client.defaults.baseURL = baseURL;
  }
}

// Export singleton instance
export const api = new ApiClient();

export default apiClient;

