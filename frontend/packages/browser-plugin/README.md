# 仓库说明

本仓库为RPA浏览器插件仓库，处理网页相关自动化

# 打包说明

- 打包命令：npm run build

# 部分功能说明

## 1. 插件深度搜索功能

需要悬浮鼠标5秒以上，才能触发深度搜索，深度搜索旨在解决一部分元素遮挡的问题，但有些未遮挡的元素，深度搜索后会导致元素并非是用户想要的元素，所以不是所有的元素都需要触发深度搜索

### 实现方式：

通过获取鼠标 x,y 下所有的元素 `document.elementsFromPoint(x, y)` 来获取元素后，通过每个元素的 left, top, right, bottom 距离 target (x, y) 找到最近的一个元素，若存在多个结果，取第一项。

### 插件 shadowRoot 递归获取元素功能,

具体查看 `shadowRootElement` 函数，递归查找元素是否是 shadowRoot 元素，若是，则继续查找 shadowRoot 下元素，直到找到普通元素，中间拼接 `$shadow$`，方便用户识别元素路径, 通过path获取元素时，也会识别到 `$shadow$`，并经函数 `getElementBySelector`找到目标元素， shadowRoot 元素暂时只支持 css 选择器获取，不支持xpath选择器获取。

### frame 定位功能

#### 跨域/同源iframe 元素位置统一处理办法

#### 1. 跨域iframe元素位置统一处理办法

说明：在跨域iframe元素中，由于同源策略的限制，以及存在iframe 的src 固定，iframe 的url 是会变动的，以及同一个tab下可能存在一摸一样src 的iframe , 通过src 查找所要的iframe 是不准确的。
解决方法：通过插件主进程获取到iframe 的嵌套关系， parentFrameId , 得到一个嵌套关系的顺序，让后通过传入的 x,y 坐标，通过嵌套关系顺序，逐层查找，x, y 也会逐层减去 iframe 的位置，以及iframe的盒模型borderLeft, paddingLeft 得到准确的iframe content 的位置。
详细见 getIframeElement 这个函数在backgroundInject 和contentInject 的处理

#### 2. 同源iframe元素位置统一处理办法

说明： 同上，虽然同源限制更小，但是按同一套方法处理，可以避免冗余，减少变量，减少出错。

#### 3. iframe元素定位处理办法

说明：再content中，会标记当前窗口下的所有frame 元素，并通过iframe.contentWindow.postMessage将iframe 的xpath 路径传给对应的iframe, 对应的iframe 中通过window.addEventListener('message', function(e) { }) 接收xpath 路径, 并传给主进程，这时就可以绑定iframe 的xpath 路径和iframe 的id。这样就可以按照 id 的嵌套关系来得到一个总的iframe 的 path 全路径，通过iframeXpath 这个字段即可定位到对应的iframe 以及iframe中的目标元素。

#### 4. 注意

iframeXpath 与其他元素定位逻辑相同，统一查找逻辑，也存在动态性问题。

# 构建crx/xpi 包说明

### Chrome

1. chrome 可以选择构建crx 插件包，推荐使用chrome developer dashboard 发布到chrome 插件商店，chrome 开发者账户需要收费，若不发布到插件商店，会被chrome 浏览器的限制启用，需要在安装插件时写入chrome://policy 政策 `ExtensionInstallAllowlist ` Windows 以注册表的方式 `Software\Policies\Google\Chrome\ExtensionInstallAllowlist` 写入白名单，Linux 写入方式 `/etc/opt/chrome/policies/managed/policy.json  ` 详细可见 [https://chromeenterprise.google/policies/?policy=ExtensionInstallAllowlist]()
2. 不发布的打包方式：打开chrome浏览器，进入chrome://extensions/ 页， 启用开发者模式，选择打包扩展程序，浏览扩展程序根目录，第一次私钥文件可以不填，然后打包扩展程序，在扩展程序根目录就会生成一个对应的.crx 文件 和 .pem 密钥文件，.pem文件后续在更新插件包的时候需要使用，同一个密钥文件就会生成一样的插件id， 用于更新插件。

### Firefox

1. firefox 可以免费自行申请一个开发者账户，上传打包自己的插件xpi 文件，可以不发布，直接下载下xpi 文件亦可以安装。
