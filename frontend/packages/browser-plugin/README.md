# English | [简体中文](./README.zh.md)

# Repository Description

This repository is for the RPA browser plugin, which handles web-related automation.

# Build Instructions

- Build command: `npm run build`

# Feature Overview

## 1. Deep Search Feature

To trigger deep search, you need to hover the mouse for more than 5 seconds. Deep search is designed to solve the problem of some elements being covered. However, for some uncovered elements, deep search may result in selecting an element that is not the one the user wants, so not all elements require deep search.

### Implementation:

By using `document.elementsFromPoint(x, y)` to get all elements under the mouse coordinates (x, y), then for each element, calculate the distance from its left, top, right, and bottom to the target (x, y), and find the closest element. If there are multiple results, take the first one.

### Recursive shadowRoot Element Retrieval

See the `shadowRootElement` function for details. It recursively checks if an element is a shadowRoot element. If so, it continues to search within the shadowRoot until a normal element is found. The path is concatenated with `$shadow$` for easy identification. When retrieving elements by path, `$shadow$` is also recognized, and the function `getElementBySelector` is used to find the target element. Currently, shadowRoot elements only support CSS selectors, not XPath selectors.

### Frame Positioning Feature

#### Unified Handling for Cross-origin/Same-origin iframe Elements

##### 1. Cross-origin iframe Handling

In cross-origin iframes, due to the same-origin policy and the fact that iframe src can be fixed but the URL may change, and there may be identical src iframes in the same tab, finding the desired iframe by src is inaccurate. The solution is to obtain the nesting relationship (parentFrameId) from the plugin's main process, get the nesting order, and then, by passing the x, y coordinates and the nesting order, search layer by layer. The x, y coordinates are also reduced layer by layer by the iframe's position and box model (borderLeft, paddingLeft) to get the accurate position in the iframe content. See the `getIframeElement` function in backgroundInject and contentInject for details.

##### 2. Same-origin iframe Handling

Same as above. Although the same-origin restriction is less strict, using the same method avoids redundancy, reduces variables, and minimizes errors.

##### 3. iframe Element Positioning

In content, all frame elements in the current window are marked, and the iframe's XPath is sent to the corresponding iframe via `iframe.contentWindow.postMessage`. The iframe receives the XPath via `window.addEventListener('message', function(e) { })` and sends it to the main process. This binds the iframe's XPath to its id. Thus, the full iframe path can be obtained according to the id nesting relationship, and the target element in the iframe can be located via the `iframeXpath` field.

##### 4. Note

The logic for locating iframeXpath is the same as for other elements, and there are also dynamic issues.

# Building crx/xpi Packages

### Chrome

1. Chrome can build crx plugin packages. It is recommended to use the Chrome Developer Dashboard to publish to the Chrome Web Store. A developer account is required (paid). If not published to the store, Chrome will restrict enabling the plugin. You need to add the plugin to the whitelist via the `chrome://policy` policy. On Windows, add to the registry at `Software\Policies\Google\Chrome\ExtensionInstallAllowlist`. On Linux, add to `/etc/opt/chrome/policies/managed/policy.json`. See [https://chromeenterprise.google/policies/?policy=ExtensionInstallAllowlist]() for details.
2. For unpublished packaging: Open Chrome, go to chrome://extensions/, enable Developer Mode, select 'Pack extension', browse to the extension root directory. The first time, you can leave the private key file blank. After packing, a .crx file and a .pem key file will be generated in the root directory. The .pem file is needed for future updates. Using the same key file will generate the same plugin id for updates.

### Firefox

1. You can apply for a free developer account on Firefox, upload your packaged xpi file, and install it directly without publishing.
