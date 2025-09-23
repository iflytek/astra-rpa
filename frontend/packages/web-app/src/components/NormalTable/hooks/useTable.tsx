// import { Button } from 'ant-design-vue'
import { debounce } from 'lodash-es'

import useTableFormItem from './useTableFormItem'

export default function useTable() {
  const { createHomeForm } = useTableFormItem()
  function renderHeaderForm(formOption) {
    // /**
    //  * 生成查询按钮
    //  */
    // const renderSearchBtn = (item) => {
    //   const nodeProps = { ...item }
    //   delete nodeProps.componentType
    //   delete nodeProps.hidden
    //   delete nodeProps.text
    //   const searchFn = debounce(() => {
    //     item.itemFunc ? item.itemFunc() : formOption.searchFn?.()
    //   }, 300)
    //   return (
    //     <Button
    //       class={item.hidden ? 'hide' : ''}
    //       type="primary"
    //       {...nodeProps}
    //       onClick={searchFn}
    //     >
    //       {item.text || '查询'}
    //     </Button>
    //   )
    // }
    const searchFn = debounce(() => formOption.searchFn?.(), 300)

    return (
      <div class="nTable-header_forms">
        {formOption.formList?.map((item) => {
          const createFn = createHomeForm[item.componentType]
          const formItem = createFn?.(item, formOption.params, searchFn) ?? item.render?.()
          return (
            <div class={`text-[14px] formItem${item.hidden ? ' hide' : ''}`}>
              {item.label && (
                <span>{`${item.label}：`}</span>
              )}
              {formItem}
            </div>
          )
        })}
      </div>
    )
  }
  function renderHeaderButton(buttonOption) {
    return (
      <div class="nTable-header_btns">
        {buttonOption.buttonList?.map(item => createHomeForm.button(item))}
      </div>
    )
  }

  return {
    renderHeaderForm,
    renderHeaderButton,
  }
}
