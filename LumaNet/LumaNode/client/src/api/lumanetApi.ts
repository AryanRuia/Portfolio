const API_BASE = '/api';

async function apiRequest(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export const api = {
  // Authentication
  login: (credentials: { username: string; password: string }) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    }),

  // Subjects
  getSubjects: () => apiRequest('/subjects'),
  createSubject: (data: any) => apiRequest('/subjects', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteSubject: (subjectId: string) => apiRequest(`/subjects/${subjectId}`, {
    method: 'DELETE',
  }),

  // Materials
  getMaterials: (subjectId: string) => apiRequest(`/materials?subject=${subjectId}`),
  uploadMaterial: async (file: File, metadata: any) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await fetch(`${API_BASE}/materials/upload`, {
      method: 'POST',
      body: formData,
    });

    return response.json();
  },
  deleteMaterial: (materialId: string) => apiRequest(`/materials/${materialId}`, {
    method: 'DELETE',
  }),

  // Users
  getUsers: () => apiRequest('/users'),
  createUser: (data: any) => apiRequest('/users', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  deleteUser: (userId: string) => apiRequest(`/users/${userId}`, {
    method: 'DELETE',
  }),
};
