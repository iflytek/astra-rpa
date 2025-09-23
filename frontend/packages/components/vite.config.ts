import { resolve } from 'node:path'

import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import { defineConfig } from 'vite'

import pj from './package.json'

const external = [
  ...Object.keys(pj.dependencies),
  ...Object.keys(pj.peerDependencies),
  '@rpa/components/icon',
  '@rpa/tokens/dark',
]

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx()],
  build: {
    sourcemap: true,
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      formats: ['es'],
    },
    rollupOptions: {
      external,
      input: [resolve(__dirname, 'src/index.ts')],
      output: {
        format: 'es',
        exports: 'named',
        preserveModules: true,
        preserveModulesRoot: 'src',
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@rpa/tokens/variables.scss";`,
      },
    },
  },
})
