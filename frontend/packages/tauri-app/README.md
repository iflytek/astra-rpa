# AstronRPA Tauri App

> 基于 Tauri 框架构建的 RPA (机器人流程自动化) 桌面应用程序

## 项目简介

AstronRPA 是一个使用 Tauri 框架开发的跨平台桌面 RPA 应用，结合了 Rust 后端的高性能和 Web 前端的灵活性。应用支持在线和离线两种运行模式，提供完整的 RPA 自动化解决方案。

## 技术栈

- **前端**: Vue.js (来自 @rpa/web-app 工作区包)
- **后端**: Rust + Tauri
- **UI 框架**: 支持系统托盘、窗口管理等原生功能
- **依赖管理**: Python 运行时环境动态下载和管理

## 项目特性

- 🚀 **跨平台支持**: Windows、macOS、Linux
- 🌐 **双模式运行**: 在线模式和离线模式
- 📦 **自动依赖管理**: 自动下载和配置 Python 运行环境
- 🔔 **系统托盘**: 支持最小化到系统托盘
- 🪟 **无边框窗口**: 现代化的用户界面设计
- 📋 **全局快捷键**: 支持全局快捷键操作
- 📁 **文件操作**: 完整的文件系统访问权限
- 🔄 **进程防重复**: 防止多重启动实例

## 安装与使用

### 环境要求

- Node.js >= 16
- Rust >= 1.70
- pnpm 包管理器

### 快速开始

1. **安装依赖**
   ```bash
   pnpm install
   ```

2. **开发模式运行**
   ```bash
   # 启动 Web 前端开发服务器
   pnpm run dev:web
   
   # 启动 Tauri 开发环境（离线模式）
   pnpm run dev
   ```

3. **构建生产版本**
   ```bash
   # 构建 Web 前端
   pnpm run build:web
   
   # 构建桌面应用
   pnpm run build
   ```

## 可用脚本

### 开发脚本
- `pnpm run dev:web` - 启动 Web 前端开发服务器
- `pnpm run dev` - 启动 Tauri 开发环境（离线模式）

### 构建脚本
- `pnpm run build` - 构建生产版本
- `pnpm run build:web` - 仅构建 Web 前端
- `pnpm run build:updater` - 构建在线更新版本
- `pnpm run build:debug` - 构建调试版本

## 配置说明

### 配置文件

配置文件位于 `src-tauri/resources/conf.json`，包含:
- `remote_addr`: 远程服务器地址（在线模式使用）
- `casdoor`: casdoor 登录认证服务地址

## 核心功能

### 系统功能
- **窗口管理**: 无边框窗口、窗口阴影、居中显示
- **系统托盘**: 最小化到托盘、托盘菜单交互
- **进程管理**: 防止重复启动、进程监控
- **日志系统**: 完整的日志记录和文件输出

### RPA 功能
- **Python 环境**: 自动下载和配置 Python 运行时
- **脚本执行**: 执行 RPA 自动化脚本
- **实时通信**: 前后端实时消息传递
- **文件处理**: 自动下载、解压依赖文件

## 依赖说明

### 主要依赖
- `@tauri-apps/api`: Tauri 前端 API
- `@rpa/web-app`: Web 前端应用（工作区依赖）

### 开发依赖
- `@tauri-apps/cli`: Tauri 命令行工具
- `env-cmd`: 环境变量管理
- `cross-env`: 跨平台环境变量设置

## 目录结构

```
packages/tauri-app/
├── src-tauri/              # Rust 后端代码
│   ├── src/                # 源代码
│   │   ├── main.rs         # 主程序入口
│   │   ├── tray.rs         # 系统托盘模块
│   │   └── utils.rs        # 工具函数
│   ├── resources/          # 资源文件
│   ├── icons/              # 应用图标
│   └── Cargo.toml          # Rust 依赖配置
├── scripts/                # 构建脚本
└── package.json            # Node.js 依赖配置
```

## 开发指南

### 添加新功能

1. **前端功能**: 在 `@rpa/web-app` 包中开发
2. **后端功能**: 在 `src-tauri/src/` 中添加 Rust 代码
3. **系统集成**: 使用 Tauri Commands 实现前后端通信

### 调试

- 使用 `pnpm run build:debug` 构建调试版本
- 查看 `logs/main.log` 获取运行日志
- 使用浏览器开发者工具调试前端

## 版本信息

- **当前版本**: 0.1.0
- **Tauri 版本**: 1.6.x
- **许可协议**: 私有项目

## 技术支持

如遇问题，请检查:
1. 日志文件中的错误信息
2. Python 环境是否正确安装
3. 网络连接状态（在线模式）
4. 配置文件是否正确

---

© 2024 科大讯飞股份有限公司
