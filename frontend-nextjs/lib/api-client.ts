'use client';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}/api/v1${endpoint}`;

      const headers: Record<string, string> = { ...(options.headers as Record<string, string> ?? {}) };

      // Automatically attach the auth token to headers if it exists
      // Skip for login/register endpoints
      if (endpoint !== '/auth/login' && endpoint !== '/auth/register') {
        const token = localStorage.getItem("token");
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        } else {
          console.warn("No auth token found for request to", endpoint);
        }
      }

      // For FormData, the browser sets the Content-Type header automatically.
      // For other requests, we set it to application/json.
      if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
      }

      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle successful responses with no content (e.g., DELETE requests)
      if (response.status === 204) {
        return { success: true, data: undefined, message: "Operation successful" };
      }

      const responseData = await response.json();

      if (!response.ok) {
        // Use the 'detail' field from FastAPI's HTTPExceptions if available
        const errorMessage = responseData.detail || responseData.error || `API request failed with status ${response.status}`;
        throw new Error(errorMessage);
      }

      // The backend API returns the data directly. We wrap it in a consistent
      // ApiResponse format for the frontend.
      return { success: true, data: responseData, message: responseData.message };

    } catch (error) {
      console.error(`API Error at ${endpoint}:`, error);
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  // --- AUTH METHODS ---
  async login(credentials: { username: string; password: string }) {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: any) {
    return this.request("/users/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  }

  async getMe() {
    return this.request("/auth/me");
  }

  // --- USER JOURNEY METHODS ---
  async getProjects(limit: number = 10, offset: number = 0, status: string | null = null) {
    let url = `/projects?limit=${limit}&offset=${offset}`;
    if (status) {
      url += `&status=${status}`;
    }
    return this.request(url);
  }

  async getRecentActivity() {
    return this.request("/projects/recent-activity");
  }

  async uploadProject(projectName: string, files: File[]) {
    const formData = new FormData();
    formData.append("projectName", projectName);
    files.forEach((file) => {
      formData.append("files", file);
    });

    return this.request("/projects/upload", {
      method: "POST",
      body: formData,
    });
  }

  async getProjectStatus(projectId: string) {
    return this.request(`/projects/${projectId}/status`);
  }

  async getProjectPreview(projectId: string) {
    return this.request(`/projects/${projectId}/preview`);
  }

  async getAvailableFormats() {
    return this.request("/formats");
  }

  async startGeneration(projectId: string, formatIds: string[], prompt?: string) {
    return this.request("/generate", {
      method: "POST",
      body: JSON.stringify({ projectId, formatIds, customResizes: [], prompt }),
    });
  }

  async getGenerationStatus(jobId: string) {
    return this.request(`/generate/${jobId}/status`);
  }

  async getGenerationResults(jobId: string) {
    return this.request(`/generate/${jobId}/results`);
  }

  async getGeneratedAssets(originalAssetId: string) {
    return this.request(`/assets/${originalAssetId}/generated`);
  }

  async downloadAssets(assetIds: string[], format: string = 'jpeg', quality: string = 'high'): Promise<ApiResponse<null>> {
    const endpoint = "/generate/download";
    const url = `${this.baseUrl}/api/v1${endpoint}`;
    const token = localStorage.getItem("token");

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ assetIds, format, quality, grouping: 'individual' }),
      });

      const contentType = response.headers.get("content-type");
      if (!response.ok || (contentType && contentType.includes("application/json"))) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Download request failed or received unexpected JSON response.");
      }

      // Get the filename from the Content-Disposition header
      const disposition = response.headers.get('content-disposition');
      let filename = 'download.zip';
      if (disposition && disposition.indexOf('attachment') !== -1) {
        const filenameRegex = /filename[^;=\n\r]*=((['"])(.*?)\2|[^;\n\r]*)/;
        const matches = filenameRegex.exec(disposition);
        if (matches != null && matches[3]) {
          filename = matches[3];
        }
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);

      return { success: true };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      console.error(`API Error at ${endpoint}:`, errorMessage);
      return { success: false, error: errorMessage };
    }
  }

  // --- ADMIN METHODS ---
  async getUsers(limit: number = 10, offset: number = 0) {
    return this.request(`/users?limit=${limit}&offset=${offset}&t=${new Date().getTime()}`);
  }

  async createUser(userData: any) {
    return this.request("/users/", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId: string, userData: any) {
    return this.request(`/users/${userId}`, {
      method: "PUT",
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(userId: string) {
    return this.request(`/users/${userId}`, {
      method: "DELETE",
    });
  }

  async deactivateUser(userId: string) {
    return this.request(`/users/${userId}/deactivate`, {
      method: "PUT",
    });
  }

  async activateUser(userId: string) {
    return this.request(`/users/${userId}/activate`, {
      method: "PUT",
    });
  }

  async getPlatforms() {
    return this.request("/admin/platforms");
  }

  async createPlatform(data: any) {
    return this.request("/admin/platforms", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async deletePlatform(platformId: string) {
    return this.request(`/admin/platforms/${platformId}`, {
      method: "DELETE",
    });
  }

  async getAdminFormats() {
    return this.request("/admin/formats");
  }

  async createAdminFormat(data: any) {
    return this.request("/admin/formats", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateAdminFormat(formatId: string, data: any) {
    return this.request(`/admin/formats/${formatId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteAdminFormat(formatId: string) {
    return this.request(`/admin/formats/${formatId}`, {
      method: "DELETE",
    });
  }

  // --- Admin Rules ---
  async getAdaptationRules() {
    return this.request("/admin/rules/adaptation");
  }

  async updateAdaptationRules(data: any) {
    return this.request("/admin/rules/adaptation", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async getAiBehaviorRules() {
    return this.request("/admin/rules/ai-behavior");
  }

  async updateAiBehaviorRules(data: any) {
    return this.request("/admin/rules/ai-behavior", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async getUploadModerationRules() {
    return this.request("/admin/rules/upload-moderation");
  }

  async updateUploadModerationRules(data: any) {
    return this.request("/admin/rules/upload-moderation", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async getManualEditingRules() {
    return this.request("/admin/rules/manual-editing");
  }

  async updateManualEditingRules(data: any) {
    return this.request("/admin/rules/manual-editing", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // --- Admin Text Styles ---
  async getTextStyleSets() {
    return this.request("/admin/text-style-sets");
  }

  async createTextStyleSet(data: any) {
    return this.request("/admin/text-style-sets", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTextStyleSet(setId: string, data: any) {
    return this.request(`/admin/text-style-sets/${setId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteTextStyleSet(setId: string) {
    return this.request(`/admin/text-style-sets/${setId}`, {
      method: "DELETE",
    });
  }

  // --- Admin Dashboard ---
  async getAdminStats() {
    return this.request("/admin/stats");
  }

  async getCeleryWorkerStats() {
    return this.request("/monitoring/celery/workers");
  }

  async getSystemHealth() {
    return this.request("/monitoring/health-check");
  }

  // --- Admin Analytics ---
  async getUserGrowthAnalytics() {
    return this.request("/admin/analytics/user-growth");
  }

  async getProjectStatusAnalytics() {
    return this.request("/admin/analytics/project-status");
  }

  async getGenerationByFormatAnalytics() {
    return this.request("/admin/analytics/generation-by-format");
  }

  async updatePlatform(platformId: string, name: string) {
    return this.request(`/admin/platforms/${platformId}`, {
      method: "PUT",
      body: JSON.stringify({ name }),
    });
  }

  // --- Settings ---
  async getAiBehaviorSettings() {
    return this.request("/settings/rules/ai-behavior");
  }

  async getAdaptationSettings() {
    return this.request("/settings/rules/adaptation");
  }

  async getUploadModerationSettings() {
    return this.request("/settings/rules/upload-moderation");
  }

  async getTextStyleSetsSettings() {
    return this.request("/settings/text-style-sets");
  }

  async getEditingRules() {
    return this.request("/users/me/editing-rules");
  }

  async getPromptSuggestions(assetId: string) {
    return this.request(`/assets/${assetId}/prompt-suggestions`);
  }
}


export const apiClient = new ApiClient();