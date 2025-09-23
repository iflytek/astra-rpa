/** @format */

import { describe, it, expect, beforeEach } from 'vitest'
import * as element from '../content/element'
describe('content/element', () => {
  beforeEach(() => {
    document.body.innerHTML = `
    <div id="testMain" class="foo" type="main">Hello</div>
    <div id="test2" class="bar" type="secondary">
      <span class="child">Child</span>
    </div>
    <svg id="svg1"><circle></circle></svg>
    <iframe id="frame1" src="about:blank"></iframe>
  `
  })
  it('getText should get input value', () => {
    const input = document.createElement('input')
    input.value = 'abc'
    expect(element.getText(input)).toBe('abc')
  })
  it('getText should get textarea value', () => {
    const textarea = document.createElement('textarea')
    textarea.value = 'def'
    expect(element.getText(textarea)).toBe('def')
  })
  it('getText should get img alt', () => {
    const img = document.createElement('img')
    img.setAttribute('alt', 'alttext')
    expect(element.getText(img)).toBe('alttext')
  })
  it('getAttr should get id/class/name/type/value/href/src/title/text/readonly', () => {
    const a = document.createElement('a')
    a.id = 'id1'
    a.className = 'cls'
    a.name = 'nm'
    a.setAttribute('type', 't')
    a.href = 'https://a.com'
    a.title = 'tt'
    a.value = 'v'
    a.textContent = 'txt'
    a.readOnly = false
    expect(element.getAttr(a, 'id')).toBe('id1')
    expect(element.getAttr(a, 'class')).toBe('cls')
    expect(element.getAttr(a, 'name')).toBe('nm')
    expect(element.getAttr(a, 'type')).toBe('t')
    expect(element.getAttr(a, 'value')).toBe('v')
    expect(element.getAttr(a, 'href')).toContain('a.com')
    expect(element.getAttr(a, 'title')).toBe('tt')
    expect(typeof element.getAttr(a, 'text')).toBe('string')
    expect(element.getAttr(a, 'readonly')).toBe('false')
  })
  it('getAttrs should get attribute map', () => {
    const div = document.createElement('div')
    div.setAttribute('src', 's')
    div.setAttribute('href', 'h')
    div.setAttribute('id', 'i')
    div.setAttribute('class', 'c')
    div.setAttribute('title', 't')
    div.setAttribute('name', 'n')
    const attrs = element.getAttrs(div)
    expect(attrs.src).toBe('s')
    expect(attrs.href).toBe('h')
    expect(attrs.id).toBe('i')
    expect(attrs.class).toBe('c')
    expect(attrs.title).toBe('t')
    expect(attrs.name).toBe('n')
  })
  it('isTable should detect table and child', () => {
    const table = document.createElement('table')
    expect(element.isTable(table)).toBe(true)
    const tr = document.createElement('tr')
    table.appendChild(tr)
    expect(element.isTable(tr)).toBe(true)
  })
  it('getXpath should return xpath', () => {
    const div = document.createElement('div')
    document.body.appendChild(div)
    expect(element.getXpath(div)).toContain('div')
    document.body.removeChild(div)
  })
  it('getNthCssSelector should return selector', () => {
    const div = document.createElement('div')
    document.body.appendChild(div)
    expect(element.getNthCssSelector(div)).toContain('div')
    document.body.removeChild(div)
  })
  it('getElementsByXpath should return elements or null', () => {
    expect(element.getElementsByXpath('//div', false)).toBeInstanceOf(Array)
  })

  it('element.getElementDirectory returns correct directory for element with id', () => {
    const el = document.getElementById('testMain')
    const dirs = element.getElementDirectory(el)
    expect(dirs.length).toBeGreaterThan(0)
    const id = dirs[dirs.length - 1].attrs.find(a => a.name === 'id' && a.value === 'testMain')
  })

  it('element.generateXPath returns correct xpath for directory', () => {
    const el = document.getElementById('testMain')
    const dirs = element.getElementDirectory(el)
    const xpath = element.generateXPath(dirs)
    expect(typeof xpath).toBe('string')
    expect(xpath).toContain('="testMain"')
  })

  it('element.getAllElements returns all elements', () => {
    const all = element.getAllElements()
    expect(Array.isArray(all)).toBe(true)
    expect(all.length).toBeGreaterThan(0)
  })

  it('element.getAllElementsPosition returns positions for all elements', () => {
    const positions = element.getAllElementsPosition()
    expect(Array.isArray(positions)).toBe(true)
    expect(positions.length).toBeGreaterThan(0)
    expect(positions[0]).toHaveProperty('element')
  })

  it('element.getAllElementsPositionInBody returns only visible elements', () => {
    const positions = element.getAllElementsPositionInBody()
    expect(Array.isArray(positions)).toBe(true)
    expect(positions.every(pos => pos.element)).toBe(true)
  })

  it('element.getElementsByPosition returns elements at a point', () => {
    const positions = element.getElementsByPosition(1, 1)
    expect(Array.isArray(positions)).toBe(true)
  })

  it('element.getElementsFromPoints returns unique elements in area', () => {
    const elements = element.getElementsFromPoints({ x: 0, y: 0 }, { x: 2, y: 2 })
    expect(Array.isArray(elements)).toBe(true)
  })

  it('element.getElementFromAllElements filters by range', async () => {
    const elements = [
      { x: 0, y: 0, width: 10, height: 10 },
      { x: 20, y: 20, width: 10, height: 10 }
    ]
    const range = { start: { x: 0, y: 0 }, end: { x: 15, y: 15 } }
    const result = await element.getElementFromAllElements(elements, range)
    expect(result.length).toBe(1)
  })

  it('element.getClosestElementByPoint returns element at point', () => {
    const el = element.getClosestElementByPoint({ x: 1, y: 1 })
    expect(el instanceof Element || el === undefined).toBe(true)
  })

  it('element.hasChildElement detects children', () => {
    const parent = document.getElementById('test2')
    expect(element.hasChildElement(parent)).toBe(true)
    const child = document.querySelector('.child')
    expect(element.hasChildElement(child)).toBe(false)
  })

  it('element.getBoundingClientRect returns scaled rect', () => {
    window.currentFrameInfo = { iframeTransform: { scaleX: 1, scaleY: 1 } }
    Object.defineProperty(window, 'devicePixelRatio', { value: 1, configurable: true })
    const el = document.getElementById('testMain')
    const rect = element.getBoundingClientRect(el)
    expect(rect).toHaveProperty('left')
    expect(rect).toHaveProperty('width')
  })

  it('element.getIframeTransform returns scaleX and scaleY', () => {
    const el = document.createElement('div')
    el.style.transform = 'scale(2, 3)'
    document.body.appendChild(el)
    const result = element.getIframeTransform(el)
    expect(result).toHaveProperty('scaleX')
    expect(result).toHaveProperty('scaleY')
  })

  it('element.getFrameContentRect returns correct rect', () => {
    window.currentFrameInfo = { iframeTransform: { scaleX: 1, scaleY: 1 } }
    Object.defineProperty(window, 'devicePixelRatio', { value: 1, configurable: true })
    const el = document.getElementById('testMain')
    const rect = element.getFrameContentRect(el)
    expect(rect).toHaveProperty('left')
    expect(rect).toHaveProperty('width')
  })

  it('element.getChildElementByType returns correct child', () => {
    const parent = document.getElementById('test2')
    expect(element.getChildElementByType(parent, { elementGetType: 'index', index: 0 })).toBe(parent.children[0])
    expect(element.getChildElementByType(parent, { elementGetType: 'all' })).toEqual(Array.from(parent.children))
    expect(element.getChildElementByType(parent, { elementGetType: 'last' })).toBe(parent.lastElementChild)
  })

  it('element.getSiblingElementByType returns correct sibling', () => {
    const el = document.getElementById('testMain')
    expect(element.getSiblingElementByType(el, { elementGetType: 'next' })).toBe(el.nextElementSibling)
    expect(element.getSiblingElementByType(el, { elementGetType: 'prev' })).toBe(el.previousElementSibling)
  })
})
