/**
 * Prevention & Healing Records Workspace API Client
 * Connects to backend /api/v1/ph endpoints.
 */

import { api } from './client';

export const preventionHealingApi = {
  // ── Enhancement Programs ──
  getEnhancementPrograms: async (params = {}) => {
    return await api.get('/ph/enhancement-programs', { params });
  },

  getEnhancementProgram: async (id) => {
    return await api.get(`/ph/enhancement-programs/${id}`);
  },

  createEnhancementProgram: async (data) => {
    return await api.post('/ph/enhancement-programs', data);
  },

  updateEnhancementProgram: async (id, data) => {
    return await api.put(`/ph/enhancement-programs/${id}`, data);
  },

  deleteEnhancementProgram: async (id) => {
    return await api.delete(`/ph/enhancement-programs/${id}`);
  },

  // ── Family Support Records ──
  getFamilySupportRecords: async (params = {}) => {
    return await api.get('/ph/family-support', { params });
  },

  getFamilySupportRecord: async (id) => {
    return await api.get(`/ph/family-support/${id}`);
  },

  createFamilySupportRecord: async (data) => {
    return await api.post('/ph/family-support', data);
  },

  updateFamilySupportRecord: async (id, data) => {
    return await api.put(`/ph/family-support/${id}`, data);
  },

  deleteFamilySupportRecord: async (id) => {
    return await api.delete(`/ph/family-support/${id}`);
  },

  // ── Other Nations Support ──
  getOtherNationsSupport: async (params = {}) => {
    return await api.get('/ph/other-nations', { params });
  },

  getOtherNationsRecord: async (id) => {
    return await api.get(`/ph/other-nations/${id}`);
  },

  createOtherNationsRecord: async (data) => {
    return await api.post('/ph/other-nations', data);
  },

  updateOtherNationsRecord: async (id, data) => {
    return await api.put(`/ph/other-nations/${id}`, data);
  },

  deleteOtherNationsRecord: async (id) => {
    return await api.delete(`/ph/other-nations/${id}`);
  },

  // ── Inactive Staff Onboarding Profiles ──
  getPendingStaff: async (params = {}) => {
    return await api.get('/ph/pending-staff', { params });
  },

  createPendingStaff: async (data) => {
    return await api.post('/ph/pending-staff', data);
  },

  updatePendingStaff: async (id, data) => {
    return await api.put(`/ph/pending-staff/${id}`, data);
  },

  activatePendingStaff: async (id, data) => {
    return await api.post(`/ph/pending-staff/${id}/activate`, data);
  },

  // ── Client Reconciliation ──
  getClientRefs: async (params = {}) => {
    return await api.get('/ph/client-refs', { params });
  },

  reconcileClientRef: async (id, data) => {
    return await api.post(`/ph/client-refs/${id}/reconcile`, data);
  },

  searchPersons: async (q) => {
    return await api.get('/ph/persons/search', { params: { q } });
  },

  // ── Safe 8-Step Excel Import Wizard ──
  analyzeImport: async (formData) => {
    return await api.post('/ph/import/analyze', formData);
  },

  getImportBatches: async (params = {}) => {
    return await api.get('/ph/import/batches', { params });
  },

  getImportBatch: async (id) => {
    return await api.get(`/ph/import/batches/${id}`);
  },

  getImportBatchRows: async (id, params = {}) => {
    return await api.get(`/ph/import/batches/${id}/rows`, { params });
  },

  approveImportBatch: async (id) => {
    return await api.post(`/ph/import/approve/${id}`);
  },

  executeImportBatch: async (id) => {
    return await api.post(`/ph/import/execute/${id}`);
  },

  cancelImportBatch: async (id) => {
    return await api.post(`/ph/import/cancel/${id}`);
  },

  // ── Annual Summary & Reports ──
  getSummary: async (fiscalYear = '2026-2027') => {
    return await api.get('/ph/summary', { params: { fiscal_year: fiscalYear } });
  },
};

export default preventionHealingApi;
