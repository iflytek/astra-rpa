/** @format */
import { readFileSync, writeFileSync } from 'node:fs'

export function generateManifest(mode: string, environment) {
  console.log('Generating manifest.json...')
  const packageJson = readFileSync('./package.json', 'utf-8')
  const { version } = JSON.parse(packageJson)
  const isFirefox = mode === 'firefox'
  const appName = environment.VITE_APP_NAME
  const appDescription = environment.VITE_APP_NAME
  const appHomePage = environment.VITE_APP_HOMEPAGE
  let manifest = {
    manifest_version: 3,
    name: appName,
    description: mode !== 'production' ? `${appDescription}-${mode}` : appDescription,
    homepage_url: appHomePage,
    version,
    icons: {
      16: 'static/icon_16.png',
      48: 'static/icon_48.png',
      128: 'static/icon_128.png',
    },
    background: {
      service_worker: 'background.js',
      type: 'module',
    },

    host_permissions: ['<all_urls>'],
    content_scripts: [
      {
        all_frames: true,
        matches: ['http://*/*', 'https://*/*', 'file://*/*', 'ftp://*/*'],
        js: ['content.js'],
        css: ['rpa.css'],
        run_at: 'document_start',
        match_about_blank: false,
        world: 'ISOLATED',
      },
    ],
    content_security_policy: {
      extension_pages: 'script-src \'self\'; object-src \'self\';',
      sandbox: 'sandbox allow-scripts allow-forms allow-popups allow-modals; script-src \'self\' \'unsafe-inline\' \'unsafe-eval\'; child-src \'self\';',
    },
    permissions: [
      'nativeMessaging',
      'debugger',
      'tabs',
      'activeTab',
      'contextMenus',
      'webNavigation',
      'cookies',
      'storage',
      'notifications',
      'tabCapture',
      'scripting',
      'userScripts',
      'management',
    ],
  }

  if (isFirefox) {
    const permission = manifest.permissions.filter(item => item !== 'debugger')
    const manifestFirefox = {
      manifest_version: 2,
      background: {
        scripts: ['background.js'],
      },
      description: `${appDescription}-Firefox`,
      content_security_policy: 'script-src \'none\' \'unsafe-eval\';',
      browser_specific_settings: {
        gecko: {
          id: environment.VITE_FIREFOXID,
          strict_min_version: '58.0',
        },
      },
      permissions: [...permission, '<all_urls>'],
    }
    // @ts-expect-error firefox specific
    manifest = { ...manifest, ...manifestFirefox }
  }

  writeFileSync('./public/manifest.json', JSON.stringify(manifest, null, 2))
  console.log('manifest.json generated successfully.')
}
