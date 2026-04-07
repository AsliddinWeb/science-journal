import { onUnmounted } from 'vue'

const SCRIPT_ID = 'json-ld-schema'

export function useJsonLd() {
  function inject(schema: object | object[]) {
    remove()
    const schemas = Array.isArray(schema) ? schema : [schema]
    schemas.forEach((s, i) => {
      const el = document.createElement('script')
      el.type = 'application/ld+json'
      el.id = i === 0 ? SCRIPT_ID : `${SCRIPT_ID}-${i}`
      el.textContent = JSON.stringify(s, null, 0)
      document.head.appendChild(el)
    })
  }

  function remove() {
    document.querySelectorAll(`script[id^="${SCRIPT_ID}"]`).forEach((el) => el.remove())
  }

  onUnmounted(remove)

  return { inject, remove }
}
