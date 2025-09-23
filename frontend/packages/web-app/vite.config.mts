import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { RpaResolver } from '@rpa/components/resolver'
import { sentryVitePlugin } from '@sentry/vite-plugin'
import type { SentryVitePluginOptions } from '@sentry/vite-plugin'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
// import Inspect from 'vite-plugin-inspect' 开发时查看编译代码
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers'
import Components from 'unplugin-vue-components/vite'
import { defineConfig } from 'vite'
import { analyzer } from 'vite-bundle-analyzer'
import { lazyImport, VxeResolver } from 'vite-plugin-lazy-import'

import { ModalReplacementResolver } from './src/plugins/component-resolver'

const baseSrc = fileURLToPath(new URL('./src', import.meta.url))
const basePublic = fileURLToPath(new URL('../../public', import.meta.url))
const nodeModules = fileURLToPath(new URL('./node_modules', import.meta.url))

const sentryConfig: SentryVitePluginOptions = {
  authToken: process.env.SENTRY_AUTH_TOKEN,
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,
  url: process.env.SENTRY_URL,
}

// https://vitejs.dev/config/
export default defineConfig((env) => {
  const isServe = env.command === 'serve'
  const isPublish = env.mode === 'publish'
  const isDebug = env.mode === 'debug'

  const enableAnalyze = env.mode === 'analyze'
  const enableSentry = isPublish && sentryConfig.authToken && sentryConfig.org && sentryConfig.project

  return {
    publicDir: basePublic,
    base: isServe ? '/' : './',
    build: {
      sourcemap: isDebug ? 'inline' : isPublish,
      rollupOptions: {
        input: {
          index: './index.html',
          404: './404.html',
          logwin: './logwin.html',
          batch: './batch.html',
          multichat: './multichat.html',
          userform: './userform.html',
          record: './record.html',
          recordmenu: './recordmenu.html',
        },
      },
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: isPublish,
          drop_debugger: true,
        },
      },
    },
    plugins: [
      vue(),
      vueJsx(),
      // Inspect(),
      Components({
        dirs: [],
        dts: './src/components.d.ts',
        resolvers: [
          ModalReplacementResolver(), // 优先级最高，用于替换 a-modal
          AntDesignVueResolver({
            importStyle: false, // css in js
          }),
          RpaResolver(),
        ],
      }),
      lazyImport({
        resolvers: [
          VxeResolver({
            libraryName: 'vxe-table',
          }),
          VxeResolver({
            libraryName: 'vxe-pc-ui',
          }),
        ],
      }),
      {
        name: 'client-sdk-inject',
        transformIndexHtml(html) {
          // 找到head 标签，并在其后插入<script>标签, 不区分环境
          return html.replace(
            /<head>/,
            `<head>
              <script src="client-sdk.js"></script>`,
          )
        },
      },
      enableSentry ? sentryVitePlugin(sentryConfig) : null,
      enableAnalyze ? analyzer() : null,
    ],
    resolve: {
      alias: [
        {
          find: '@',
          replacement: baseSrc,
        },
        {
          find: 'dayjs',
          replacement: 'dayjs/esm',
        },
        {
          find: /^dayjs\/locale/,
          replacement: 'dayjs/esm/locale',
        },
        {
          find: /^dayjs\/plugin/,
          replacement: 'dayjs/esm/plugin',
        },
        {
          find: /^ant-design-vue\/es$/,
          replacement: resolve(nodeModules, 'ant-design-vue/es'),
        },
        {
          find: /^ant-design-vue\/dist$/,
          replacement: resolve(nodeModules, 'ant-design-vue/dist'),
        },
        {
          find: /^ant-design-vue\/lib$/,
          replacement: resolve(nodeModules, 'ant-design-vue/es'),
        },
        {
          find: /^ant-design-vue$/,
          replacement: resolve(nodeModules, 'ant-design-vue/es'),
        },
        {
          find: 'lodash',
          replacement: 'lodash-es',
        },
      ],
    },

    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @import "@rpa/tokens/variables.scss";
          `,
        },
      },
    },

    clearScreen: false,
    server: {
      port: 1420,
      strictPort: true,
      host: '0.0.0.0', // 指定监听所有网络接口
      watch: {
        // 3. tell vite to ignore watching `src-tauri`
        ignored: ['**/src-tauri/**', '**/node_modules/**', '**/src-electron/**', '**/dist/**', '**/dist-electron/**'],
      },
    },
  }
})
