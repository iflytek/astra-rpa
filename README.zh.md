# AstronRPA

<div align="center">

![AstronRPA Logo](./docs/images/icon_128px.png)

**🤖 企业级机器人流程自动化（RPA）开发平台**

[![License](https://img.shields.io/badge/license-Open%20Source-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![Java](https://img.shields.io/badge/java-8+-orange.svg)](https://openjdk.java.net/)
[![Vue](https://img.shields.io/badge/vue-3+-green.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![GitHub Stars](https://img.shields.io/github/stars/iflytek/astron-rpa?style=social)](https://github.com/iflytek/astron-rpa/stargazers)

[English](README.md) | 简体中文

</div>

## 📑 目录

- [📋 概述](#-概述)
- [🎯 为什么选择 AstronRPA](#-为什么选择-astronrpa)
- [✨ 核心特性](#-核心特性)
- [🛠️ 技术栈](#-技术栈)
- [📱 界面展示](#-界面展示)
- [🚀 快速开始](#-快速开始)
  - [系统要求](#系统要求)
  - [使用 Docker](#使用-docker)
  - [源码部署](#源码部署)
- [📦 组件生态](#-组件生态)
- [🏗️ 技术架构](#-技术架构)
- [📚 文档链接](#-文档链接)
- [🤝 参与贡献](#-参与贡献)
- [💖 赞助支持](#-赞助支持)
- [📞 获取帮助](#-获取帮助)
- [📄 开源协议](#-开源协议)

## 📋 概述

AstronRPA 是一个全能型的机器人流程自动化（RPA）开发工具，为企业和开发者提供从设计到部署的全流程 RPA 自动化解决方案。平台集成最新的 AI 大模型、丰富的组件库、多种开发模式和框架，让开发者能够以最便捷的方式构建强大的自动化流程。

AstronRPA 源自服务于数万家企业和数百万开发者的"科大讯飞 RPA 平台"，我们将其核心引擎完全开源。通过可视化设计和构建工具，开发者可以使用无代码或低代码的方式快速创建和调试机器人、应用程序和工作流，实现强大的 RPA 应用开发和更多定制化的业务逻辑。

### 🎯 为什么选择 AstronRPA？

- **🏭 生产可用**：源自服务数万家企业的成熟平台
- **👨‍💻 开发者友好**：可视化设计 + 完整的 API 和文档
- **☁️ 云原生**：基于微服务架构，支持容器化部署
- **🔓 开源透明**：核心引擎完全开源，社区驱动开发
- **🤖 AI 赋能**：集成 DeepSeek 等大语言模型
- **🧩 组件丰富**：25+ 专业 RPA 组件库

## ✨ 核心特性

- 🚀 **高性能执行** - 基于 Python 3.13+ 的高性能执行引擎，支持分布式运行
- 🔒 **企业级安全** - 完整的权限管理、审计日志和数据加密
- 🔧 **易于集成** - 丰富的 API 接口和 SDK，支持多语言集成
- 📊 **实时监控** - 完整的执行状态监控、性能指标和告警系统
- 🌍 **多环境支持** - 支持 Windows、Linux 和容器化部署
- 📈 **弹性扩展** - 微服务架构，支持水平扩展和负载均衡

### 🎯 可视化设计
- 拖拽式流程设计器
- 实时预览和调试
- 丰富的组件模板
- 智能连线和布局

### 🤖 AI 赋能
- 智能元素识别
- OCR 文字提取
- 验证码自动识别
- 自然语言流程生成

### 🔧 组件化开发
- 25+ 专业 RPA 组件
- 标准化组件接口
- 自定义组件扩展
- 组件版本管理

### 📊 执行监控
- 实时执行状态
- 详细日志记录
- 性能指标统计
- 异常告警通知

### 🌐 多端支持
- Web 端在线编辑
- 桌面端本地运行
- 移动端监控查看
- API 接口集成

## 🛠️ 技术栈

**前端技术**: Vue 3 + TypeScript + Vite + Ant Design Vue
**后端服务**: Java Spring Boot + Python FastAPI
**数据存储**: MySQL + Redis
**消息队列**: 支持异步任务处理
**容器化**: Docker + Docker Compose
**桌面应用**: Tauri (Rust + Web)
**包管理**: pnpm workspace 单体仓库管理
**监控系统**: 集成 SkyWalking 链路追踪

## 📱 界面展示

<div align="center">
  <img src="https://via.placeholder.com/800x400?text=可视化流程设计器" alt="可视化流程设计器" width="45%">
  <img src="https://via.placeholder.com/800x400?text=执行监控仪表盘" alt="执行监控仪表盘" width="45%">
</div>

## 🏗️ 架构概览

![Architecture Overview](./docs/images/Structure-zh.png "Architecture Overview")

### 技术架构详情

### 前端架构
- **框架**：Vue 3 + TypeScript + Vite
- **UI 组件**：Ant Design Vue + VXE Table
- **状态管理**：Pinia
- **桌面应用**：Tauri（Rust + Web 技术栈）
- **包管理**：pnpm workspace 单体仓库管理

### 后端架构
- **主服务**：Java Spring Boot 2.3.11
- **AI 服务**：Python FastAPI + DeepSeek 集成
- **OpenAPI 服务**：Python FastAPI 
- **资源服务**：Java Spring Boot
- **数据库**：MySQL + Redis
- **消息队列**：支持异步任务处理

### RPA 引擎
- **语言**：Python 3.13+
- **框架**：FastAPI + asyncio
- **组件化架构**：25+ 专业 RPA 组件
- **执行器**：支持原子操作、工作流、录制回放
- **通信**：WebSocket 实时通信
- **定位技术**：图像识别、OCR、UI 自动化

### 部署架构
- **容器化**：Docker + Docker Compose
- **微服务**：独立服务模块，可单独部署
- **可观测性**：集成 SkyWalking 链路追踪
- **负载均衡**：Nginx 反向代理

## 🚀 快速开始

### 系统要求
- **操作系统**：Windows 10/11（主要支持）、macOS、Linux
- **Node.js**：>= 22
- **Python**：3.13.x
- **Java**：JDK 8+
- **pnpm**：>= 9
- **rustc**：>= 1.90.0
- **UV**：Python 包管理工具
- **7-Zip**：用于压缩解压

### 使用 Docker

推荐使用 Docker 进行快速部署：

```bash
# 克隆项目
git clone https://github.com/iflytek/astron-rpa.git
cd astron-rpa

# 进入 docker 目录
cd docker

# 启动容器栈
docker-compose up -d

# 查看服务状态
docker-compose ps
```

- 在浏览器访问 `http://localhost:8080`
- 生产部署及安全加固请参考 [部署文档](docker/QUICK_START.md)

### 源码部署

#### 一键启动（推荐）

1. **准备 Python 环境**
   ```bash
   # 下载 Python 3.13.x 并压缩为 Python313.7z 放在项目根目录
   # 或使用自定义文件名作为参数传入
   ```

2. **运行打包脚本**
   ```bash
   # 默认使用 Python313.7z, 注意运行前清理pack_workspace下面的wheels包
   pack.bat
   
   # 或使用自定义 Python 文件
   pack.bat "" "Python3.13.5.7z"
   ```

3. **构建前端应用**
   ```bash
   cd frontend
   pnpm install
   pnpm build:web
   ```

4. **构建tauri应用**
   ```bash
   cd frontend
   pnpm install
   pnpm build:tauri
   ```

#### 开发环境

```bash
# 安装依赖
cd frontend
pnpm install

# 启动 Web 开发服务器
pnpm dev:web

# 启动 Tauri 桌面应用（开发模式）
pnpm dev:tauri

# 启动后端服务（需要先配置数据库）
cd backend/robot-service
mvn spring-boot:run
```

## 📦 组件生态

### 核心组件包
- **rpasystem**：系统操作、进程管理、截图
- **rpabrowser**：浏览器自动化、网页操作
- **rpagui**：图形界面自动化、鼠标键盘操作
- **rpaexcel**：Excel 表格操作、数据处理
- **rpacv**：计算机视觉、图像识别
- **rpaai**：AI 智能服务集成
- **rpadatabase**：数据库连接和操作
- **rpanetwork**：网络请求、API 调用
- **rpaemail**：邮件发送和接收
- **rpadocx**：Word 文档处理
- **rpapdf**：PDF 文档操作
- **rpaencrypt**：加密解密功能

### 执行框架
- **atomic**：原子操作定义和执行
- **executor**：工作流执行引擎
- **recording**：操作录制和回放
- **param_utils**：参数处理工具

### 共享库
- **rpaframe**：RPA 框架核心
- **rpawebsocket**：WebSocket 通信
- **locator**：元素定位技术

## 🌟 核心特性

### 🎯 可视化设计
- 拖拽式流程设计器
- 实时预览和调试
- 丰富的组件模板
- 智能连线和布局

### 🤖 AI 赋能
- 智能元素识别
- OCR 文字提取
- 验证码自动识别
- 自然语言流程生成

### 🔧 组件化开发
- 25+ 专业 RPA 组件
- 标准化组件接口
- 自定义组件扩展
- 组件版本管理

### 📊 执行监控
- 实时执行状态
- 详细日志记录
- 性能指标统计
- 异常告警通知

### 🌐 多端支持
- Web 端在线编辑
- 桌面端本地运行
- 移动端监控查看
- API 接口集成

## 📚 文档链接

- [📖 使用指南](HOW_TO_RUN.zh.md)
- [🚀 部署指南](docker/QUICK_START.md)
- [📖 API 文档](backend/openapi-service/api.yaml)
- [🔧 组件开发指南](engine/components/)
- [🐛 故障排除](docs/TROUBLESHOOTING.md)
- [📝 更新日志](CHANGELOG.md)

## 🤝 参与贡献

我们欢迎任何形式的贡献！请查看 [贡献指南](CONTRIBUTING.md)

### 开发规范
- 遵循现有代码风格
- 添加必要的测试用例
- 更新相关文档
- 确保所有检查通过

### 贡献步骤
1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 🌟 Star 历史

<div align="center">
  <img src="https://api.star-history.com/svg?repos=iflytek/astron-rpa&type=Date" alt="Star 历史图表" width="600">
</div>

## 💖 赞助支持

<div align="center">
  <a href="https://github.com/sponsors/iflytek">
    <img src="https://img.shields.io/badge/赞助-GitHub%20Sponsors-pink?style=for-the-badge&logo=github" alt="GitHub Sponsors">
  </a>
  <a href="https://opencollective.com/astronrpa">
    <img src="https://img.shields.io/badge/赞助-Open%20Collective-blue?style=for-the-badge&logo=opencollective" alt="Open Collective">
  </a>
</div>

## 📞 获取帮助

- 📧 技术支持: [cbg_rpa_ml@iflytek.com](mailto:cbg_rpa_ml@iflytek.com)
- 💬 社区讨论: [GitHub Discussions](https://github.com/iflytek/astron-rpa/discussions)
- 🐛 问题反馈: [Issues](https://github.com/iflytek/astron-rpa/issues)

## 📄 开源协议

本项目基于 [开源协议](LICENSE) 开源。

---

<div align="center">

**由科大讯飞开发维护**

[![Follow](https://img.shields.io/github/followers/iflytek?style=social&label=关注)](https://github.com/iflytek)
[![Star](https://img.shields.io/github/stars/iflytek/astron-rpa?style=social&label=Star)](https://github.com/iflytek/astron-rpa)
[![Fork](https://img.shields.io/github/forks/iflytek/astron-rpa?style=social&label=Fork)](https://github.com/iflytek/astron-rpa/fork)
[![Watch](https://img.shields.io/github/watchers/iflytek/astron-rpa?style=social&label=关注)](https://github.com/iflytek/astron-rpa/watchers)

**AstronRPA** - 让 RPA 开发变得简单而强大！

如果您觉得这个项目对您有帮助，请给我们一个 ⭐ Star！

</div>