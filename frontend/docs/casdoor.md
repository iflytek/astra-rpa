# Casdoor 配置说明文档

## 1. 配置项说明

Casdoor 认证在本项目中通过 SDK 初始化，主要配置项如下：

| 配置项            | 说明                       | 示例值                      |
|-------------------|----------------------------|-----------------------------|
| serverUrl         | Casdoor 服务端地址         | http://localhost:8000       |
| clientId          | 应用 Client ID             | e3ba6fec42cfe996121f        |
| appName           | Casdoor 应用名称           | example-app                   |
| organizationName  | Casdoor 组织名称           | example-org                         |
| redirectPath      | 登录回调路径               | /                           |

配置代码示例（见 [`index.ts`](../packages/web-app/src/auth/casdoorAuth/index.ts)）：

```typescript
const config = {
  serverUrl: this.serverUrl,
  clientId: 'e3ba6fec42cfe996121f',
  appName: 'example-app',
  organizationName: 'example-org',
  redirectPath: '/',
}
```

## 2. 服务端登录页面地址配置

- 默认 Casdoor 服务端地址为 `http://localhost:8000`。
- 实际地址可通过 [`frontend/packages/tauri-app/src-tauri/resources/conf.json`](../packages/tauri-app/src-tauri/resources/conf.json) 文件中的 `casdoor` 字段动态配置（ `unauthorize.ts`）。

示例：

```json
{
  "casdoor": "http://localhost:8000"
}
```

## 3. 登录流程

1. 检查本地是否已登录（`accessToken`）。
2. 未登录时，自动重定向到 Casdoor 登录页面
3. 登录回调后，获取 `code` 和 `state`，调用后端接口换取 `accessToken` 并存储到本地。
4. 登录成功后跳转到主页面。

注:

- 登录重定向 URL 由后端 `/robot/user/api/redirect-url` 接口返回。
- 所有 Casdoor 相关操作均依赖本地存储的 `accessToken`，并通过 HTTP Header 传递。

## 4. 其他说明

如需修改 Casdoor 配置，请确保同步更新前端 SDK 初始化参数及后端配置文件。
