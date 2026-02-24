import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Simple axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

// Auth API (no token needed)
export const authApi = {
  register: async (data: any) => {
    const response = await apiClient.post('/api/auth/register', {
        ...data,
        organization: data.organization || '' // Include organization
    });
    return response.data;
  },
  
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    // Axios handles content-type for URLSearchParams automatically
    const response = await apiClient.post('/api/auth/login', formData);
    
    // Save token
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
    }
    
    return response.data;
  },
};

// Protected API (needs token)
const getAuthHeaders = () => {
  if (typeof window === 'undefined') return {}; // Server-side safety
  
  const token = localStorage.getItem('access_token');
  if (!token) {
      console.warn('No access token found in localStorage');
      // We could throw here, or let the API call fail. 
      // Returning empty/null might be safer effectively, 
      // but let's return a valid object structure so we don't crash on spread
      return {}; 
  }
  return {
    'Authorization': `Bearer ${token}`
  };
};

export const api = {
  // Re-export auth methods
  ...authApi,
  
  // Upload with token
  uploadImage: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/upload/image', formData, {
      headers: getAuthHeaders()
    });
    
    return response.data;
  },
  
  uploadVideo: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/upload/video', formData, {
      headers: getAuthHeaders()
    });
    
    return response.data;
  },
  
  // Analysis
  startAnalysis: async (scanId: string) => {
    const response = await apiClient.post(
      `/api/analyze/start/${scanId}`,
      {},
      { headers: getAuthHeaders() }
    );
    return response.data;
  },
  
  getResult: async (scanId: string) => {
    const response = await apiClient.get(`/api/analyze/result/${scanId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },
  
  getMe: async () => {
    const response = await apiClient.get('/api/auth/me', {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  updateMe: async (data: any) => {
    const response = await apiClient.put('/api/auth/me', data, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  deleteMe: async () => {
    const response = await apiClient.delete('/api/auth/me', {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  // Audio Upload
  uploadAudio: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/upload/audio', formData, { 
        headers: getAuthHeaders() 
    });
    return response.data;
  },

  // Analysis Ext
  getAnalysisStatus: async (scanId: string) => {
    const response = await apiClient.get(`/api/analyze/status/${scanId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  // Reports
  getReportJson: async (scanId: string) => {
    const response = await apiClient.get(`/api/report/${scanId}/json`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  getReportPdf: async (scanId: string) => {
     const response = await apiClient.get(`/api/report/${scanId}/pdf`, {
       headers: getAuthHeaders(),
       responseType: 'blob'
     });
     return response.data;
  },

  // Trusted Capture
  startCapture: async () => {
    const response = await apiClient.post('/api/capture/start', {}, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  sealCapture: async (captureId: string, data: any) => {
    const response = await apiClient.post('/api/capture/seal', 
      { capture_id: captureId, ...data }, 
      { headers: getAuthHeaders() }
    );
    return response.data;
  },

  verifyCapture: async (captureId: string) => {
    // Verification might be public, but sends auth anyway if available? 
    // Usually verification is public. But let's assume public.
    const response = await apiClient.get(`/api/capture/verify/${captureId}`);
    return response.data;
  },
  
  // History
  getHistory: async () => {
    const response = await apiClient.get('/api/history', {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  getBin: async () => {
    const response = await apiClient.get('/api/history/bin', {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  deleteScan: async (scanId: string) => {
    const response = await apiClient.delete(`/api/history/${scanId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  restoreScan: async (scanId: string) => {
    const response = await apiClient.post(`/api/history/${scanId}/restore`, {}, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  permanentDeleteScan: async (scanId: string) => {
    const response = await apiClient.delete(`/api/history/${scanId}/permanent`, {
      headers: getAuthHeaders()
    });
    return response.data;
  },

  batchExportScans: async (scanIds: string[]) => {
    const response = await apiClient.post(`/api/report/batch-export`, scanIds, {
      headers: getAuthHeaders(),
      responseType: 'blob'
    });
    return response.data;
  },
  
  // Helpers
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
};

export default api;