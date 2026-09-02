/**
 * API Client
 * HTTP client with authentication and error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

interface ApiError {
  code: string;
  message: string;
  fields?: Record<string, string>;
}

export class ApiException extends Error {
  constructor(
    public code: string,
    message: string,
    public status: number,
    public fields?: Record<string, string>
  ) {
    super(message);
    this.name = 'ApiException';
  }
}

// Token storage
let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

// Request helper
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (accessToken) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // For refresh token cookie
  });

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json();

  if (!response.ok) {
    const error = data.error as ApiError;
    throw new ApiException(
      error?.code || 'UNKNOWN_ERROR',
      error?.message || 'An error occurred',
      response.status,
      error?.fields
    );
  }

  return data as T;
}

// HTTP methods
export const api = {
  get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'GET' });
  },

  post<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  patch<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  },
};

// Token refresh logic
let refreshPromise: Promise<string> | null = null;

export async function refreshAccessToken(): Promise<string> {
  // Prevent multiple simultaneous refresh requests
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await api.post<{ access_token: string; expires_in: number }>(
        '/auth/refresh'
      );
      setAccessToken(response.access_token);
      return response.access_token;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// Wrapper for authenticated requests with auto-refresh
export async function authenticatedRequest<T>(
  requestFn: () => Promise<T>
): Promise<T> {
  try {
    return await requestFn();
  } catch (error) {
    if (error instanceof ApiException && error.status === 401) {
      // Try to refresh token
      try {
        await refreshAccessToken();
        return await requestFn();
      } catch {
        // Refresh failed, clear token
        setAccessToken(null);
        throw error;
      }
    }
    throw error;
  }
}
