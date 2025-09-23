import antfu from '@antfu/eslint-config'

export default antfu({
  stylistic: {
    indent: 2, // 4, or 'tab'
    quotes: 'single', // or 'double'
  },
  formatters: {
    css: true,
    html: true,
    markdown: true,
    prettierOptions: {
      htmlWhitespaceSensitivity: 'ignore',
      bracketSameLine: false,
    },
  },
  typescript: true,
  vue: true,
  rules: {
    'vue/no-mutating-props': 'off',
    'vue/no-unused-refs': 'off',
    'vue/no-deprecated-slot-attribute': 'off',
    'vue/require-v-for-key': 'off',
    'vue/custom-event-name-casing': 'off',
    'no-console': 'off',
    'ts/no-unused-expressions': 'off',
    'ts/no-require-imports': 'off',
    'eslint-comments/no-unlimited-disable': 'off',
    'jsonc/sort-keys': 'off',
    'regexp/no-unused-capturing-group': 'off',
    'style/max-statements-per-line': 'off',
    'node/prefer-global/process': 'off',
    'regexp/no-super-linear-backtracking': 'off',
    'ts/no-use-before-define': 'off',
    'no-control-regex': 'off',
    'import/no-self-import': 'off',
    'perfectionist/sort-imports': [
      'error',
      {
        type: 'alphabetical',
        order: 'asc',
        ignoreCase: true,
        internalPattern: ['^~/.+', '^@/.+'],
        newlinesBetween: 1,
        groups: [
          'type-import',
          'builtin',
          'external',
          'styles',
          'plugins',
          'utils',
          'internal',
          'parent',
          'sibling',
          'index',
          'unknown',
        ],
        customGroups: [
          {
            groupName: 'styles',
            elementNamePattern: '.*\\.(css|scss)$',
          },
          {
            groupName: 'utils',
            elementNamePattern: '^@/utils/.*',
          },
          {
            groupName: 'plugins',
            elementNamePattern: '^@/plugins/.*',
          },
        ],
      },
    ],
    'unicorn/prefer-dom-node-text-content': 'off',
  },
  ignores: [
    'packages/electron-app/resources/**/*.js',
    'packages/components/lib/**/*.js',
    'public/*.js',
    'packages/browser-plugin/src/3rd/*.js',
    'packages/browser-plugin/src/test/*.js',
  ],
})
