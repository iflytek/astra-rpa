import { UploadOutlined } from '@ant-design/icons-vue'
import { Checkbox, DatePicker, Input, Radio, Select } from 'ant-design-vue'

import TagInputConfig from '../components/tagInputConfig.vue'
import { fontFamilyMap, fontStyleMap } from '../config'

export default function useConfigFormItem() {
  /**
   * 生成input
   */
  function renderInput(itemData) {
    return <TagInputConfig itemData={itemData} />
  }
  /**
   * 生成密码框
   */
  function renderPassword(itemData) {
    console.log('itemData', itemData)
    return (
      <Input.Password
        v-model:value={itemData.defaultValue.value}
        placeholder={itemData.placeholder.value[0].value}
        allowClear={false}
        readonly
      />
    )
  }
  /**
   * 生成日期（时间）选择器(无范围)
   */
  function renderDatePicker(itemData) {
    return (
      <DatePicker
        style={{ width: '100%' }}
        valueFormat={itemData.format.value}
        format={itemData.format.value}
        showTime={{ format: itemData.format.value.split(' ')[1] }}
        allowClear={false}
        inputReadOnly={true}
        open={false}
      />
    )
  }
  /**
   * 生成文件(夹)选择框
   */
  function renderPathInput(itemData) {
    return (
      <Input
        placeholder={itemData.placeholder.value[0].value}
        allowClear={false}
        suffix={
          <UploadOutlined />
        }
        readonly
      />
    )
  }

  /**
   * 生成checkbox复选框组
   */
  function renderCheckboxGroup(itemData) {
    const verticalStyle = 'display: flex;flex-direction: column;'
    return (
      <Checkbox.Group
        style={`${itemData.direction.value === 'vertical' ? verticalStyle : ''}`}
        v-model:value={itemData.defaultValue.value}
      >
        {
          itemData.options.value.map((op) => {
            return (
              <Checkbox value={op.rId}>
                {
                  op.value.value.map((item) => {
                    return (
                      item.type === 'var' ? <hr class="dialog-tag-input-hr" data-name={item.value}></hr> : item.value
                    )
                  })
                }
              </Checkbox>
            )
          })
        }
      </Checkbox.Group>
    )
  }
  /**
   * 生成radio单选框组
   */
  function renderRadioGroup(itemData) {
    const verticalStyle = 'display: flex;flex-direction: column;'
    return (
      <Radio.Group
        style={`${itemData.direction.value === 'vertical' ? verticalStyle : ''}`}
        v-model:value={itemData.defaultValue.value}
      >
        {
          itemData.options.value.map((op) => {
            return (
              <Radio value={op.rId}>
                {
                  op.value.value.map((item) => {
                    return (
                      item.type === 'var' ? <hr class="dialog-tag-input-hr" data-name={item.value}></hr> : item.value
                    )
                  })
                }
              </Radio>
            )
          })
        }
      </Radio.Group>
    )
  }
  // 单选
  function renderSingleSelect(itemData) {
    return renderSelect(itemData, null)
  }
  // 多选
  function renderMultiSelect(itemData) {
    return renderSelect(itemData, 'multiple')
  }
  /**
   * 生成select下拉框
   */
  function renderSelect(itemData, mode) {
    return (
      <Select
        mode={mode}
        placeholder={itemData.placeholder.value[0].value}
        allowClear={false}
        v-model:value={itemData.defaultValue.value}
      >
        {
          itemData.options.value.map((op) => {
            return (
              <Select.Option value={op.rId} disabled>
                {
                  op.value.value.map((item) => {
                    return (
                      item.type === 'var' ? <hr class="dialog-tag-input-hr" data-name={item.value}></hr> : item.value
                    )
                  })
                }
              </Select.Option>
            )
          })
        }
      </Select>
    )
  }

  /**
   * 生成文本描述区
   */
  function renderTextDesc(itemData) {
    const finalFontFamily = fontFamilyMap[itemData.fontFamily.value || 'msyh']
    const finalFontStyle = itemData.fontStyle.value.map(style => fontStyleMap[style]).join(';')

    return (
      <p
        style={`font-size: ${itemData.fontSize.value}px;${finalFontFamily};${finalFontStyle}`}
      >
        { itemData.textContent?.value[0]?.value || '' }
      </p>
    )
  }

  return {
    createItemFn: {
      INPUT: renderInput,
      PASSWORD: renderPassword,
      DATEPICKER: renderDatePicker,
      PATH_INPUT: renderPathInput,
      CHECKBOX_GROUP: renderCheckboxGroup,
      RADIO_GROUP: renderRadioGroup,
      SINGLE_SELECT: renderSingleSelect,
      MULTI_SELECT: renderMultiSelect,
      TEXT_DESC: renderTextDesc,
    },
  }
}
