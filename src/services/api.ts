import axios from 'axios';
import { LegalQuery, QueryResponse, AnalysisResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000';
//const API_BASE_URL = "https://a2e01387c6d8.ngrok-free.app"
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 5 minutes
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Upload and analyze PDF
  async uploadPDF(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<AnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  // Download processed file
  async downloadProcessedFile(fileId: string): Promise<Blob> {
    const response = await api.get(`/download/${fileId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Process legal query
  async processLegalQuery(query: LegalQuery): Promise<QueryResponse> {
    const response = await api.post('/legal-query', query);
    return response.data;
  },
};