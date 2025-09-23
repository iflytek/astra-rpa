import { generateXPath, getElementBySelector, getElementsByXpath } from './element'

export function elementChangeWatcher(data: ElementInfo): WatchXPathResult {
  const { xpath, cssSelector, checkType, shadowRoot, matchTypes } = data
  const onlyPosition = matchTypes && matchTypes.includes('onlyPosition')
  let result: WatchXPathResult = {
    found: false,
    lastMatchedNode: null,
    lastMatchedStep: null,
    notFoundStep: null,
    notFoundIndex: 0,
  }
  if (checkType === 'customization') {
    if (shadowRoot) {
      return findNodeByCssSelectorStepwise(cssSelector, onlyPosition)
    }
    if (xpath) {
      return findNodeByXPathStepwise(xpath, onlyPosition)
    }
    if (cssSelector) {
      return findNodeByCssSelectorStepwise(cssSelector, onlyPosition)
    }
  }
  else {
    const dirXpath = generateXPath(data.pathDirs)
    result = findNodeByXPathStepwise(dirXpath, onlyPosition)
  }
  return result
}

function findNodeByCssSelectorStepwise(selector: string, onlyPosition: boolean = false): WatchXPathResult {
  const steps = selector
    .split('>')
    .map(s => s.trim())
    .filter(Boolean)

  let lastMatchedNode: Element | null = document.querySelector('html')
  let lastMatchedStep: string | null = null

  for (let i = 0; i < steps.length; i++) {
    let j = i + 1
    if (steps[i] === '$shadow$') {
      j = j + 1
      if (j > steps.length) {
        return {
          found: false,
          lastMatchedNode,
          lastMatchedStep,
          notFoundStep: selector,
          notFoundIndex: i + 1,
        }
      }
    }

    const partialSelector = steps.slice(0, j).join('>').trim()
    let nodes: Element[] | null = null

    try {
      nodes = getElementBySelector(partialSelector, onlyPosition)
    }
    catch {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: partialSelector,
        notFoundIndex: i + 1,
      }
    }

    if (!nodes || nodes.length === 0) {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: partialSelector,
        notFoundIndex: i + 1,
      }
    }

    lastMatchedNode = nodes[0] ?? null
    lastMatchedStep = partialSelector
  }

  return {
    found: true,
    lastMatchedNode,
    lastMatchedStep,
    notFoundStep: null,
  }
}

function findNodeByXPathStepwise(xpath: string, onlyPosition: boolean = false): WatchXPathResult {
  const steps = xpath.split('/').filter(s => s.trim() !== '')
  let lastMatchedNode: Node | null = document
  let lastMatchedStep: XPathStep | null = null
  let nextStep = ''

  for (let i = 0; i < steps.length; i++) {
    const step = i === 0 && !steps[i].startsWith('html') ? `//${steps[i]}` : `/${steps[i]}`
    nextStep = nextStep + step

    let eles: Node[] | null = null
    try {
      eles = getElementsByXpath(nextStep, onlyPosition)
    }
    catch {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: nextStep,
        notFoundIndex: i + 1,
      }
    }

    const foundNode = eles && eles.length > 0 ? eles[0] : null
    if (!foundNode) {
      return {
        found: false,
        lastMatchedNode,
        lastMatchedStep,
        notFoundStep: nextStep,
        notFoundIndex: i + 1,
      }
    }

    lastMatchedNode = foundNode
    lastMatchedStep = nextStep
  }

  return {
    found: true,
    lastMatchedNode,
    lastMatchedStep,
    notFoundStep: null,
  }
}
