import type { AllowedComponentProps, Component, VNodeProps } from 'vue'

export interface NiceModalHocProps {
  id: string
}

export type ComponentWithModalId = Component & { [NICE_MODAL_ID_KEY]?: string }

export type Simplify<T> = T extends any ? { [P in keyof T]: T[P] } : never

export type ComponentProps<C extends Component> = C extends new (...args: any) => any
  ? Omit<
    InstanceType<C>['$props'],
      keyof VNodeProps | keyof AllowedComponentProps
  >
  : never

export type RemoveReadonly<T> = { -readonly [P in keyof T]: T[P] }

export const MODAL_REGISTRY: Record<string, { comp: Component, props: Partial<NiceModalHocProps> }> = {}
export const ALREADY_MOUNTED: Record<string, boolean> = {}

// Symbol for modal ID
export const NICE_MODAL_ID_KEY = Symbol('NiceModalId')

// Modal callbacks store
export const modalCallbacks: Record<string, ReturnType<typeof Promise.withResolvers>> = {}
export const hideModalCallbacks: Record<string, ReturnType<typeof Promise.withResolvers>> = {}
