import StyleDictionary from 'style-dictionary'
import { formats, transformGroups, transformTypes } from 'style-dictionary/enums'

import { isDark } from './config/filter.js'
import { jsVarsPlugin, scssVarsPlugin, tailwindPreset } from './config/format.js'

const { value: transformTypeValue } = transformTypes

const pickDarkName = 'css/pick-dark'

// 自定义格式：生成引用 CSS 变量的 SCSS 变量
StyleDictionary.registerFormat({
  name: 'scss/variables-ref',
  format: scssVarsPlugin,
})

// 自定义格式：生成 less 变量的 js 文件
// StyleDictionary.registerFormat({
//   name: 'less/variables-esm',
//   format: lessVarsPlugin,
// })

// 自定义格式：生成 css 变量的 js 文件
StyleDictionary.registerFormat({
  name: 'javascript/css-variables',
  format: jsVarsPlugin,
})

StyleDictionary.registerTransform({
  name: pickDarkName,
  type: transformTypeValue,
  filter: isDark,
  transform: token => token.dark,
})

StyleDictionary.registerTransformGroup({
  name: 'tailwind',
  transforms: ['name/kebab', 'color/rgb'],
})

StyleDictionary.registerFormat({
  name: 'tailwind/preset',
  format: tailwindPreset,
})

const buildPath = 'dist/'

export default {
  source: [`tokens/**/*.js`],
  platforms: {
    'css': {
      transformGroup: transformGroups.css,
      buildPath,
      files: [
        {
          destination: 'variables.css',
          format: formats.cssVariables,
          options: { outputReferences: true },
        },
      ],
    },
    'css/variables-dark': {
      transformGroup: transformGroups.css,
      transforms: ['css/pick-dark'],
      buildPath,
      files: [
        {
          destination: 'variables.dark.css',
          format: formats.cssVariables,
          filter: token => token.dark,
          options: {
            outputReferences: true,
            showFileHeader: false,
            selector: '.dark',
          },
        },
      ],
    },
    'scss': {
      transformGroup: transformGroups.scss,
      buildPath,
      files: [
        {
          destination: 'variables.scss',
          format: 'scss/variables-ref',
          options: { outputReferences: true },
        },
      ],
    },
    'js': {
      transformGroup: transformGroups.js,
      buildPath,
      files: [
        {
          destination: 'variables.js',
          format: formats.javascriptEs6,
        },
        {
          destination: 'variables.cjs',
          format: formats.javascriptModuleFlat,
        },
        {
          destination: 'variables.css.js',
          format: 'javascript/css-variables',
        },
        {
          destination: 'variables.d.ts',
          format: formats.typescriptEs6Declarations,
        },
      ],
    },
    'js/variables-dark': {
      transformGroup: transformGroups.js,
      transforms: [pickDarkName],
      buildPath,
      files: [
        {
          destination: 'variables.dark.js',
          format: formats.javascriptEs6,
        },
        {
          destination: 'variables.dark.cjs',
          format: formats.javascriptModuleFlat,
        },
      ],
    },
    'tailwindPreset': {
      transformGroup: 'tailwind',
      buildPath,
      files: [
        {
          destination: 'tailwind-preset.js',
          format: 'tailwind/preset',
        },
      ],
    },
  },
}
