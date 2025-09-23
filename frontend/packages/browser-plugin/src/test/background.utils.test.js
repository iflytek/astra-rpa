import { describe, it, expect, vi } from 'vitest'
import { Utils } from '../background/utils'


describe('background/utils', () => {
  it('getNavigatorUserAgent should return $chrome$ for Chrome', () => {
    vi.stubGlobal('navigator', { userAgent: 'Mozilla/5.0 Chrome' });
    expect(Utils.getNavigatorUserAgent()).toBe('$chrome$');
  });
  it('getNavigatorUserAgent should return $firefox$ for Firefox', () => {
    vi.stubGlobal('navigator', { userAgent: 'Mozilla/5.0 Firefox' });
    expect(Utils.getNavigatorUserAgent()).toBe('$firefox$');
  });
  it('wait should resolve after given seconds', async () => {
    const start = Date.now();
    await Utils.wait(0.01);
    expect(Date.now() - start).toBeGreaterThanOrEqual(10);
  });
  it('removeUrlParams should remove query string', () => {
    expect(Utils.removeUrlParams('https://a.com/?a=1')).toBe('https://a.com/');
  });
  it('isEndWithSlash should work', () => {
    expect(Utils.isEndWithSlash('https://a.com/')).toBe(true);
    expect(Utils.isEndWithSlash('https://a.com')).toBe(false);
  });
  it('stringToRegex should parse regex string', () => {
    const reg = Utils.stringToRegex('/abc/i');
    expect(reg).toBeInstanceOf(RegExp);
    expect('abc').toMatch(reg);
  });
  it('isSupportProtocal should work', () => {
    expect(Utils.isSupportProtocal('http://a')).toBe(true);
    expect(Utils.isSupportProtocal('file://a')).toBe(true);
    expect(Utils.isSupportProtocal('chrome://a')).toBe(false);
  });
  it('isNumberStartString should work', () => {
    expect(Utils.isNumberStartString('1abc')).toBe(true);
    expect(Utils.isNumberStartString('abc')).toBe(false);
  });
  it('isNumberString should work', () => {
    expect(Utils.isNumberString('a1')).toBe(true);
    expect(Utils.isNumberString('abc')).toBe(false);
  });
  it('isSpecialCharacter should work', () => {
    expect(Utils.isSpecialCharacter('1abc')).toBe(true);
    expect(Utils.isSpecialCharacter('abc!')).toBe(true);
    expect(Utils.isSpecialCharacter('abc')).toBe(false);
  });
  it('success/fail/result should return correct structure', () => {
    const s = Utils.success('data', 'ok');
    expect(s.code).toBeDefined();
    expect(s.data).toBe('data');
    expect(s.msg).toBe('ok');
    const f = Utils.fail('fail');
    expect(f.code).toBeDefined();
    expect(f.data).toBeNull();
    expect(f.msg).toBe('fail');
    const r = Utils.result('d', 'm', 123);
    expect(r.code).toBe(123);
    expect(r.data).toBe('d');
    expect(r.msg).toBe('m');
  });
});