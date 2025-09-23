import type { RuleObject } from 'ant-design-vue/es/form'
import type { i18n, Namespace, TFunction } from 'i18next'

export interface AnyObj {
  [key: string]: any
}

export interface ArrObj {
  [key: string]: any[]
}

export interface FunObj {
  [key: string]: (...args: any[]) => any
}

export type Fun = (args?: any) => any

export interface LangTranslate {
  i18next: i18n
  t: TFunction<Namespace, undefined>
}

export interface instanceComponent {
  show: () => void
  remove: () => void
}

export type FormRules = Record<string, RuleObject[]>
