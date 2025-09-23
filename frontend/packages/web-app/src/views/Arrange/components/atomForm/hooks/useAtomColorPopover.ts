import type { Ref } from 'vue'

import { createColorLinearGradient, hex2rgb } from '@/views/Arrange/utils/colorPicker'

// 渲染面板颜色
export function renderSaturationColor(color: string, canvasSaturationRef: Ref<HTMLCanvasElement>) {
  const canvas: any = canvasSaturationRef.value
  const height = canvas.height
  const width = canvas.width
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = color
  ctx.fillRect(0, 0, width, height)
  createColorLinearGradient('l', ctx, width, height, '#FFFFFF', 'rgba(255,255,255,0)')
  createColorLinearGradient('p', ctx, width, height, 'rgba(0,0,0,0)', '#000000')
}

// 渲染调色器颜色
export function renderBarColor(canvasBarRef: Ref<HTMLCanvasElement>) {
  const canvas: any = canvasBarRef.value
  const ctx = canvas.getContext('2d')
  const width = canvas.width
  const height = canvas.height
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, '#FF0000') // red
  gradient.addColorStop(0.17 * 1, '#FF00FF') // purple
  gradient.addColorStop(0.17 * 2, '#0000FF') // blue
  gradient.addColorStop(0.17 * 3, '#00FFFF') // green
  gradient.addColorStop(0.17 * 4, '#00FF00') // green
  gradient.addColorStop(0.17 * 5, '#FFFF00') // yellow
  gradient.addColorStop(1, '#FF0000') // red
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)
}

// 获取颜色面板canvas上的颜色
export function getColorOnCanvas(canvasSaturationRef: Ref<HTMLCanvasElement>, e: MouseEvent) {
  const canvas: any = canvasSaturationRef.value
  const height = canvas.height
  const width = canvas.width
  let x = e.offsetX
  let y = e.offsetY
  if (x < 0)
    x = 0
  if (x > width)
    x = width
  if (y < 0)
    y = 0
  if (y > height)
    y = height
  const pointPosition = {
    top: `${y - 5}px`,
    left: `${x - 5}px`,
  }
  const ctx = canvas.getContext('2d')
  const imageData = ctx.getImageData(Math.max(x - 5, 0), Math.max(0, y - 5), 1, 1)
  return {
    pointPosition,
    imageData,
  }
}

// 获取rgb颜色
export function getRgbColor(color: any) {
  let rgb: any = { r: '0', g: '0', b: '0' }
  if (typeof color !== 'string') {
    rgb = { r: color[0], g: color[1], b: color[2] }
  }
  else {
    if (!color.includes('#')) {
      const [r, g, b] = color.split(',')
      rgb = { r, g, b }
    }
    else {
      rgb = hex2rgb(color)
    }
  }
  return rgb
}

export default function useAtomColorPopover() { }
