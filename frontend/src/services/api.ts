interface ApiErrorBody {
  error?: { message?: string; code?: string };
  detail?: string;
}

export class ApiError extends Error {
  constructor(message: string, readonly status: number, readonly code?: string) {
    super(message);
    this.name = 'ApiError';
  }
}

const baseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function apiRequest<T>(path: string, init: RequestInit = {}, authenticated = true): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body) headers.set('Content-Type', 'application/json');
  const token = authenticated ? localStorage.getItem('car-inventory-token') : null;
  if (token) headers.set('Authorization', `Bearer ${token}`);

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, { ...init, headers });
  } catch {
    throw new ApiError('Unable to reach the inventory service. Please try again.', 0, 'network_error');
  }

  if (response.status === 204) return undefined as T;
  const body = await response.json().catch(() => null) as ApiErrorBody | T | null;
  if (!response.ok) {
    const errorBody = body as ApiErrorBody | null;
    throw new ApiError(
      errorBody?.error?.message || errorBody?.detail || 'The request could not be completed.',
      response.status,
      errorBody?.error?.code,
    );
  }
  return body as T;
}
