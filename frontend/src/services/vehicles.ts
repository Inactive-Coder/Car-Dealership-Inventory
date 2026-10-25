import { apiRequest } from './api';
import type { Vehicle, VehicleInput, VehiclePage } from '../types/api';

export interface VehicleFilters { make?: string; model?: string; category?: string; min_price?: string; max_price?: string }

export function listVehicles(filters: VehicleFilters = {}): Promise<VehiclePage> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => { if (value?.trim()) params.set(key, value.trim()); });
  return apiRequest<VehiclePage>(params.size ? `/api/vehicles/search?${params}` : '/api/vehicles');
}

export const purchaseVehicle = (id: string) => apiRequest<Vehicle>(`/api/vehicles/${id}/purchase`, { method: 'POST' });
export const createVehicle = (payload: VehicleInput) => apiRequest<Vehicle>('/api/vehicles', { method: 'POST', body: JSON.stringify(payload) });
export const updateVehicle = (id: string, payload: VehicleInput) => apiRequest<Vehicle>(`/api/vehicles/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
export const deleteVehicle = (id: string) => apiRequest<void>(`/api/vehicles/${id}`, { method: 'DELETE' });
export const restockVehicle = (id: string, quantity: number) => apiRequest<Vehicle>(`/api/vehicles/${id}/restock`, { method: 'POST', body: JSON.stringify({ quantity }) });
