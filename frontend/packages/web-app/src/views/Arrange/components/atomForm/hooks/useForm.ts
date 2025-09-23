import { computed } from 'vue'
import type { Ref } from 'vue'

let showFormRef: Ref<boolean>

function useShowAtomForm(atomFormRef: any) {
  showFormRef = atomFormRef

  return computed(() => atomFormRef.value)
}

function toggleAtomForm(show?: boolean) {
  if (show === undefined) {
    return showFormRef.value = !showFormRef.value
  }
  showFormRef.value = show
}

export {
  toggleAtomForm,
  useShowAtomForm,
}
