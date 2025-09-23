<script setup lang="ts">
import { message } from 'ant-design-vue'
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'

import { getColorOnCanvas, getRgbColor, renderBarColor, renderSaturationColor } from '@/views/Arrange/components/atomForm/hooks/useAtomColorPopover'
import { createDom } from '@/views/Arrange/components/atomForm/hooks/useAtomVarPopover'
import { DEFAULT_COLOR_LIST, ORIGIN_BUTTON } from '@/views/Arrange/config/atom'
import { isHex, isRgb, rgb2hex, rgb2hsv } from '@/views/Arrange/utils/colorPicker.ts'

const { initColor, renderData } = defineProps({
  initColor: {
    type: String,
    default: '#000000',
  },
  renderData: {
    type: Object as () => RPA.AtomDisplayItem,
    default: () => ({}),
  },
})

const emit = defineEmits(['closePopover'])

// 默认颜色列表
const colorsDefault = reactive(DEFAULT_COLOR_LIST)
const canvasSaturationRef = ref(null)
const canvasBarRef = ref(null)
const position = reactive({
  pointPosition: {
    top: '0px',
    left: '0px',
  },
  slideBarStyle: {},
})
const attr = reactive({
  modelRgb: '',
  modelHex: '',
  r: 0,
  g: 0,
  b: 0,
  h: 0,
  s: 0,
  v: 0,
})
const rgbString = computed(() => {
  return `rgb(${attr.r}, ${attr.g}, ${attr.b})`
})

watch(() => initColor, (newVal) => {
  selectColor(newVal)
})

// 颜色面板点击
function selectSaturation(e: MouseEvent) {
  const { pointPosition, imageData } = getColorOnCanvas(canvasSaturationRef, e)
  position.pointPosition = pointPosition
  setRGBHSV(imageData.data)
  attr.modelHex = rgb2hex({ r: attr.r, g: attr.g, b: attr.b }, true)
}

// 颜色条选中
function selectBar(e: any) {
  const canvas: any = canvasBarRef.value
  const { top: BarTop, height } = canvas.getBoundingClientRect()
  const ctx = e.target.getContext('2d')
  const mousemove = (e: any) => {
    let y = e.clientY - BarTop
    if (y < 0)
      y = 0
    if (y > height)
      y = height
    position.slideBarStyle = {
      top: `${y - 2}px`,
    }
    // 先获取颜色条上的颜色在颜色面板上进行渲染
    const imgData = ctx.getImageData(0, Math.min(y, height - 1), 1, 1)
    const [r, g, b] = imgData.data
    renderSaturationColor(`rgb(${r},${g},${b})`, canvasSaturationRef)
    // 再根据颜色面板上选中的点的颜色，来修改输入框的值
    nextTick(() => {
      const canvas: any = canvasSaturationRef.value
      const ctx = canvas.getContext('2d')
      const pointX = Number.parseFloat(position.pointPosition.left)
      const pointY = Number.parseFloat(position.pointPosition.top)
      const pointRgb = ctx.getImageData(Math.max(0, pointX), Math.max(0, pointY), 1, 1)
      setRGBHSV(pointRgb.data)
      attr.modelHex = rgb2hex({ r: attr.r, g: attr.g, b: attr.b }, true)
    })
  }
  mousemove(e)
  const mouseup = () => {
    document.removeEventListener('mousemove', mousemove)
    document.removeEventListener('mouseup', mouseup)
  }
  document.addEventListener('mousemove', mousemove)
  document.addEventListener('mouseup', mouseup)
}

// 默认颜色选择区选择颜色
function selectColor(color: string) {
  setRGBHSV(color)
  attr.modelRgb = rgbString.value.substring(4, rgbString.value.length - 1)
  attr.modelHex = rgb2hex({ r: attr.r, g: attr.g, b: attr.b }, true)
  renderSaturationColor(rgbString.value, canvasSaturationRef)
  position.pointPosition = {
    left: `${Math.max(attr.s * 150 - 5, 0)}px`,
    top: `${Math.max((1 - attr.v) * 80 - 5, 0)}px`,
  }
  renderSlide()
}

// 调色卡的位置
function renderSlide() {
  position.slideBarStyle = {
    top: `${(1 - attr.h / 360) * 78}px`,
  }
}

// hex输入框失去焦点
function inputHex() {
  if (isHex(attr.modelHex)) {
    selectColor(attr.modelHex)
  }
  else {
    message.error('请输入3位或者6位合法十六进制值')
  }
}
function inputRgb() {
  if (isRgb(attr.modelRgb)) {
    const [r, g, b] = attr.modelRgb.split(',')
    const hex = rgb2hex({ r, g, b }, true)
    attr.modelHex = hex
    selectColor(attr.modelHex)
  }
  else {
    message.error('请输入合法的rgb数值')
  }
}

// color可能是 #fff 也可能是 123,21,11  这两种格式
function setRGBHSV(color: any, initHex = false) {
  const rgb = getRgbColor(color)
  const hsv = rgb2hsv(rgb)
  Object.keys(rgb).forEach(item => attr[item] = rgb[item])
  Object.keys(hsv).forEach(item => attr[item] = hsv[item])
  if (initHex)
    attr.modelHex = rgb2hex(rgb, true)
  attr.modelRgb = rgbString.value.substring(4, rgbString.value.length - 1)
}

function clearColor() {
  selectColor(initColor)
}

// 确认选择的颜色
function changeColor() {
  if (!isHex(attr.modelHex) || !isRgb(attr.modelRgb))
    return
  createDom({ val: attr.modelRgb }, renderData, ORIGIN_BUTTON)
  emit('closePopover')
}

onMounted(() => {
  selectColor(initColor)
  renderBarColor(canvasBarRef)
})
</script>

<template>
  <div class="color-picker">
    <div class="color-panel">
      <ul class="colors color-box">
        <li
          v-for="item in colorsDefault" :key="item" class="item" :style="{ background: item }"
          @click="selectColor(item)"
        />
      </ul>
      <div class="color-set">
        <!-- 颜色面板 -->
        <div class="saturation" @mousedown.prevent.stop="selectSaturation">
          <canvas ref="canvasSaturationRef" width="150" height="80" />
          <div :style="position.pointPosition" class="slide" />
        </div>
        <!-- 颜色卡条 -->
        <div class="bar" @mousedown.prevent.stop="selectBar">
          <canvas ref="canvasBarRef" width="12" height="80" />
          <div :style="position.slideBarStyle" class="slide" />
        </div>
      </div>
    </div>
    <!-- 颜色预览和颜色输入 -->
    <div class="color-view">
      <!-- 颜色预览区 -->
      <div :style="{ background: rgbString }" class="color-show" />
      <!-- 颜色输入区 -->
      <div class="input">
        <div class="color-type">
          <span class="name"> HEX </span>
          <input v-model="attr.modelHex" class="value" @blur="inputHex">
        </div>
        <div class="color-type">
          <span class="name"> RGB </span>
          <input v-model="attr.modelRgb" class="value" @blur="inputRgb">
        </div>
      </div>
    </div>
    <!-- 默认颜色列表选择区 -->
    <div class="btn">
      <button class="clear-btn" @click="clearColor">
        清空
      </button>
      <button class="confirm-btn" @click="changeColor">
        确认
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '@/views/Arrange/components/atomForm/style/AtomColorPopover.scss';
</style>
