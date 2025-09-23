/**
 * 权限工具测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { PermissionValidator, PERMISSIONS, ROLES, hasPermission, hasRole, isAdmin } from '../permission'

// Mock user store
const mockUserStore = {
  isLoggedIn: true,
  userInfo: { id: 1, username: 'testuser' },
  hasPermission: vi.fn(),
  hasRole: vi.fn()
}

vi.mock('@/store', () => ({
  useUserStore: () => mockUserStore
}))

describe('PermissionValidator', () => {
  let validator: PermissionValidator

  beforeEach(() => {
    vi.clearAllMocks()
    validator = new PermissionValidator()
  })

  describe('hasPermission', () => {
    it('should return false when user is not logged in', () => {
      mockUserStore.isLoggedIn = false
      
      const result = validator.hasPermission(PERMISSIONS.USER_VIEW)
      
      expect(result).toBe(false)
    })

    it('should return true for super admin', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.SUPER_ADMIN)
      
      const result = validator.hasPermission(PERMISSIONS.USER_DELETE)
      
      expect(result).toBe(true)
    })

    it('should check user permission when not super admin', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(true)
      
      const result = validator.hasPermission(PERMISSIONS.USER_VIEW)
      
      expect(result).toBe(true)
      expect(mockUserStore.hasPermission).toHaveBeenCalledWith(PERMISSIONS.USER_VIEW)
    })

    it('should return false when user lacks permission', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(false)
      
      const result = validator.hasPermission(PERMISSIONS.USER_DELETE)
      
      expect(result).toBe(false)
    })
  })

  describe('hasAnyPermission', () => {
    it('should return true if user has any of the permissions', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockImplementation((perm: string) => 
        perm === PERMISSIONS.USER_VIEW
      )
      
      const result = validator.hasAnyPermission([
        PERMISSIONS.USER_VIEW,
        PERMISSIONS.USER_DELETE
      ])
      
      expect(result).toBe(true)
    })

    it('should return false if user has none of the permissions', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(false)
      
      const result = validator.hasAnyPermission([
        PERMISSIONS.USER_VIEW,
        PERMISSIONS.USER_DELETE
      ])
      
      expect(result).toBe(false)
    })
  })

  describe('hasAllPermissions', () => {
    it('should return true if user has all permissions', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(true)
      
      const result = validator.hasAllPermissions([
        PERMISSIONS.USER_VIEW,
        PERMISSIONS.USER_CREATE
      ])
      
      expect(result).toBe(true)
    })

    it('should return false if user lacks any permission', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockImplementation((perm: string) => 
        perm === PERMISSIONS.USER_VIEW
      )
      
      const result = validator.hasAllPermissions([
        PERMISSIONS.USER_VIEW,
        PERMISSIONS.USER_DELETE
      ])
      
      expect(result).toBe(false)
    })
  })

  describe('hasRole', () => {
    it('should return false when user is not logged in', () => {
      mockUserStore.isLoggedIn = false
      
      const result = validator.hasRole(ROLES.ADMIN)
      
      expect(result).toBe(false)
    })

    it('should check user role when logged in', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(true)
      
      const result = validator.hasRole(ROLES.ADMIN)
      
      expect(result).toBe(true)
      expect(mockUserStore.hasRole).toHaveBeenCalledWith(ROLES.ADMIN)
    })
  })

  describe('hasAnyRole', () => {
    it('should return true if user has any of the roles', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.USER)
      
      const result = validator.hasAnyRole([ROLES.ADMIN, ROLES.USER])
      
      expect(result).toBe(true)
    })

    it('should return false if user has none of the roles', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      
      const result = validator.hasAnyRole([ROLES.ADMIN, ROLES.SUPER_ADMIN])
      
      expect(result).toBe(false)
    })
  })

  describe('isAdmin', () => {
    it('should return true for admin role', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.ADMIN)
      
      const result = validator.isAdmin()
      
      expect(result).toBe(true)
    })

    it('should return true for super admin role', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.SUPER_ADMIN)
      
      const result = validator.isAdmin()
      
      expect(result).toBe(true)
    })

    it('should return false for regular user', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.USER)
      
      const result = validator.isAdmin()
      
      expect(result).toBe(false)
    })
  })

  describe('isSuperAdmin', () => {
    it('should return true for super admin', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.SUPER_ADMIN)
      
      const result = validator.isSuperAdmin()
      
      expect(result).toBe(true)
    })

    it('should return false for regular admin', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.ADMIN)
      
      const result = validator.isSuperAdmin()
      
      expect(result).toBe(false)
    })
  })

  describe('canAccessRoute', () => {
    it('should return true for routes without special requirements', () => {
      const result = validator.canAccessRoute('/dashboard')
      
      expect(result).toBe(true)
    })

    it('should check permissions for protected routes', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockImplementation((perm: string) => 
        perm === PERMISSIONS.USER_VIEW
      )
      
      const result = validator.canAccessRoute('/system/user')
      
      expect(result).toBe(true)
    })

    it('should deny access when lacking permissions', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(false)
      
      const result = validator.canAccessRoute('/system/user')
      
      expect(result).toBe(false)
    })
  })

  describe('canPerformAction', () => {
    it('should allow create action with proper permissions', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockImplementation((perm: string) => 
        perm === PERMISSIONS.USER_CREATE
      )
      
      const result = validator.canPerformAction('create')
      
      expect(result).toBe(true)
    })

    it('should allow update own resource', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.userInfo = { id: 1, username: 'testuser' }
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(false)
      
      const resource = { userId: 1 }
      const result = validator.canPerformAction('update', resource)
      
      expect(result).toBe(true)
    })

    it('should deny update others resource without permission', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.userInfo = { id: 1, username: 'testuser' }
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(false)
      
      const resource = { userId: 2 }
      const result = validator.canPerformAction('update', resource)
      
      expect(result).toBe(false)
    })

    it('should allow system view with proper permission', () => {
      mockUserStore.isLoggedIn = true
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockImplementation((perm: string) => 
        perm === PERMISSIONS.SYSTEM_VIEW
      )
      
      const result = validator.canPerformAction('view_system')
      
      expect(result).toBe(true)
    })

    it('should return true for unknown actions', () => {
      const result = validator.canPerformAction('unknown_action')
      
      expect(result).toBe(true)
    })
  })
})

describe('convenience functions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUserStore.isLoggedIn = true
  })

  describe('hasPermission', () => {
    it('should work as convenience function', () => {
      mockUserStore.hasRole.mockReturnValue(false)
      mockUserStore.hasPermission.mockReturnValue(true)
      
      const result = hasPermission(PERMISSIONS.USER_VIEW)
      
      expect(result).toBe(true)
    })
  })

  describe('hasRole', () => {
    it('should work as convenience function', () => {
      mockUserStore.hasRole.mockReturnValue(true)
      
      const result = hasRole(ROLES.ADMIN)
      
      expect(result).toBe(true)
    })
  })

  describe('isAdmin', () => {
    it('should work as convenience function', () => {
      mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.ADMIN)
      
      const result = isAdmin()
      
      expect(result).toBe(true)
    })
  })
})

describe('checkRoutePermission', () => {
  const { checkRoutePermission } = require('../permission')

  beforeEach(() => {
    vi.clearAllMocks()
    mockUserStore.isLoggedIn = true
  })

  it('should allow access to public routes', () => {
    const route = {
      meta: { requiresAuth: false }
    }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(true)
  })

  it('should deny access when not logged in', () => {
    mockUserStore.isLoggedIn = false
    
    const route = {
      meta: { requiresAuth: true }
    }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(false)
  })

  it('should check single permission', () => {
    mockUserStore.hasRole.mockReturnValue(false)
    mockUserStore.hasPermission.mockReturnValue(true)
    
    const route = {
      meta: { permission: PERMISSIONS.USER_VIEW }
    }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(true)
  })

  it('should check multiple permissions', () => {
    mockUserStore.hasRole.mockReturnValue(false)
    mockUserStore.hasPermission.mockImplementation((perm: string) => 
      perm === PERMISSIONS.USER_VIEW
    )
    
    const route = {
      meta: { permission: [PERMISSIONS.USER_VIEW, PERMISSIONS.USER_DELETE] }
    }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(true)
  })

  it('should check single role', () => {
    mockUserStore.hasRole.mockReturnValue(true)
    
    const route = {
      meta: { roles: ROLES.ADMIN }
    }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(true)
  })

  it('should check multiple roles', () => {
    mockUserStore.hasRole.mockImplementation((role: string) => role === ROLES.USER)
    
    const route = {
      meta: { roles: [ROLES.ADMIN, ROLES.USER] }
    }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(true)
  })

  it('should return true for routes without special requirements', () => {
    const route = { meta: {} }
    
    const result = checkRoutePermission(route)
    
    expect(result).toBe(true)
  })
})

describe('PERMISSIONS and ROLES constants', () => {
  it('should have correct permission constants', () => {
    expect(PERMISSIONS.USER_VIEW).toBe('user:view')
    expect(PERMISSIONS.USER_CREATE).toBe('user:create')
    expect(PERMISSIONS.USER_UPDATE).toBe('user:update')
    expect(PERMISSIONS.USER_DELETE).toBe('user:delete')
    expect(PERMISSIONS.AGENT_VIEW).toBe('agent:view')
    expect(PERMISSIONS.TEST_CASE_VIEW).toBe('test_case:view')
  })

  it('should have correct role constants', () => {
    expect(ROLES.SUPER_ADMIN).toBe('super_admin')
    expect(ROLES.ADMIN).toBe('admin')
    expect(ROLES.USER).toBe('user')
    expect(ROLES.GUEST).toBe('guest')
  })
})
