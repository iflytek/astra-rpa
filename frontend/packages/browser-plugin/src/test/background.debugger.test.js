import { describe, it, expect, vi, beforeEach } from 'vitest'
import { Debugger, checkDebuggerDetached } from '../background/debugger'

global.chrome = global.chrome || {};

describe('background/debugger', () => {

  it('checkDebuggerDetached should resolve true if not attached', async () => {
    global.chrome.debugger.getTargets = vi.fn(cb => cb([]));
    await expect(checkDebuggerDetached(1)).resolves.toBe(true);
  });

  it('checkDebuggerDetached should timeout after 10 attempts', async () => {
    global.chrome.debugger.getTargets = vi.fn(cb => cb([{ tabId: 1 }]));
    await expect(checkDebuggerDetached(1, 11)).rejects.toThrow('检测 detach 状态超时');
  });

  it('Debugger.attachDebugger should resolve true', async () => {
    await expect(Debugger.attachDebugger(1)).resolves.toBe(true);
    Debugger.attached = false
  });
  
  it('Debugger.attachDebugger should reject if already attached', async () => {
    Debugger.attached = true;
    await expect(Debugger.attachDebugger(1)).rejects.toThrow('Debugger is already attached to a tab');
    Debugger.attached = false;
  });

  it('Debugger.detachDebugger should resolve true', async () => {
    Debugger.attached = true;
    await expect(Debugger.detachDebugger(1)).resolves.toBe(true);
  });

  it('Debugger.enableRuntime should resolve true', async () => {
    await expect(Debugger.enableRuntime(1)).resolves.toBe(true);
  });

  it('Debugger.getFrameTree should resolve', async () => {
    await expect(Debugger.getFrameTree(1)).resolves.toBeDefined();
  });

  it('Debugger.evaluate should throw if no context', async () => {
    Debugger.frameContextIdMap = { 0: [] };
    await expect(Debugger.evaluate(1, '1+1', 0)).rejects.toThrow('未找到执行上下文');
  });
});
