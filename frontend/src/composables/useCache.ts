interface CacheEntry<T> {
  value: T
  expiresAt: number
}

const store = new Map<string, CacheEntry<unknown>>()

export function useCache() {
  function get<T>(key: string): T | null {
    const entry = store.get(key) as CacheEntry<T> | undefined
    if (!entry) return null
    if (Date.now() > entry.expiresAt) {
      store.delete(key)
      return null
    }
    return entry.value
  }

  function set<T>(key: string, value: T, ttlSeconds: number): void {
    store.set(key, { value, expiresAt: Date.now() + ttlSeconds * 1000 })
  }

  function invalidate(key: string): void {
    store.delete(key)
  }

  function invalidatePrefix(prefix: string): void {
    for (const key of store.keys()) {
      if (key.startsWith(prefix)) store.delete(key)
    }
  }

  return { get, set, invalidate, invalidatePrefix }
}
