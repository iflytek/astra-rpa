import type {
  CompletionItem,
  CompletionList,
  Diagnostic,
  Position,
  SignatureHelp,
  WorkspaceEdit,
} from 'vscode-languageserver-types'

import type { HoverInfo } from './LspSession'
import { LspSession } from './LspSession'
import type { EditorSettings } from './Settings'

// Wait for a small amount before sending the request to the server. This allows
// the user to type multiple characters before we send the request.
const diagnosticDelayInMs = 500

export interface LspClientNotifications {
  onWaitingForDiagnostics?: (isWaiting: boolean) => void
  onDiagnostics?: (diag: Diagnostic[]) => void
  onError?: (message: string) => void
}

export class LspClient {
  private _lspSession: LspSession
  private _docContent = ''
  private _docVersion = 0
  private _diagnosticsTimer: any
  private _notifications: LspClientNotifications = {}

  constructor(code: string, baseUrl?: string) {
    this._lspSession = new LspSession(baseUrl)
    this.updateCode(code)
  }

  requestNotification(notifications: LspClientNotifications) {
    this._notifications = notifications
  }

  // Updates the code and queues the change to be sent to the language server.
  updateCode(content: string) {
    if (content !== this._docContent) {
      this._docContent = content
      this._docVersion++
      this._lspSession.updateInitialCode(content)
      this._restartDiagnosticsTimer()
    }
  }

  updateSettings(settings: EditorSettings) {
    this._lspSession.updateSettings(settings)
    this._restartDiagnosticsTimer()
  }

  async getHoverForPosition(code: string, position: Position): Promise<HoverInfo | undefined> {
    return this._lspSession.getHoverForPosition(code, position)
  }

  async getRenameEditsForPosition(
    code: string,
    position: Position,
    newName: string,
  ): Promise<WorkspaceEdit | undefined> {
    return this._lspSession.getRenameEditsForPosition(code, position, newName)
  }

  async getSignatureHelpForPosition(
    code: string,
    position: Position,
  ): Promise<SignatureHelp | undefined> {
    return this._lspSession.getSignatureHelpForPosition(code, position)
  }

  async getCompletionForPosition(
    code: string,
    position: Position,
  ): Promise<CompletionList | undefined> {
    return this._lspSession.getCompletionForPosition(code, position)
  }

  async resolveCompletionItem(
    completionItem: CompletionItem,
  ): Promise<CompletionItem | undefined> {
    return this._lspSession.resolveCompletionItem(completionItem)
  }

  private _restartDiagnosticsTimer() {
    if (this._diagnosticsTimer) {
      clearTimeout(this._diagnosticsTimer)
      this._diagnosticsTimer = undefined
    }

    this._diagnosticsTimer = setTimeout(() => {
      this._diagnosticsTimer = undefined
      this._requestDiagnostics()
    }, diagnosticDelayInMs)
  }

  private _requestDiagnostics() {
    const docVersion = this._docVersion

    if (this._notifications.onWaitingForDiagnostics) {
      this._notifications.onWaitingForDiagnostics(true)
    }

    this._lspSession
      .getDiagnostics(this._docContent)
      .then((diagnostics) => {
        if (this._docVersion === docVersion) {
          if (this._notifications.onWaitingForDiagnostics) {
            this._notifications.onWaitingForDiagnostics(false)
          }

          if (this._notifications.onDiagnostics) {
            this._notifications.onDiagnostics(diagnostics)
          }
        }
      })
      .catch((err) => {
        if (this._notifications.onWaitingForDiagnostics) {
          this._notifications.onWaitingForDiagnostics(false)
        }

        if (this._notifications.onError) {
          this._notifications.onError(err.message)
        }
      })
  }
}
