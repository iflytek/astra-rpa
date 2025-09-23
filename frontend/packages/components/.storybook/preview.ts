import {
  DecoratorHelpers,
  withThemeByClassName,
} from '@storybook/addon-themes'
import type { Preview } from '@storybook/vue3-vite'
import { ConfigProvider } from 'ant-design-vue'
import { computed, ref } from 'vue'

import { getAntdvTheme } from '../src'
import type { Theme } from '../src'
import '@rpa/tokens/variables.css'
import './preview.css'

const { initializeThemeState, pluckThemeFromContext } = DecoratorHelpers

initializeThemeState(['dark', 'light'], 'light')

const themeRef = ref('light')

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  decorators: [
    withThemeByClassName({
      themes: {
        light: 'light',
        dark: 'dark',
      },
      defaultTheme: 'light',
    }),
    (story, context) => {
      const { themeOverride } = context.parameters.themes ?? {}
      const selectedTheme = pluckThemeFromContext(context)
      themeRef.value = themeOverride || selectedTheme

      return {
        components: { story, ConfigProvider },
        setup() {
          const antdvTheme = computed(() =>
            getAntdvTheme(themeRef.value as Theme),
          )
          return { antdvTheme }
        },
        template:
          '<ConfigProvider :theme="antdvTheme" :key="theme"><story /></ConfigProvider>',
      }
    },
  ],
}

export default preview
