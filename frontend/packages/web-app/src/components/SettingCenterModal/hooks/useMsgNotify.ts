import { message } from 'ant-design-vue'
import type { Rule } from 'ant-design-vue/es/form'
import { isEmpty } from 'lodash-es'
import { onBeforeUnmount, ref } from 'vue'
import type { Ref } from 'vue'

import { toolsInterfacePost } from '@/api/setting'
import useUserSettingStore from '@/stores/useUserSetting.ts'

export function useNotify() {
  const emailRef = ref()
  const initEmailData = {
    is_enable: false, // 是否启用, 默认不启用
    receiver: '', // 收件人
    is_default: true, // 默认不起用其他邮箱
    mail_server: '', // 发件服务器
    mail_port: '', // 端口
    sender_mail: '', // 邮件账号
    password: '', // 邮件密码(需要使用密钥，存储的也是密钥名称)
    use_ssl: true, // 是否SSL
    cc: '', // 抄送
  }
  const initPhoneData = {
    is_enable: false, // 是否启用, 默认不启用
    receiver: '', // 收件人手机号
    phone_msg_url: 'https://pretest.xfpaas.com/dripsms/smssafe',
  }
  const email: Ref<RPA.EmailFormMap> = ref(JSON.parse(JSON.stringify(initEmailData)))
  const emailFormRules: Record<string, Rule[]> = {
    receiver: [
      { required: true, message: '请输入收件箱地址', trigger: 'blur' },
      {
        pattern: /\w[-\w.+]*@([A-Z0-9][-A-Z0-9]+\.)+[A-Z]{2,14}/i,
        message: '邮箱地址格式错误',
        trigger: 'blur',
      },
    ],
    mail_server: [{ required: true, message: '请输入邮箱服务器', trigger: 'blur' }],
    mail_port: [{ required: true, message: '请输入邮箱端口号', trigger: 'blur' }],
    sender_mail: [
      { required: true, message: '请输入发件箱地址！', trigger: 'blur' },
      {
        pattern: /\w[-\w.+]*@([A-Z0-9][-A-Z0-9]+\.)+[A-Z]{2,14}/i,
        message: '邮箱地址格式错误！',
        trigger: 'blur',
      },
    ],
    password: [{ required: true, message: '请输入密钥', trigger: 'blur' }],
  }
  const phoneRef = ref()
  const phone_msg: Ref<RPA.PhoneFormMap> = ref(JSON.parse(JSON.stringify(initPhoneData)))
  const phoneFormRules: Record<string, Rule[]> = {
    receiver: [
      // /0?(13|14|15|18)[0-9]{9}/
      { required: true, message: '请输入手机号码', trigger: 'blur' },
      {
        pattern: /^1([3-9])\d{9}$/,
        message: '手机号码格式错误！',
        trigger: 'blur',
      },
    ],
  }

  function handleMsgTest(key: string) {
    console.log('handleMsgTest', key)
    handleValidateSave().then(() => {
      toolsInterfacePost({
        alert_type: key,
      }).then((res) => {
        message.success(res.msg || '测试成功')
      })
      message.info(`${key === 'mail' ? '邮箱' : '短信'}测试已发送，可稍后查看！`)
    })
  }
  function errorSave() {
    let newSetting
    if (email.value.is_enable) {
      newSetting = {
        msgNotifyForm: {
          email: JSON.parse(JSON.stringify(initEmailData)),
          phone_msg: phone_msg.value,
        },
      }
    }
    else {
      newSetting = {
        msgNotifyForm: {
          email: email.value,
          phone_msg: JSON.parse(JSON.stringify(initPhoneData)),
        },
      }
    }
    useUserSettingStore().saveUserSetting(newSetting)
  }
  function handleValidateSave() {
    return new Promise((resolve, reject) => {
      const currRef = email.value.is_enable ? emailRef : phoneRef
      currRef.value.validate().then(() => {
        const newSetting = {
          msgNotifyForm: {
            email: email.value,
            phone_msg: phone_msg.value,
          },
        }
        useUserSettingStore().saveUserSetting(newSetting)
        resolve({})
      }).catch(() => {
        reject(new Error('未通过校验'))
      })
    })
  }

  function initData() {
    const msgNotifyForm = useUserSettingStore().userSetting?.msgNotifyForm || {} as RPA.MessageFormMap
    const { email: emailData, phone_msg: phoneData } = msgNotifyForm
    if (emailData && !isEmpty(emailData)) {
      email.value = emailData
    }
    if (phoneData && !isEmpty(phoneData)) {
      phone_msg.value = phoneData
    }
  }
  initData()

  onBeforeUnmount(() => {
    handleValidateSave().catch(() => { errorSave() })
  })
  return {
    emailRef,
    email,
    emailFormRules,
    phoneRef,
    phone_msg,
    phoneFormRules,
    handleValidateSave,
    handleMsgTest,
  }
}
