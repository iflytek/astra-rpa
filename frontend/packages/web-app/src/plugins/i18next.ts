import i18next from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import I18NextVue from 'i18next-vue'
import { get, hasIn, isEmpty, isObject, isString, template } from 'lodash-es'
import type { App } from 'vue'

import locales from '@/constants/i18n'

export interface LanguageType {
  'zh-CN': string
  'en-US': string
}

const resources = locales.reduce((acc, locale) => {
  acc[locale.lng] = {
    translation: locale.value,
  }
  return acc
}, {})

i18next.use(LanguageDetector).init({
  debug: false,
  fallbackLng: 'zh-CN',
  supportedLngs: locales.map(locale => locale.lng),
  resources,
  interpolation: {
    escapeValue: false,
  },
})

export function isI18n(str: unknown): str is LanguageType {
  return isObject(str) && hasIn(str, 'zh-CN') && hasIn(str, 'en-US')
}

export function translate(str: string | LanguageType, variables?: Record<string, string>): string {
  if (isString(str))
    return str

  if (isI18n(str)) {
    const text = get(str, i18next.language)

    if (isEmpty(variables))
      return text

    const compiled = template(text, { interpolate: /\{\{([\s\S]+?)\}\}/g })
    return compiled(variables)
  }

  return ''
}

function install(app: App<Element>) {
  app.use(I18NextVue, { i18next })
}

export default Object.assign(i18next, { isI18n, translate, install })
