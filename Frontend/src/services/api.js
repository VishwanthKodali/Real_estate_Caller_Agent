import axios from 'axios'

const api = axios.create({ baseURL: '/api/v1' })

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// Auth
export const authApi = {
  register: d => api.post('/auth/register', d),
  login: d => api.post('/auth/login', d),
  me: () => api.get('/auth/me'),
  updateMe: d => api.put('/auth/me', d),
}

// Projects
export const projectsApi = {
  list: () => api.get('/projects'),
  get: id => api.get(`/projects/${id}`),
  create: d => api.post('/projects', d),
  update: (id, d) => api.put(`/projects/${id}`, d),
  delete: id => api.delete(`/projects/${id}`),
}

// Documents
export const documentsApi = {
  list: projectId => api.get(`/documents/${projectId}`),
  upload: (projectId, formData) => api.post(`/documents/${projectId}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getText: (projectId, docId) => api.get(`/documents/${projectId}/${docId}/text`),
  delete: (projectId, docId) => api.delete(`/documents/${projectId}/${docId}`),
  reprocess: (projectId, docId) => api.post(`/documents/${projectId}/reprocess/${docId}`),
}

// Campaigns
export const campaignsApi = {
  list: (projectId) => api.get('/campaigns', { params: projectId ? { project_id: projectId } : {} }),
  get: id => api.get(`/campaigns/${id}`),
  create: d => api.post('/campaigns', d),
  update: (id, d) => api.put(`/campaigns/${id}`, d),
  delete: id => api.delete(`/campaigns/${id}`),
  activate: id => api.post(`/campaigns/${id}/activate`),
  pause: id => api.post(`/campaigns/${id}/pause`),
  agentDetails: id => api.get(`/campaigns/${id}/agent-details`),
}

// Prospects
export const prospectsApi = {
  list: (campaignId, status) => api.get(`/prospects/${campaignId}`, { params: status ? { status } : {} }),
  get: (campaignId, id) => api.get(`/prospects/${campaignId}/${id}`),
  create: (campaignId, d) => api.post(`/prospects/${campaignId}`, d),
  update: (campaignId, id, d) => api.put(`/prospects/${campaignId}/${id}`, d),
  delete: (campaignId, id) => api.delete(`/prospects/${campaignId}/${id}`),
  bulkUpload: (campaignId, file) => {
    const fd = new FormData(); fd.append('file', file)
    return api.post(`/prospects/${campaignId}/bulk-upload`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

// Calls
export const callsApi = {
  startCampaign: (campaignId, maxCalls) => api.post(`/calls/${campaignId}/start`, null, { params: maxCalls ? { max_calls: maxCalls } : {} }),
  callProspect: (campaignId, prospectId) => api.post(`/calls/${campaignId}/call/${prospectId}`),
  logs: (campaignId, filters) => api.get(`/calls/${campaignId}/logs`, { params: filters }),
  stats: campaignId => api.get(`/calls/${campaignId}/stats`),
  hotProspects: campaignId => api.get(`/calls/${campaignId}/hot-prospects`),
  updateOutcome: (campaignId, callId, params) => api.post(`/calls/${campaignId}/calls/${callId}/update-outcome`, null, { params }),
  voices: () => api.get('/calls/voices'),
}

// Dashboard
export const dashboardApi = {
  stats: () => api.get('/dashboard/stats'),
}

export default api
