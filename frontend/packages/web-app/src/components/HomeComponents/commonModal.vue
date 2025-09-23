<script>
import { FormModel, Icon, Input, message } from 'ant-design-vue'
import { mapGetters } from 'vuex'

import {
  checkResourceName,
  downloadToLocal,
  getLocalNameType,
  publishResource,
  updateInfo,
  uploadToCloud,
} from '@/renderer/api/http/local'
import {
  MODE_LOCAL,
  RESOURCE_COMPONENT,
  RESOURCE_LABEL,
  RESOURCE_PROJECT,
  RESOURCE_ROBOT,
} from '@/renderer/AppPostTask/views/PostTaskList/postConfig/baseConfig/config'
import system from '@/renderer/store/modules/system'
import { access, accessSync, mkdirSync, stat } from '@/renderer/utils/fileSystem'
import { creatUuid } from '@/renderer/utils/fileUtils'
import { getLatestCopyPath, getLatestDownloadPath } from '@/renderer/utils/globalUtils'
import { checkFloder } from '@/renderer/utils/regValidate'
import { copyToTarget } from '@/renderer/utils/utils'

const os = window.require('os')
const remote = window.require('@electron/remote')
const { dialog } = remote
const win = remote.getCurrentWindow()

const { DATA_PATH } = system.state.CONFIG_DATA || {}

const SCREATE_COPY = '创建副本'
const PROJECT_VERSION_SNAPSHOT = '版本快照'
const MODIFY_PROJECT_NAME = '重命名'
const DOWNLOAD_TO_LOCAL = '下载至本地列表'
const UPLOAD_TO_CLOUD = '上传至云端'

const DUPLICATE = 'duplicate' // 副本类型
const SNAPSHOT = 'snapshot' // 版本快照类型

const FN = {
  [SCREATE_COPY]: publishResource,
  [PROJECT_VERSION_SNAPSHOT]: publishResource,
  [MODIFY_PROJECT_NAME]: updateInfo,
  [DOWNLOAD_TO_LOCAL]: downloadToLocal,
  [UPLOAD_TO_CLOUD]: uploadToCloud,
}
const TYPE_TEXT_CONFIG = {
  [RESOURCE_PROJECT]: '工程名称',
  [RESOURCE_COMPONENT]: '组件名称',
  [RESOURCE_ROBOT]: '机器人名称',
}

export default {
  name: 'CommonModal',
  props: {
    showModal: {
      type: Boolean,
      default() {
        return false
      },
    },
    options: {
      type: Object,
      default() {
        return {}
      },
    },
  },
  data() {
    return {
      title: '',
      versionDes: '',
      confirmLoading: false,
      submitInfo: {
        name: '',
        path: '',
      },
      rules: {
        name: [
          { required: true, message: '名称不能为空！', trigger: 'blur' },
          {
            max: 32,
            message: '请不要超过32个字符！',
            trigger: ['change', 'blur'],
          },
        ],
        path: [
          { required: true, message: '地址不能为空！', trigger: 'blur' },
          { validator: checkFloder, trigger: 'blur' },
        ],
      },
    }
  },
  computed: {
    ...mapGetters({
      getUserPath: 'global/getUserPath',
    }),
  },
  mounted() {
    const { title, resourceName, copyIndex } = this.options
    title && (this.title = title)
    resourceName && (this.submitInfo.name = copyIndex ? `${resourceName}副本${copyIndex}` : resourceName)
    // 读数据库看上次用户保存的路径是什么，优先用户上次选择的路径，如果没有再使用默认路径
    this.title === DOWNLOAD_TO_LOCAL
    && getLatestDownloadPath().then((downloadPath) => {
      console.log('downloadPath>>>>>>>>>>>>>', downloadPath)
      this.submitInfo.path
        = downloadPath.length > 0 && downloadPath[0]
          ? downloadPath[0]
          : `${this.getUserPath}\\Documents\\${DATA_PATH}\\Download`
      // 判断默认存储目录是否已存在
      stat(this.submitInfo.path).then(({ err, stats }) => {
        if (!err) {
          !stats.isDirectory && mkdirSync(this.submitInfo.path, { recursive: true })
        }
        else {
          mkdirSync(this.submitInfo.path, { recursive: true })
        }
      })
    })
    const { mode } = this.options
    // 读数据库看上次用户保存的路径是什么，优先用户上次选择的路径，如果没有再使用默认路径
    if (this.title === SCREATE_COPY && mode === MODE_LOCAL) {
      getLatestCopyPath().then((copyPath) => {
        console.log('copyPath>>>>>>>>>>>>>', copyPath)
        this.submitInfo.path
          = copyPath.length > 0 && copyPath[0] ? copyPath[0] : `${this.getUserPath}\\Documents\\${DATA_PATH}\\Download`
        // 判断默认存储目录是否已存在
        stat(this.submitInfo.path).then(({ err, stats }) => {
          if (!err) {
            !stats.isDirectory && mkdirSync(this.submitInfo.path, { recursive: true })
          }
          else {
            mkdirSync(this.submitInfo.path, { recursive: true })
          }
        })
      })
    }
  },
  methods: {
    handleOkConfirm() {
      this.confirmLoading = true
      this.$refs.baseForm.validate((volid) => {
        this.confirmLoading = false
        if (volid) {
          this.handleOk()
        }
      })
    },
    handleOk() {
      this.confirmLoading = true
      const { resourceType, resourceId, dataPath, mode, resourceName, resourcePath } = this.options
      const defaultPath = `${os.homedir()}\\AppData\\Local\\${DATA_PATH}\\resources\\default`
      access(defaultPath).then(async (defaultError) => {
        if (defaultError) {
          mkdirSync(defaultPath)
        }
        const targetPath = `${defaultPath}\\${resourceId}`
        if (this.title === SCREATE_COPY || this.title === MODIFY_PROJECT_NAME) {
          let checkRes
          try {
            checkRes = await checkResourceName({
              resourceName: this.submitInfo.name,
              resourceType,
              mode,
            })
            if (checkRes.data === '0') {
              this.confirmLoading = false
              const msgTip = this.title === SCREATE_COPY ? '副本名称重复！请重新命名' : '名称重复！请重新命名'
              message.error(msgTip)
              return false
            }
          }
          catch {
            this.confirmLoading = false
          }
        }
        let params = {
          resourceType,
          resourceId,
        }
        let result
        const needSet = false // 是否需要存储到vuex中
        switch (this.title) {
          case SCREATE_COPY:
            params = {
              ...params,
              mode,
              destType: DUPLICATE,
              destId: creatUuid(resourceType, needSet),
              destName: this.submitInfo.name,
            }
            if (mode === MODE_LOCAL) {
              // 1.校验路径是否存在
              try {
                accessSync(this.submitInfo.path)
              }
              catch {
                message.error('保存位置不正确！')
                this.confirmLoading = false
              }
              params.destPath = `${this.submitInfo.path}`
            }
            break
          case PROJECT_VERSION_SNAPSHOT:
            params = {
              ...params,
              mode,
              destType: SNAPSHOT,
              destId: resourceId,
              destName: resourceName,
              destVersion: this.options.versionIndex,
              destVersionDesc: this.versionDes,
            }
            break
          case MODIFY_PROJECT_NAME:
            params = {
              ...params,
              mode,
              resourceName: this.submitInfo.name,
            }
            break
          case DOWNLOAD_TO_LOCAL:
            params = {
              ...params,
              dataPath,
              resourcePath: this.submitInfo.path,
              resourceId: creatUuid(RESOURCE_PROJECT, false),
              resourceName: this.submitInfo.name,
            }
            // 1.校验路径是否存在
            try {
              accessSync(this.submitInfo.path)
            }
            catch {
              message.error('保存位置不正确！')
              this.confirmLoading = false
            }
            if ([RESOURCE_ROBOT, RESOURCE_COMPONENT].includes(this.options.resourceType)) {
              params.resourceId = this.options.resourceId
              params.ResourceVersion = ''
            }
            // 2.校验该路径是否已存在该云端工程
            try {
              result = await getLocalNameType({
                resourcePath: `${this.submitInfo.path}\\${this.submitInfo.name}`,
              })
              if (result?.data?.resourceName === this.submitInfo.name) {
                message.error('本地已存在该资源！')
                this.confirmLoading = false
              }
            }
            catch (err) {
              console.log(err)
            }
            break
          case UPLOAD_TO_CLOUD:
            checkResourceName({
              resourceName: this.submitInfo.name,
              resourceType,
              mode: 'cloud',
            }).then((res) => {
              if (res.data === '0') {
                message.error('存在同名云端工程！请重新命名')
                this.confirmLoading = false
              }
              else {
                const origin = this.$router.currentRoute.name
                copyToTarget(resourcePath, targetPath, true, origin)
                this.$ipcRenderer.once('fse-copy-callback', () => {
                  uploadToCloud({
                    resourceType,
                    resourceId: creatUuid(RESOURCE_PROJECT, false),
                    resourcePath: targetPath,
                    resourceName: this.submitInfo.name,
                  })
                    .then((r) => {
                      this.confirmLoading = false
                      r.code && message.success('上传成功！')
                      this.handleCancel()
                    })
                    .catch(() => {
                      this.confirmLoading = false
                    })
                })
              }
            })
            break
          default:
            break
        }
        if (this.confirmLoading && this.title !== UPLOAD_TO_CLOUD) {
          FN[this.title]({
            ...params,
          })
            .then((res) => {
              if (res.code) {
                this.confirmLoading = false
                this.$emit('handleBack', {
                  ...this.options,
                  savePath: this.submitInfo.path,
                  newName: this.submitInfo?.name || '',
                })
                this.handleCancel()
              }
              else {
                this.confirmLoading = false
              }
            })
            .catch(() => {
              this.confirmLoading = false
            })
        }
      })
    },
    handleCancel() {
      this.confirmLoading ? message.warning('有操作正在进行，请稍后再试！') : this.$emit('cancel')
    },
    getDirectory() {
      return (
        <Input onChange={() => this.clearValidate('path')} v-model={this.submitInfo.path}>
          <div slot="suffix" class="modal-icon">
            <Icon type="ellipsis" onClick={() => this.handleOpenFile()} />
          </div>
        </Input>
      )
    },
    handleOpenFile() {
      win.focus()
      dialog
        .showOpenDialog(win, {
          title: '选择保存文件目录',
          properties: ['openDirectory'],
        })
        .then((result) => {
          if (result.filePaths.length) {
            this.submitInfo.path = result?.filePaths[0]
            this.clearValidate('path')
          }
        })
    },
    clearValidate(props) {
      this.$refs.baseForm.clearValidate(props)
    },
    getContent() {
      switch (this.title) {
        case SCREATE_COPY:
        case MODIFY_PROJECT_NAME:
        case UPLOAD_TO_CLOUD:
          return (
            <FormModel
              ref="baseForm"
              props={{ model: this.submitInfo }}
              rules={this.rules}
              labelCol={{
                span: this.options.resourceType === RESOURCE_ROBOT ? 6 : 4,
              }}
              wrapperCol={{
                span: this.options.resourceType === RESOURCE_ROBOT ? 16 : 18,
              }}
            >
              <FormModel.Item prop="name" label={`${RESOURCE_LABEL[this.options.resourceType]}名称`}>
                <Input v-select-all onChange={() => this.clearValidate('name')} v-model={this.submitInfo.name} />
              </FormModel.Item>
              {this.options.mode === MODE_LOCAL && this.title === SCREATE_COPY && (
                <FormModel.Item prop="path" label="保存位置">
                  {this.getDirectory()}
                </FormModel.Item>
              )}
            </FormModel>
          )
        case DOWNLOAD_TO_LOCAL:
          return (
            <FormModel
              ref="baseForm"
              props={{ model: this.submitInfo }}
              rules={this.rules}
              labelCol={{ span: 6 }}
              wrapperCol={{ span: 18 }}
            >
              <FormModel.Item prop="name" label={TYPE_TEXT_CONFIG[this.options.resourceType]}>
                <Input onChange={() => this.clearValidate('name')} v-model={this.submitInfo.name} />
              </FormModel.Item>
              <FormModel.Item prop="path" label="保存位置">
                {this.getDirectory()}
              </FormModel.Item>
            </FormModel>
          )
        case PROJECT_VERSION_SNAPSHOT:
          return (
            <FormModel
              ref="baseForm"
              props={{ model: this.submitInfo }}
              rules={this.rules}
              labelCol={{ span: 6 }}
              wrapperCol={{ span: 16 }}
            >
              <FormModel.Item label="版本名称">
                <span>{`版本${this.options.versionIndex}`}</span>
              </FormModel.Item>
              <FormModel.Item label="版本快照说明">
                <Input.TextArea
                  v-select-all
                  placeholder="请输入本次版本快照说明，长度请限制在50个字符以内"
                  maxLength={50}
                  v-model={this.versionDes}
                />
              </FormModel.Item>
            </FormModel>
          )
        default:
          break
      }
    },
  },
  render() {
    return (
      <a-modal
        v-modal:open={this.showModal}
        width={500}
        title={this.title}
        onOk={this.handleOkConfirm}
        confirmLoading={this.confirmLoading}
        onCancel={this.handleCancel}
      >
        <div class="commonModal">{this.getContent()}</div>
      </a-modal>
    )
  },
}
</script>

<style lang="scss">
.pick-btn {
  text-align: center;
}
.pick-quit {
  height: 32px;
  line-height: 32px;
}
</style>
