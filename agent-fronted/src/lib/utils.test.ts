import { describe, it, expect } from 'vitest'
import { cn } from './utils'

describe('utils', () => {
  describe('cn', () => {
    it('should merge class names correctly', () => {
      expect(cn('c-red', 'c-blue')).toBe('c-red c-blue')
    })

    it('should handle conditional classes', () => {
      const isTrue = false
      expect(cn('c-red', isTrue && 'c-blue', 'c-green')).toBe('c-red c-green')
    })

    it('should merge tailwind classes', () => {
      expect(cn('p-2 p-4')).toBe('p-4')
    })
  })
})
