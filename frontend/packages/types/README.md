# @rpa/types

共享的 TypeScript 类型定义包，用于 RPA 项目中的多个 packages。

## 安装

在需要使用类型的 package 中安装：

```bash
pnpm add @rpa/types
```

## 使用方法

### 1. 导入类型

```typescript
import type {
  AppEnv,
  ClipboardManager,
  UtilsManager,
  WindowManager
} from '@rpa/types'
```

### 2. 在组件中使用

```typescript
import type { AppEnv, WindowManager } from '@rpa/types'
// Vue 组件示例
import { defineComponent } from 'vue'

export default defineComponent({
  setup() {
    const windowManager: WindowManager = window.windowManager!
    const appEnv: AppEnv = window.utilsManager?.getAppEnv() || 'browser'

    const createWindow = async (options: CreateWindowOptions) => {
      return await windowManager.createWindow(options)
    }

    return {
      createWindow,
      appEnv
    }
  }
})
```

### 3. 在 SDK 中使用

```typescript
// SDK 文件示例
import type { WindowManager, WindowMessage } from '@rpa/types'

export class WindowSDK {
  private windowManager: WindowManager

  constructor(windowManager: WindowManager) {
    this.windowManager = windowManager
  }

  async sendMessage(message: WindowMessage) {
    return await this.windowManager.emitTo(message)
  }
}
```

### 4. 全局类型声明

types package 已经包含了全局类型声明，你可以在任何地方直接使用：

```typescript
// 直接使用全局类型 - TypeScript 会自动识别类型
const windowManager = window.windowManager // 类型: WindowManager | undefined
const clipboardManager = window.clipboardManager // 类型: ClipboardManager | undefined
const utilsManager = window.utilsManager // 类型: UtilsManager | undefined

// 类型安全的访问
if (windowManager) {
  // 在这里 windowManager 的类型是 WindowManager
  await windowManager.showWindow()
  const isMaximized = await windowManager.isMaximized()
}

if (utilsManager) {
  // 在这里 utilsManager 的类型是 UtilsManager
  const appEnv = utilsManager.getAppEnv() // 类型: AppEnv
  const version = await utilsManager.getAppVersion() // 类型: Promise<string>
}
```

### 5. 配置说明

要让全局类型在你的 package 中生效，需要确保：

1. **安装依赖**：在 package.json 中添加 `"@rpa/types": "workspace:*"`
2. **TypeScript 配置**：在 tsconfig.json 中添加 `"types": ["@rpa/types"]`
3. **重新安装依赖**：运行 `pnpm install` 重新安装依赖

```json
// package.json
{
  "dependencies": {
    "@rpa/types": "workspace:*"
  }
}

// tsconfig.json
// {
//   "compilerOptions": {
//     "types": ["@rpa/types"]
//   }
// }
```

## 可用的类型

- `WindowManager` - 窗口管理器接口
- `CreateWindowOptions` - 窗口创建选项
- `WindowMessage` - 窗口消息类型
- `ClipboardManager` - 剪贴板管理器接口
- `UtilsManager` - 工具管理器接口
- `ShortCutManager` - 快捷键管理器接口
- `UpdaterManager` - 更新管理器接口
- `UpdateManifest` - 更新清单接口
- `UpdateInfo` - 更新信息接口
- `AppEnv` - 应用环境类型

## 开发

### 添加新类型

1. 在 `index.d.ts` 中添加新的类型定义
2. 使用 `export` 关键字导出类型
3. 更新此 README 文档

### 类型检查

```bash
pnpm type-check
```

## 注意事项

- 所有类型都应该使用 `export` 关键字导出
- 保持类型定义的向后兼容性
- 添加适当的注释说明类型用途
- 避免使用 `any` 类型，尽量使用具体的类型定义
