import type {
  CompletionItem,
  CompletionList,
  Diagnostic,
  Position,
  Range,
  SignatureHelp,
  WorkspaceEdit,
} from 'vscode-languageserver-types'

import { endpointDelete, endpointPost } from './EndpointUtils'
import type { EditorSettings } from './Settings'

export interface HoverInfo {
  contents: {
    kind: string
    value: string
  }
  range: Range
}

// Number of attempts to create a new session before giving up.
const maxErrorCount = 4

export class LspSession {
  private _sessionId?: string
  private _settings?: EditorSettings
  private _initialCode = ''
  private _appServerApiAddressPrefix = 'https://pyright-playground.azurewebsites.net/api/'

  constructor(baseUrl?: string) {
    if (baseUrl) {
      this._appServerApiAddressPrefix = `${baseUrl}/lsp/`
    }
  }

  updateSettings(settings: EditorSettings) {
    this._settings = settings

    // Force the current session to close so we can
    // create a new one with the updated settings.
    this._closeSession()
  }

  updateInitialCode(text: string) {
    // When creating a new session, we can send the initial
    // code to the server to speed up initialization.
    this._initialCode = text
  }

  async getDiagnostics(code: string): Promise<Diagnostic[]> {
    return this._doWithSession<Diagnostic[]>(async (sessionId) => {
      const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}/diagnostics`
      return endpointPost(endpoint, {}, JSON.stringify({ code }))
        .then(async (response) => {
          const data = await response.json()
          if (!response.ok) {
            throw data
          }
          return data.diagnostics
        })
        .catch((err) => {
          throw err
        })
    })
  }

  async getHoverForPosition(code: string, position: Position): Promise<HoverInfo | undefined> {
    return this._doWithSession<HoverInfo>(async (sessionId) => {
      const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}/hover`
      return endpointPost(endpoint, {}, JSON.stringify({ code, position }))
        .then(async (response) => {
          const data = await response.json()
          if (!response.ok) {
            throw data
          }
          return data.hover
        })
        .catch((err) => {
          throw err
        })
    })
  }

  async getRenameEditsForPosition(
    code: string,
    position: Position,
    newName: string,
  ): Promise<WorkspaceEdit | undefined> {
    return this._doWithSession<WorkspaceEdit>(async (sessionId) => {
      const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}/rename`
      return endpointPost(endpoint, {}, JSON.stringify({ code, position, newName }))
        .then(async (response) => {
          const data = await response.json()
          if (!response.ok) {
            throw data
          }
          return data.edits
        })
        .catch((err) => {
          throw err
        })
    })
  }

  async getSignatureHelpForPosition(
    code: string,
    position: Position,
  ): Promise<SignatureHelp | undefined> {
    return this._doWithSession<SignatureHelp>(async (sessionId) => {
      const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}/signature`
      return endpointPost(endpoint, {}, JSON.stringify({ code, position }))
        .then(async (response) => {
          const data = await response.json()
          if (!response.ok) {
            throw data
          }
          return data.signatureHelp
        })
        .catch((err) => {
          throw err
        })
    })
  }

  async getCompletionForPosition(
    code: string,
    position: Position,
  ): Promise<CompletionList | undefined> {
    return this._doWithSession<CompletionList>(async (sessionId) => {
      const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}/completion`
      return endpointPost(endpoint, {}, JSON.stringify({ code, position }))
        .then(async (response) => {
          const data = await response.json()
          if (!response.ok) {
            throw data
          }
          return data.completionList
        })
        .catch((err) => {
          throw err
        })
    })
  }

  async resolveCompletionItem(item: CompletionItem): Promise<CompletionItem | undefined> {
    return this._doWithSession<CompletionItem>(async (sessionId) => {
      const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}/completionresolve`
      return endpointPost(endpoint, {}, JSON.stringify({ completionItem: item }))
        .then(async (response) => {
          const data = await response.json()
          if (!response.ok) {
            throw data
          }
          return data.completionItem
        })
        .catch((err) => {
          throw err
        })
    })
  }

  // Establishes a session if necessary and calls the callback to perform some
  // work. If the session cannot be established or the call fails, an attempt
  // is made to retry the operation with exponential backoff.
  private async _doWithSession<T>(callback: (sessionId: string) => Promise<T>): Promise<T> {
    let errorCount = 0
    let backoffDelay = 100

    while (true) {
      if (errorCount > maxErrorCount) {
        throw new Error('Could not connect to service')
      }

      try {
        const sessionId = await this._createSession()
        const result = await callback(sessionId)

        return result
      }
      catch {
        // Throw away the current session.
        this._sessionId = undefined
        errorCount++
      }

      await this._sleep(backoffDelay)

      // Exponentially back off.
      backoffDelay *= 2
    }
  }

  private _sleep(sleepTimeInMs: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, sleepTimeInMs))
  }

  private async _createSession(): Promise<string> {
    // If there's already a valid session ID, use it.
    if (this._sessionId) {
      return Promise.resolve(this._sessionId)
    }

    const sessionOptions: any = {}
    if (this._settings) {
      if (this._settings.strictMode) {
        sessionOptions.type_checking_mode = 'strict'
      }

      sessionOptions.code = this._initialCode
      sessionOptions.config_overrides = { ...this._settings.configOverrides }
      sessionOptions.locale = this._settings.locale ?? navigator.language
      sessionOptions.project_id = this._settings.projectId
    }

    const endpoint = `${this._appServerApiAddressPrefix}session`
    const sessionId = await endpointPost(endpoint, {}, JSON.stringify(sessionOptions)).then(
      async (response) => {
        const data = await response.json()
        if (!response.ok) {
          throw data
        }
        return data.sessionId
      },
    )

    this._sessionId = sessionId
    return sessionId
  }

  private async _closeSession(): Promise<void> {
    const sessionId = this._sessionId
    if (!sessionId) {
      return
    }

    // Immediately discard the old session ID.
    this._sessionId = undefined

    const endpoint = `${this._appServerApiAddressPrefix}session/${sessionId}`
    await endpointDelete(endpoint, {})
  }
}
