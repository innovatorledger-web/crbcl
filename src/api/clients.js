import { api } from './client';

export const clientsApi = {
  list: (params = {}) => api.entities.Client.list(params.sort, params.limit),
  get: (id, allowDeleted = false) => api.fetch(`/api/v1/clients/${id}?allow_deleted=${allowDeleted}`).then(res => res.json()).catch(() => api.entities.Client.get(id)),
  create: (data) => api.entities.Client.create(data),
  update: (id, data) => api.patch(`/api/v1/clients/${id}`, data),
  delete: async (id) => {
    const res = await api.fetch(`/api/v1/clients/${id}`, { method: 'DELETE' });
    if (res.ok || res.status === 204) return true;
    const data = await res.json().catch(() => ({}));
    const msg =
      data?.detail?.error?.message ||
      data?.error?.message ||
      (typeof data?.detail === 'string' ? data.detail : null) ||
      'Could not delete client record.';
    throw new Error(msg);
  },

  uploadPhoto: async (clientId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.fetch(`/api/v1/clients/${clientId}/photo`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData?.detail?.message || errData?.detail || 'Photo upload failed.');
    }
    return res.json();
  },

  // Phase 2 Sub-Resources
  checkDuplicates: (criteria) =>
    api.fetch('/api/v1/clients/duplicate-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(criteria),
    }).then(res => res.json()),

  merge: (sourceId, targetId, reason, notes = '') =>
    api.fetch('/api/v1/clients/merge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_person_id: sourceId, target_person_id: targetId, reason, notes }),
    }).then(res => res.json()),

  getMedical: (clientId) =>
    api.fetch(`/api/v1/clients/${clientId}/medical`).then(res => res.json()),

  updateMedicalProfile: (clientId, data) =>
    api.fetch(`/api/v1/clients/${clientId}/medical`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),

  addAllergy: (clientId, data) =>
    api.fetch(`/api/v1/clients/${clientId}/allergies`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),

  addCondition: (clientId, data) =>
    api.fetch(`/api/v1/clients/${clientId}/conditions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),

  addMedication: (clientId, data) =>
    api.fetch(`/api/v1/clients/${clientId}/medications`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),

  getProviders: (clientId) =>
    api.fetch(`/api/v1/clients/${clientId}/providers`).then(res => res.json()),

  linkProvider: (clientId, data) =>
    api.fetch(`/api/v1/clients/${clientId}/providers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),

  getSchools: (clientId) =>
    api.fetch(`/api/v1/clients/${clientId}/schools`).then(res => res.json()),

  enrollSchool: (clientId, data) =>
    api.fetch(`/api/v1/clients/${clientId}/schools`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(res => res.json()),

  getTimeline: (clientId) =>
    api.fetch(`/api/v1/clients/${clientId}/timeline`).then(res => res.json()),

  // Approval Workflow & Canonical Identity Methods
  searchPersons: (params = {}) => {
    const q = new URLSearchParams();
    if (typeof params === 'string') {
      q.set('query', params);
    } else {
      if (params.query) q.set('query', params.query);
      if (params.person_id_number) q.set('person_id_number', params.person_id_number);
      if (params.date_of_birth) q.set('date_of_birth', params.date_of_birth);
      if (params.limit) q.set('limit', params.limit);
      if (params.offset) q.set('offset', params.offset);
    }
    return api.fetch(`/api/v1/clients/search-person?${q.toString()}`).then(res => res.json());
  },

  submitExisting: (payload) =>
    api.fetch('/api/v1/clients/submit-existing', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    }),

  submitNew: (payload) =>
    api.fetch('/api/v1/clients/submit-new', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    }),

  getPendingApprovals: (offset = 0, limit = 50) =>
    api.fetch(`/api/v1/clients/approvals/pending?offset=${offset}&limit=${limit}`).then(res => res.json()),

  getApprovalReview: (clientId) =>
    api.fetch(`/api/v1/clients/approvals/${clientId}`).then(res => res.json()),

  approve: (clientId, notes = '') =>
    api.fetch(`/api/v1/clients/approvals/${clientId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes }),
    }).then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    }),

  returnProposal: (clientId, reason) =>
    api.fetch(`/api/v1/clients/approvals/${clientId}/return`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    }).then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    }),

  declineProposal: (clientId, reason) =>
    api.fetch(`/api/v1/clients/approvals/${clientId}/decline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    }).then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    }),

  listFiltered: (approvalStatus = null, limit = 100, offset = 0, trash = false) => {
    const q = new URLSearchParams();
    if (approvalStatus && approvalStatus !== 'ALL') q.set('approval_status', approvalStatus);
    if (trash) q.set('trash', 'true');
    q.set('limit', limit);
    q.set('offset', offset);
    return api.fetch(`/api/v1/clients?${q.toString()}`).then(res => res.json());
  },

  getCounts: () =>
    api.fetch('/api/v1/clients/counts').then(res => res.json()).catch(() => null),

  restore: async (id) => {
    const res = await api.fetch(`/api/v1/clients/${id}/restore`, {
      method: 'POST',
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg =
        data?.detail?.error?.message ||
        data?.error?.message ||
        (typeof data?.detail === 'string' ? data.detail : null) ||
        'Could not restore client record.';
      throw new Error(msg);
    }
    return data;
  },

  permanentDelete: async (id) => {
    const res = await api.fetch(`/api/v1/clients/${id}/permanent`, {
      method: 'DELETE',
    });
    if (res.ok || res.status === 204) return true;
    const data = await res.json().catch(() => ({}));
    const msg =
      data?.detail?.error?.message ||
      data?.error?.message ||
      (typeof data?.detail === 'string' ? data.detail : null) ||
      'Could not permanently delete client record.';
    throw new Error(msg);
  },
};
