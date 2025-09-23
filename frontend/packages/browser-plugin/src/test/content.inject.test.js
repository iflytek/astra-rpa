import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as contentInject from '../content/contentInject'


describe('contentInject', () => {
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
  it('formatElementInfo should return correct structure', () => {
    const el = document.createElement('div')
    const info = contentInject['formatElementInfo'](el, document)
    expect(info.xpath).toBeDefined()
    expect(info.cssSelector).toBeDefined()
    expect(info.pathDirs).toBeDefined()
    expect(info.tag).toBe('块元素')
    expect(info.text).toBe('未知名称')
  })

  it('dispatchMouseSequence should dispatch events', () => {
    const el = document.createElement('div')
    const events = []
    el.addEventListener('mousedown', () => events.push('mousedown'))
    el.addEventListener('mouseup', () => events.push('mouseup'))
    el.addEventListener('click', () => events.push('click'))
    contentInject['dispatchMouseSequence'](el, ['mousedown', 'mouseup', 'click'], { clientX: 1, clientY: 2 })
    return new Promise((resolve) => setTimeout(() => {
      expect(events).toEqual(['mousedown', 'mouseup', 'click'])
      resolve()
    }, 10))
  })

  it('ContentHandler.ele.getElement should return element', async () => {
    const data = { matchTypes: [], checkType: 'customization', xpath: '/div[1]' }
    const eles = await contentInject['ContentHandler'].ele.getElement(data)
    expect(eles).toBe(null)
  })

  it('ContentHandler.ele.getDom should return first element', async () => {
    const data = {matchTypes: [], checkType: 'customization', xpath: '/div' }
    const el = await contentInject['ContentHandler'].ele.getDom(data)
    expect(el).toBe(null)
  })

  it('ContentHandler.ele.elementIsRender should return success', async () => {
    const data = { matchTypes: [], checkType: 'customization', xpath: '/div' }
    const res = await contentInject['ContentHandler'].ele.elementIsRender(data)
    expect(res.code).toBe('0000')
  })
})
