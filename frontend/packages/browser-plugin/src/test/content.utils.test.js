/** @format */
import { expect, test } from 'vitest';
import { Utils } from '../content/utils';

const {  isNumberStartString, isSupportUrl } = Utils;

test('isNumberStartString', () => {
  expect(isNumberStartString('123abc')).toBe(true);
  expect(isNumberStartString('abc123')).toBe(false);
})

test('isSupportUrl', () => {
  expect(isSupportUrl('https://www.example.com')).toBe(true);
  expect(isSupportUrl('http://www.example.com')).toBe(true);
  expect(isSupportUrl('ftp://www.example.com')).toBe(true);
  expect(isSupportUrl('file://www.example.com')).toBe(true);
  expect(isSupportUrl('chrome://extensions')).toBe(false);
})


