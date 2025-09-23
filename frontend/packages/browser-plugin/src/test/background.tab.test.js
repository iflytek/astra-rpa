import { describe, it, expect, vi, beforeEach } from 'vitest'
import { Tabs } from '../background/tab'

global.chrome = global.chrome || {};

// mock chrome.tabs API

describe('background/tab', () => {
  it('Tabs.query should return tabs', async () => {
    const tabs = await Tabs.query({});
    expect(Array.isArray(tabs)).toBe(true);
    expect(tabs[0].id).toBe(1);
  });
  it('Tabs.create should create tab', async () => {
    const tab = await Tabs.create({ url: 'https://b.com' });
    expect(tab.id).toBe(2);
    expect(tab.url).toBe('https://b.com');
  });
  it('Tabs.update should update tab', async () => {
    const tab = await Tabs.update(1, { url: 'https://c.com' });
    expect(tab.id).toBe(1);
    expect(tab.url).toBe('https://c.com');
  });
  it('Tabs.get should get tab', async () => {
    const tab = await Tabs.get(1);
    expect(tab.id).toBe(1);
  });
  it('Tabs.reload should resolve true', async () => {
    const res = await Tabs.reload();
    expect(res).toBe(true);
  });
  it('Tabs.goForward/goBack should resolve true', async () => {
    expect(await Tabs.goForward()).toBe(true);
    expect(await Tabs.goBack()).toBe(true);
  });
  it('Tabs.remove should resolve true', async () => {
    expect(await Tabs.remove(1)).toBe(true);
  });
  it('Tabs.getZoom should resolve 1', async () => {
    expect(await Tabs.getZoom(1)).toBe(1);
  });
  it('Tabs.executeFuncOnFrame should resolve', async () => {
    const res = await Tabs.executeFuncOnFrame(1, 0, () => 1, []);
    expect(res).toBe('ok');
  });
  it('Tabs.getAllTabs should return tabs', async () => {
    const tabs = await Tabs.getAllTabs();
    expect(Array.isArray(tabs)).toBe(true);
  });
  it('Tabs.activeTargetTab should resolve tab', async () => {
    const tab = await Tabs.activeTargetTab(1);
    expect(tab.id).toBe(1);
  });
});
