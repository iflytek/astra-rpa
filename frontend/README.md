# AstronRPA Frontend

<div align="center">

**🎨 Modern Frontend Platform for RPA Applications**

[![Node.js](https://img.shields.io/badge/node.js-22+-green.svg)](https://nodejs.org/)
[![Vue](https://img.shields.io/badge/vue-3+-4FC08D.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-5.9+-blue.svg)](https://www.typescriptlang.org/)
[![pnpm](https://img.shields.io/badge/pnpm-9+-orange.svg)](https://pnpm.io/)
[![Tauri](https://img.shields.io/badge/tauri-1.6+-purple.svg)](https://tauri.app/)

English | [简体中文](README.zh.md)

</div>

## 📑 Table of Contents

- [AstronRPA Frontend](#astronrpa-frontend)
  - [📑 Table of Contents](#-table-of-contents)
  - [📋 Overview](#-overview)
  - [✨ Key Features](#-key-features)
  - [🛠️ Tech Stack](#️-tech-stack)
  - [🚀 Quick Start](#-quick-start)
    - [System Requirements](#system-requirements)
    - [Development Setup](#development-setup)
    - [Build \& Deploy](#build--deploy)
  - [📦 Package Structure](#-package-structure)
    - [Core Packages](#core-packages)
    - [Development Tools](#development-tools)
  - [🏗️ Architecture Overview](#️-architecture-overview)
    - [Technology Stack Details](#technology-stack-details)

## 📋 Overview

AstronRPA Frontend is a modern frontend platform built for RPA applications. It provides a comprehensive solution for building both web-based and desktop RPA applications with a unified codebase.

The platform features a monorepo architecture using pnpm workspaces, supporting multiple application types including web applications, desktop applications (via Tauri), and browser plugins, all sharing common components and utilities.

## ✨ Key Features

- 🚀 **High Performance** - Vite-powered build system with optimized bundling and lazy loading
- 🔒 **Type Safety** - Full TypeScript support with strict type checking
- 🔧 **Easy Integration** - Modular package structure with workspace dependencies
- 📊 **Real-time Development** - Hot module replacement and fast refresh
- 🌍 **Multi-Platform Support** - Web, desktop (Tauri), and browser extension support
- 📈 **Scalable Architecture** - Monorepo with shared components and utilities

## 🛠️ Tech Stack

**Frontend Framework**: Vue 3 + TypeScript + Vite
**UI Components**: Ant Design Vue + VXE Table
**Desktop App**: Tauri (Rust + Web Technologies)
**State Management**: Pinia
**Package Manager**: pnpm workspaces
**Testing**: Vitest + Vue Test Utils
**Code Quality**: ESLint + Prettier
**Build Tools**: Vite + Rollup
**Styling**: Sass + Tailwind CSS
**Internationalization**: i18next + vue-i18n

## 🚀 Quick Start

### System Requirements

- **Node.js**: >= 22
- **pnpm**: >= 9
- **Rust**: >= 1.90.0 (for Tauri desktop app)
- **Operating System**: Windows 10/11, macOS, or Linux

### Development Setup

```bash
# Clone the repository
git clone https://github.com/iflytek/astron-rpa.git
cd astron-rpa/frontend

# Install dependencies
pnpm install

# Start web development server
pnpm dev:web

# Start Tauri desktop app (development mode)
pnpm dev:tauri

# Start Tauri log window (development mode)
pnpm dev:tauri-logwin
```

### Build & Deploy

```bash
# Build web application
pnpm build:web

# Build Tauri desktop application
pnpm build:tauri

# Build Tauri desktop application (debug mode)
pnpm build:tauri-debug

# Run tests
pnpm test

# Run tests with UI
pnpm test:ui

# Lint and fix code
pnpm lint:fix

# Generate internationalization files
pnpm i18n
```

## 📦 Package Structure

### Core Packages

- **@rpa/web-app**: Main web application
- **@rpa/tauri-app**: Desktop application (Tauri)
- **@rpa/tauri-app-window**: Tauri log window application
- **@rpa/browser-plugin**: Browser extension
- **@rpa/components**: Shared UI components
- **@rpa/types**: TypeScript type definitions
- **@rpa/tokens**: Design tokens and styling
- **@rpa/locales**: Internationalization resources

### Development Tools

- **ESLint Configuration**: Antfu's ESLint config
- **Testing**: Vitest with UI support
- **Internationalization**: LobeHub i18n CLI
- **Build Tools**: Vite with multiple build modes

## 🏗️ Architecture Overview

```
Frontend Monorepo
├── packages/
│   ├── web-app/           # Vue 3 Web Application
│   ├── tauri-app/         # Tauri Desktop App
│   ├── tauri-app-window/  # Tauri Log Window
│   ├── browser-plugin/    # Browser Extension
│   ├── components/        # Shared Components
│   ├── types/            # Type Definitions
│   ├── tokens/           # Design Tokens
│   └── locales/          # i18n Resources
├── node_modules/         # Dependencies
├── package.json          # Root Package Config
├── pnpm-workspace.yaml   # Workspace Configuration
└── vitest.config.ts      # Test Configuration
```

### Technology Stack Details

**Web Application**

- Vue 3 with Composition API
- TypeScript for type safety
- Vite for build tooling
- Ant Design Vue for UI components
- Pinia for state management
- Vue Router for navigation

**Desktop Application**

- Tauri for native desktop capabilities
- Rust backend with Web frontend
- Native system integration
- Cross-platform compatibility

**Shared Infrastructure**

- pnpm workspaces for monorepo management
- Shared component library
- Common type definitions
- Unified build and test processes
