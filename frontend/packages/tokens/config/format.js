import { kebabCase } from 'lodash-es'
import { fileHeader } from 'style-dictionary/utils'

import { isColor } from './filter.js'

// 自定义格式：生成引用 CSS 变量的 SCSS 变量
export async function scssVarsPlugin({ dictionary, file }) {
  const header = await fileHeader({ file })
  const vars = dictionary.allTokens.map(prop => `$${prop.name}: var(--${prop.name});`).join('\n')
  return header + vars
}

export function lessVarsPlugin({ dictionary }) {
  const vars = Object.fromEntries(dictionary.allTokens.map(prop => ([`@${kebabCase(prop.name)}`, `var(--${kebabCase(prop.name)})`])))

  return `export default ${JSON.stringify(vars, null, 2)}`
}

export async function jsVarsPlugin({ dictionary, file }) {
  const header = await fileHeader({ file })
  const vars = dictionary.allTokens.map(prop => `export const ${prop.name} = "var(--${kebabCase(prop.name)})";`).join('\n')
  return header + vars
}

/**
 * Exports theme color definitions
 * @see https://tailwindcss.com/docs/customizing-colors#using-css-variables
 */
export function tailwindPreset({ dictionary, options }) {
  const tokens = dictionary.allTokens.filter(token => isColor(token, options))

  const defaultColors = {
    transparent: 'transparent',
    current: 'currentColor',
    inherit: 'inherit',
  }

  const defaultColorsText = Object.entries(defaultColors).map(([key, value]) => `\t\t\t'${key}': '${value}',\n`).join('')

  const theme = tokens
    .map((token) => {
      // 如果以 color- 开头，则去掉 color-
      const name = token.name.startsWith('color-') ? token.name.slice(6) : token.name
      return `\t\t\t'${name}': 'var(--${token.name})'`
    })
    .join(',\n')

  return `
/** @type {import('tailwindcss').Config} */
export default {
\ttheme: {
\t\tcolors: {
${defaultColorsText}
${theme}
\t\t},
\t},
};\n`
}
