<script lang="tsx">
import { CloseOutlined } from '@ant-design/icons-vue'
import { Form, Spin } from 'ant-design-vue'

import type { DialogOption } from '@/views/Arrange/components/customDialog/types'

import createUserFormItem from '../hooks/createUserFormItem'
import useUserFormDialog from '../hooks/useUserFormDialog'

export default {
  name: 'UserFormDialog',
  components: {},
  props: {
    option: {
      type: {} as DialogOption,
      default() {
        return {}
      },
    },
  },
  emits: ['close'],
  setup(props, { emit }) {
    const { createItemFn } = createUserFormItem()
    const {
      formRef,
      dialogType,
      optionData,
      formState,
      handleClose,
      renderFooterBtns,
    } = useUserFormDialog(props, emit)
    const IntroFn = () => {
      return (
        <div data-tauri-drag-region class="userform" style={{ paddingTop: `${dialogType.value === 'basic' ? '10px' : '0'}` }}>
          <div data-tauri-drag-region class="userform-header">
            <div>{ optionData.value.title }</div>
            <CloseOutlined class="text-[rgba(0,0,0,0.65)] dark:text-[rgba(255,255,255,0.65)] cursor-pointer" onClick={handleClose} />
          </div>
          <div data-tauri-drag-region class="userform-content" style={optionData.value.mode === 'modal' ? { maxHeight: '350px' } : {}}>
            <Form
              ref={formRef}
              layout="vertical"
              model={formState.value}
            >
              {
                optionData.value?.itemList?.length
                  ? optionData.value?.itemList.map((formItem) => {
                      const formItemRules = [
                        ...(formItem?.rules || []),
                        ...(formItem?.required ? [{ required: true, message: `${formItem.label}不能为空` }] : []),
                      ]
                      return (
                        <Form.Item class="mb-3" label={formItem.label} name={formItem.bind} rules={formItemRules}>
                          {createItemFn[formItem.dialogFormType](formItem, formState.value)}
                        </Form.Item>
                      )
                    })
                  : <Spin tip="加载中..." />
              }
            </Form>
          </div>
          <div class="userform-footer">
            { renderFooterBtns(optionData.value.buttonType) }
          </div>
        </div>
      )
    }
    return () => IntroFn()
  },
}
</script>

<style lang="scss">
.userform {
  background: $color-bg-container;
  width: 100%;
  height: 100%;
  border-radius: 4px;
  padding: 0 10px 10px 10px;
  &-header {
    font-size: 16px;
    font-weight: 400;
    height: 6%;
    min-height: 30px;
    line-height: 50px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 14px;
  }
  &-content {
    height: 88%;
    max-height: calc(100% - 60px);
    overflow: hidden;
    overflow-y: auto;
    padding: 10px 14px;
    padding-top: 0;
    &::-webkit-scrollbar {
      width: 0;
      height: 0;
    }
    .ant-select-dropdown {
      position: relative;
      z-index: 9999;
    }
    .ant-spin-spinning {
      position: relative;
      display: inline-block;
      opacity: 1;
      top: 50%;
      left: 40%;
      margin-top: 20%;
    }
  }
  &-footer {
    height: 6%;
    min-height: 30px;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 10px 14px;
    button {
      margin-left: 10px;
    }
  }
}
</style>
