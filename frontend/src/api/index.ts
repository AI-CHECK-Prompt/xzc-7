import axios from 'axios';
import type { Equipment, InspectionPlan, InspectionTask, InspectionRecord, RepairOrder, PagedResponse } from '../types';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
});

export const equipmentApi = {
  create: (data: Equipment) => api.post('/equipment', data),
  list: (params?: { page?: number; page_size?: number; department?: string; status?: string }) => 
    api.get<PagedResponse<Equipment>>('/equipment', { params }),
  detail: (id: string) => api.get<Equipment>(`/equipment/${id}`),
  update: (id: string, data: Partial<Equipment>) => api.put(`/equipment/${id}`, data),
  delete: (id: string) => api.delete(`/equipment/${id}`),
  search: (keyword: string) => api.get<Equipment[]>(`/equipment/search/${keyword}`),
  departments: () => api.get<string[]>('/equipment/department/list'),
};

export const inspectionApi = {
  createPlan: (data: InspectionPlan) => api.post('/inspection/plan', data),
  listPlans: (params?: { page?: number; page_size?: number; status?: string }) => 
    api.get<PagedResponse<InspectionPlan>>('/inspection/plan', { params }),
  detailPlan: (id: string) => api.get<InspectionPlan>(`/inspection/plan/${id}`),
  updatePlan: (id: string, data: Partial<InspectionPlan>) => api.put(`/inspection/plan/${id}`, data),
  deletePlan: (id: string) => api.delete(`/inspection/plan/${id}`),
  createTask: (data: InspectionTask) => api.post('/inspection/task', data),
  listTasks: (params?: { page?: number; page_size?: number; status?: string; assignee?: string }) => 
    api.get<PagedResponse<InspectionTask>>('/inspection/task', { params }),
  updateTask: (id: string, data: Partial<InspectionTask>) => api.put(`/inspection/task/${id}`, data),
  submitRecord: (data: InspectionRecord) => api.post('/inspection/record', data),
  getRecords: (equipment_code: string) => api.get<InspectionRecord[]>(`/inspection/record/${equipment_code}`),
};

export const repairApi = {
  create: (data: RepairOrder) => api.post('/repair', data),
  list: (params?: { page?: number; page_size?: number; status?: string; priority?: string }) => 
    api.get<PagedResponse<RepairOrder>>('/repair', { params }),
  detail: (id: string) => api.get<RepairOrder>(`/repair/${id}`),
  update: (id: string, data: Partial<RepairOrder>) => api.put(`/repair/${id}`, data),
  delete: (id: string) => api.delete(`/repair/${id}`),
  getRecords: (equipment_code: string) => api.get<RepairOrder[]>(`/repair/equipment/${equipment_code}`),
};
