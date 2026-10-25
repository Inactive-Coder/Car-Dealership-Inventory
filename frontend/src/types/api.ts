export type UserRole = 'user' | 'admin';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
  user: User;
}

export interface Vehicle {
  id: string;
  make: string;
  model: string;
  category: string;
  price: number;
  quantity: number;
  created_at: string;
  updated_at: string;
}

export interface VehiclePage {
  items: Vehicle[];
  offset: number;
  limit: number;
  total: number;
}

export interface VehicleInput {
  make: string;
  model: string;
  category: string;
  price: number;
  quantity: number;
}
