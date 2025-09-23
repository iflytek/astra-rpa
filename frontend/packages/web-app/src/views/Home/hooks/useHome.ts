import BUS from '@/utils/eventBus'

import { useFileLogModal } from '@/hooks/useFileLog'

export function useHome() {
  const { openFileLogModal } = useFileLogModal()
  BUS.$off('open-log-modal')
  BUS.$on('open-log-modal', openFileLogModal)
}
