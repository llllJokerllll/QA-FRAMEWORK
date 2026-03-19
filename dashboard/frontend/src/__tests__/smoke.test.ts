import { describe, it, expect } from 'vitest'

describe('Smoke tests', () => {
  it('true is true', () => {
    expect(true).toBe(true)
  })

  it('1 + 1 equals 2', () => {
    expect(1 + 1).toBe(2)
  })

  it('App module can be imported', async () => {
    const result = await import('../App')
    expect(result.default).toBeDefined()
  }, 15000)
})
