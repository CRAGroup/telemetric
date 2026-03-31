/**
 * API Client for communicating with the Python backend
 * Replaces direct Supabase connections
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

interface ApiError {
  detail: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    // Load token from localStorage on init
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: 'An error occurred',
      }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth endpoints
  async login(email: string, password: string) {
    const data = await this.request<{
      access_token: string;
      refresh_token: string;
      token_type: string;
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async register(email: string, password: string, full_name?: string, role?: string) {
    return this.request<{
      id: number;
      email: string;
      full_name: string | null;
      role: string;
    }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name, role }),
    });
  }

  async getMe() {
    return this.request<{
      user_id: number;
      role: string;
      email: string;
      full_name: string | null;
      is_active: boolean;
    }>('/auth/me');
  }

  async logout() {
    this.setToken(null);
  }

  // Vehicle endpoints
  async getVehicles(params?: {
    page?: number;
    page_size?: number;
    status_filter?: string;
    make?: string;
    q?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/vehicles${query ? `?${query}` : ''}`);
  }

  async getVehicle(id: number) {
    return this.request<any>(`/vehicles/${id}`);
  }

  async createVehicle(data: any) {
    return this.request<any>('/vehicles', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateVehicle(id: number, data: any) {
    return this.request<any>(`/vehicles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteVehicle(id: number) {
    return this.request<void>(`/vehicles/${id}`, {
      method: 'DELETE',
    });
  }

  async getVehicleTelemetry(id: number) {
    return this.request<any>(`/vehicles/${id}/telemetry`);
  }

  async getVehicleLocation(id: number) {
    return this.request<{
      lat: number;
      lon: number;
      alt_m: number | null;
      speed_kph: number | null;
      heading_deg: number | null;
    }>(`/vehicles/${id}/location`);
  }

  async getVehicleTrips(id: number, params?: { page?: number; page_size?: number }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/vehicles/${id}/trips${query ? `?${query}` : ''}`);
  }

  async getVehicleAlerts(id: number, params?: { page?: number; page_size?: number }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/vehicles/${id}/alerts${query ? `?${query}` : ''}`);
  }

  // Driver endpoints
  async getDrivers(params?: {
    page?: number;
    page_size?: number;
    q?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/drivers${query ? `?${query}` : ''}`);
  }

  async getDriver(id: number) {
    return this.request<any>(`/drivers/${id}`);
  }

  async createDriver(data: any) {
    return this.request<any>('/drivers', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateDriver(id: number, data: any) {
    return this.request<any>(`/drivers/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteDriver(id: number) {
    return this.request<void>(`/drivers/${id}`, {
      method: 'DELETE',
    });
  }

  async getDriverScore(id: number) {
    return this.request<any>(`/drivers/${id}/score`);
  }

  async getDriverBehavior(id: number, params?: { page?: number; page_size?: number }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/drivers/${id}/behavior${query ? `?${query}` : ''}`);
  }

  async getDriverTrips(id: number, params?: { page?: number; page_size?: number }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/drivers/${id}/trips${query ? `?${query}` : ''}`);
  }

  async getDriverPerformance(id: number) {
    return this.request<any>(`/drivers/${id}/performance`);
  }

  async assignVehicleToDriver(driverId: number, vehicleId: number) {
    return this.request<any>(`/drivers/${driverId}/assign-vehicle?vehicle_id=${vehicleId}`, {
      method: 'PUT',
    });
  }

  // Vehicle Types endpoints
  async getVehicleTypes(params?: {
    page?: number;
    page_size?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, String(value));
        }
      });
    }
    const query = queryParams.toString();
    return this.request<{
      total: number;
      items: any[];
    }>(`/vehicle-types${query ? `?${query}` : ''}`);
  }

  async getVehicleType(id: number) {
    return this.request<any>(`/vehicle-types/${id}`);
  }

  async createVehicleType(data: any) {
    return this.request<any>('/vehicle-types', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateVehicleType(id: number, data: any) {
    return this.request<any>(`/vehicle-types/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteVehicleType(id: number) {
    return this.request<void>(`/vehicle-types/${id}`, {
      method: 'DELETE',
    });
  }

  // Profile endpoints
  async updateProfile(data: { full_name?: string; phone?: string; job_title?: string; department?: string }) {
    return this.request<{
      user_id: number;
      role: string;
      email: string;
      full_name: string | null;
      is_active: boolean;
    }>('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async changePassword(data: { current_password: string; new_password: string }) {
    return this.request<{ status: string }>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Maintenance endpoints
  async getMaintenance(params?: {
    page?: number;
    page_size?: number;
    vehicle_id?: number;
    status_filter?: string;
    q?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) queryParams.append(key, String(value));
      });
    }
    const query = queryParams.toString();
    return this.request<{ total: number; items: any[] }>(`/maintenance${query ? `?${query}` : ''}`);
  }

  async getMaintenanceStats() {
    return this.request<{
      total: number;
      pending: number;
      in_progress: number;
      overdue: number;
      completed: number;
    }>('/maintenance/stats');
  }

  async createMaintenance(data: any) {
    return this.request<any>('/maintenance', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateMaintenance(id: number, data: any) {
    return this.request<any>(`/maintenance/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteMaintenance(id: number) {
    return this.request<void>(`/maintenance/${id}`, {
      method: 'DELETE',
    });
  }

  // Reports endpoints
  async generateReport(data: {
    report_type: string;
    format?: string;
    start?: string;
    end?: string;
    vehicle_ids?: number[];
    driver_ids?: number[];
    title?: string;
  }) {
    return this.request<{ id: string; status: string }>('/reports/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReportTemplates() {
    return this.request<{ templates: { key: string; name: string }[] }>('/reports/templates');
  }

  async downloadReport(id: string) {
    const token = this.getToken();
    const response = await fetch(`${this.baseUrl}/reports/${id}/download`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.blob();
  }

  // Alerts endpoints
  async getAlerts(params?: { page?: number; page_size?: number; vehicle_id?: number; severity?: string }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) queryParams.append(key, String(value));
      });
    }
    const query = queryParams.toString();
    return this.request<{ total: number; items: any[] }>(`/alerts${query ? `?${query}` : ''}`);
  }

  async acknowledgeAlert(id: number) {
    return this.request<{ status: string }>(`/alerts/${id}/ack`, { method: 'POST' });
  }

  // Analytics endpoints
  async getFleetOverview(params?: { start?: string; end?: string }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) queryParams.append(key, String(value));
      });
    }
    const query = queryParams.toString();
    return this.request<any>(`/analytics/fleet-overview${query ? `?${query}` : ''}`);
  }

  async getDriverRankings(params?: { start?: string; end?: string }) {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) queryParams.append(key, String(value));
      });
    }
    const query = queryParams.toString();
    return this.request<any>(`/analytics/driver-rankings${query ? `?${query}` : ''}`);
  }

  // Settings endpoints
  async getCompanySettings() {
    return this.request<{
      id: number;
      company_name: string;
      company_logo_url: string | null;
      timezone: string;
      currency: string;
    }>('/settings/company');
  }

  async updateSettings(data: {
    company_name?: string;
    company_logo_url?: string;
    timezone?: string;
    currency?: string;
    date_format?: string;
    speed_unit?: string;
    distance_unit?: string;
  }) {
    return this.request<any>('/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
