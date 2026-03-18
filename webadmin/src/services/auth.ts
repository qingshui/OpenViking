import apiClient, { handleAPI, APIResponse } from './api'

// User types
export interface User {
  uid: string
  username: string
  role: 'ROOT' | 'ADMIN' | 'USER'
  created_at?: string
}

export interface Account {
  id: string
  name: string
  users: User[]
}

export interface LoginRequest {
  apikey: string
}

export interface LoginResponse {
  success: boolean
  user?: User
  message?: string
}

// Authentication service
export const authService = {
  /**
   * Login with API key
   */
  login: async (apikey: string): Promise<LoginResponse> => {
    try {
      // Store API key
      localStorage.setItem('ov_api_key', apikey)

      // Verify API key by making a simple request
      const response = await handleAPI<any>(
        apiClient.get('/sessions')
      )

      if (response.success) {
        // Get user info from account API
        const accountsResponse = await handleAPI<Account[]>(
          apiClient.get('/admin/accounts')
        )

        if (accountsResponse.success && accountsResponse.data) {
          // Find current user based on API key
          // This is a simplified version - in production, you'd have a proper user endpoint
          const currentUser: User = {
            uid: 'current',
            username: 'user',
            role: 'USER'
          }
          localStorage.setItem('ov_username', currentUser.username)
          return {
            success: true,
            user: currentUser,
            message: 'Login successful'
          }
        }
      }

      return {
        success: false,
        message: response.error || 'Login failed'
      }
    } catch (error) {
      const apiError = error as APIResponse
      return {
        success: false,
        message: apiError.error || 'Login failed'
      }
    }
  },

  /**
   * Logout
   */
  logout: () => {
    localStorage.removeItem('ov_api_key')
    localStorage.removeItem('ov_username')
    window.location.href = '/login'
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('ov_api_key')
  },

  /**
   * Get current user info
   */
  getCurrentUser: (): User | null => {
    const username = localStorage.getItem('ov_username')
    if (!username) {
      return null
    }
    return {
      uid: 'current',
      username,
      role: 'USER'
    }
  },

  /**
   * Get API key
   */
  getAPIKey: (): string | null => {
    return localStorage.getItem('ov_api_key')
  },

  /**
   * List accounts (admin only)
   */
  listAccounts: async (): Promise<APIResponse<Account[]>> => {
    return handleAPI<Account[]>(
      apiClient.post('', {
        method: 'GET',
        path: '/api/v1/admin/accounts'
      })
    )
  },

  /**
   * Create account (admin only)
   */
  createAccount: async (name: string): Promise<APIResponse<string>> => {
    return handleAPI<string>(
      apiClient.post('', {
        method: 'POST',
        path: '/api/v1/admin/accounts',
        data: { name }
      })
    )
  },

  /**
   * Delete account (admin only)
   */
  deleteAccount: async (accountId: string): Promise<APIResponse<void>> => {
    return handleAPI<void>(
      apiClient.post('', {
        method: 'DELETE',
        path: `/api/v1/admin/accounts/${accountId}`
      })
    )
  },

  /**
   * Register user to account (admin only)
   */
  registerUser: async (
    accountId: string,
    username: string,
    role: 'ROOT' | 'ADMIN' | 'USER'
  ): Promise<APIResponse<string>> => {
    return handleAPI<string>(
      apiClient.post('', {
        method: 'POST',
        path: `/api/v1/admin/accounts/${accountId}/users`,
        data: { username, role }
      })
    )
  },

  /**
   * List users in account (admin only)
   */
  listUsers: async (accountId: string): Promise<APIResponse<User[]>> => {
    return handleAPI<User[]>(
      apiClient.post('', {
        method: 'GET',
        path: `/api/v1/admin/accounts/${accountId}/users`
      })
    )
  },

  /**
   * Reset user API key (admin only)
   */
  resetUserKey: async (
    accountId: string,
    uid: string
  ): Promise<APIResponse<string>> => {
    return handleAPI<string>(
      apiClient.post('', {
        method: 'POST',
        path: `/api/v1/admin/accounts/${accountId}/users/${uid}/key`
      })
    )
  },

  /**
   * Check user permissions
   */
  hasPermission: (requiredRole: 'ROOT' | 'ADMIN' | 'USER'): boolean => {
    const user = authService.getCurrentUser()
    if (!user) {
      return false
    }

    const roleHierarchy = { 'ROOT': 3, 'ADMIN': 2, 'USER': 1 }
    return roleHierarchy[user.role] >= roleHierarchy[requiredRole]
  }
}

export default authService
