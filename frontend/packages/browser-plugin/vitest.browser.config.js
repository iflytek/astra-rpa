import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['src/test/content.*.{test,spec}.js'],
    exclude: ['src/test/background.*.{test,spec}.js'],
    browser: {
      provider: 'playwright', // or 'webdriverio'
      enabled: true,
      // at least one instance is required
      instances: [{ browser: 'chromium' }],
    },
  },
})
