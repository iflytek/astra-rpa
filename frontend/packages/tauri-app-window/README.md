# 多窗口参数说明

- 除客户端主窗口外，其余子窗口统一走`iflyrpa-window.exe`，该`exe`由前端提供，机器人执行过程中由调度器调起，通过传参的不同渲染不同的页面，实现多窗口方案改造，减小包体积，提升代码可维护性。

- **业务参数**传参

  - 小数据量

    - url - 加载的url,可参照GET请求的query格式追加业务参数，数据格式要求必须是字符串，具体需要传什么样的参数由前端确定后同步后端；

  - 大数据量

    - 针对大数据量的业务参数传参需求，不能追加在url之后，无法一次性接收这么多数据，只能利用标准输入监听进行分批传参，再在渲染页面将分批接收到的数据拼接起来。

    - 关注client-ui项目中的`tauri-app-window`目录下的`main.rs`，可全局搜索`listen_to_stdin`关键词复用大数据量传参的逻辑。

      ```rust
      async fn listen_to_stdin(window: Window) { // 监听标准输入
          let stdin = io::stdin();
          let handle = stdin.lock();
          let win = window.get_window("iflyrpa-window").unwrap();

          for line in handle.lines() {
              match line {
                  Ok(input) => {
                      println!("Received input: {}", input);
                      // 这里可以处理输入，比如发送到主窗口等
                      win.emit("listen_to_stdin", input).unwrap();
                  },
                  Err(e) => eprintln!("Error reading line: {}", e),
              }
          }
      }
      ```

- 常用**窗口参数**单独传参

  - --name
  - --width：已更改为不支持配置，前端优化成子窗口尺寸大小自适应不同分辨率和缩放比
  - --height：已更改为不支持配置，前端优化成子窗口尺寸大小自适应不同分辨率和缩放比
  - --top：设置窗口是否置顶
  - --pos：目前仅提供固定位置，若 pos 不为空，则设置窗口位置
    - "left_top"表示左上角,
    - "right_top"表示右上角,
    - "left_bottom"表示左下角
    - "right_bottom"表示右下角
    - "top_center" 居中置顶
    - "" 默认居中
  - --transparent
  - --mini

## 右下角日志窗口

- cmd启动命令示例

```cmd
iflyrpa-window.exe --url="tauri://localhost/logwin.html?ws=..." --pos=right_bottom
```

- 前端可以利用cmd命令自测窗口包开发情况

![](./示例图片.png)

## 人机交互对话框窗口

- cmd启动命令示例

  - 对于基础对话框原子能力，由后端通过原子能力组织好若干参数转换成`JSON`字符串后放置在`option`参数，前端页面读取后解析

    - 消息通知对话框

    ```
    iflyrpa-window.exe --url=tauri://localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.message_box%22%2C%20%22box_title%22%3A%20%22%5Cu6d88%5Cu606f%5Cu63d0%5Cu793a%5Cu6846%22%2C%20%22message_type%22%3A%20%22message%22%2C%20%22message_content%22%3A%20%22%5Cu8fd9%5Cu662f%5Cu4e00%5Cu4e2a%5Cu6d4b%5Cu8bd5%5Cu6d88%5Cu606f%23%40%25%40%23%25%23%22%2C%20%22button_type%22%3A%20%22confirm_cancel%22%2C%20%22auto_check%22%3A%20true%2C%20%22wait_time%22%3A%203%2C%20%22outputkey%22%3A%20%22result_button%22%7D
    ```

    - 输入对话框

    ```
    iflyrpa-window.exe --url=tauri://localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.input_box%22%2C%20%22box_title%22%3A%20%22%5Cu8f93%5Cu5165%5Cu5bf9%5Cu8bdd%5Cu6846%22%2C%20%22input_type%22%3A%20%22text%22%2C%20%22input_title%22%3A%20%22%5Cu8f93%5Cu5165%5Cu6846%5Cu6807%5Cu9898%22%2C%20%22default_input%22%3A%20%22%22%2C%20%22outputkey%22%3A%20%22input_content%22%7D
    ```

    - 选择对话框

    ```cmd
    // 单选
    iflyrpa-window.exe --url=tauri://localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.select_box%22%2C%20%22box_title%22%3A%20%22%5Cu9009%5Cu62e9%5Cu5bf9%5Cu8bdd%5Cu6846%22%2C%20%22select_type%22%3A%20%22multi111%22%2C%20%22options%22%3A%20%5B%7B%22label%22%3A%20%22%5Cu9009%5Cu98791%22%2C%20%22value%22%3A%20%22%5Cu9009%5Cu98791%22%7D%2C%20%7B%22label%22%3A%20%22%5Cu9009%5Cu98792%22%2C%20%22value%22%3A%20%22%5Cu9009%5Cu98792%22%7D%5D%2C%20%22options_title%22%3A%20%22%22%2C%20%22outputkey%22%3A%20%22select_result%22%7D
    // 多选
    iflyrpa-window.exe --name=userform --url=https://tauri.localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.select_box%22%2C%20%22box_title%22%3A%20%22%5Cu9009%5Cu62e9%5Cu5bf9%5Cu8bdd%5Cu6846%22%2C%20%22select_type%22%3A%20%22multi%22%2C%20%22options%22%3A%20%5B%7B%22label%22%3A%20%22%5Cu9009%5Cu98791%22%2C%20%22value%22%3A%20%22%5Cu9009%5Cu98791%22%7D%2C%20%7B%22label%22%3A%20%22%5Cu9009%5Cu98792%22%2C%20%22value%22%3A%20%22%5Cu9009%5Cu98792%22%7D%5D%2C%20%22options_title%22%3A%20%22%22%2C%20%22outputkey%22%3A%20%22select_result%22%7D
    ```

    - 日期选择对话框

    ```cmd
    iflyrpa-window.exe --url=tauri://localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.select_time_box%22%2C%20%22box_title%22%3A%20%22%5Cu65e5%5Cu671f%5Cu65f6%5Cu95f4%5Cu9009%5Cu62e9%5Cu6846%22%2C%20%22time_type%22%3A%20%22time_range%22%2C%20%22time_format%22%3A%20%22YYYY/MM/DD%20HH%3Amm%22%2C%20%22default_time%22%3A%20%22%22%2C%20%22default_time_range%22%3A%20%5B%22%22%2C%20%22%22%5D%2C%20%22input_title%22%3A%20%22%5Cu8f93%5Cu5165%5Cu6846%5Cu6807%5Cu9898%22%2C%20%22outputkey%22%3A%20%22select_time%22%7D
    ```

    - 文件选择对话框

    ```cmd
    // 文件选择框
    iflyrpa-window.exe --url=tauri://localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.select_file_box%22%2C%20%22box_title%22%3A%20%22%5Cu6587%5Cu4ef6%5Cu9009%5Cu62e9%5Cu6846%22%2C%20%22open_type%22%3A%20%22file%22%2C%20%22file_type%22%3A%20%22%2A%22%2C%20%22multiple_choice%22%3A%20true%2C%20%22select_title%22%3A%20%22%22%2C%20%22default_path%22%3A%20%22%5Cu8bf7%5Cu9009%5Cu62e9%5Cu6587%5Cu4ef6%5Cu5939%22%2C%20%22outputkey%22%3A%20%22select_file%22%7D

    // 文件夹选择框
    iflyrpa-window.exe --url=tauri://localhost/userform.html?option=%7B%22key%22%3A%20%22Dialog.select_file_box%22%2C%20%22box_title%22%3A%20%22%5Cu6587%5Cu4ef6%5Cu9009%5Cu62e9%5Cu6846%22%2C%20%22open_type%22%3A%20%22folder%22%2C%20%22file_type%22%3A%20%22%2A%22%2C%20%22multiple_choice%22%3A%20true%2C%20%22select_title%22%3A%20%22%22%2C%20%22default_path%22%3A%20%22%5Cu8bf7%5Cu9009%5Cu62e9%5Cu6587%5Cu4ef6%5Cu5939%22%2C%20%22outputkey%22%3A%20%22select_file%22%7D
    ```

  - 自定义对话框，采用标注输入分批接收数据，以`option_start`单独一行表明后端接下来准备开始分批传送字符串数据，传送完毕以`option_end`表明结束传送，前端开始拼接处理渲染数据。

  ```cmd
  // 稍短的实例
  iflyrpa-window.exe --url=tauri://localhost/userform.html
  option_start
  {"key": "Dialog.custom_box", "box_title": "\u81ea\u5b9a\u4e49\u5bf9\u8bdd\u6846", "design_interface": "{\"mode\": \"window\", \"title\": \"\u81ea\u5b9a\u4e49\u5bf9\u8bdd\u6846\", \"buttonType\": \"confirm_cancel\", \"formList\": [{\"id\": \"bh668269519638597\", \"dialogFormType\": \"RADIO_GROUP\", \"dialogFormName\": \"\u5355\u9009\u6846\", \"configKeys\": [\"label\", \"options\", \"defaultValue\", \"direction\", \"bind\"], \"label\": \"\u5355\u9009\u6846\", \"options\": {\"formType\": {\"type\": \"OPTIONSLIST\"}, \"key\": \"options\", \"title\": \"\u9009\u9879\", \"default\": [], \"required\": true, \"value\": [{\"rId\": \"3z0DFJRhL1MNRCZSS6B_q\", \"value\": \"\u9009\u98791\"}]}, \"defaultValue\": {\"formType\": {\"type\": \"SELECT\"}, \"key\": \"default_option_single_select\", \"title\": \"\u9ed8\u8ba4\u503c\", \"options\": [{\"label\": \"\u9009\u98791\", \"value\": \"3z0DFJRhL1MNRCZSS6B_q\"}], \"default\": \"\", \"value\": \"\"}, \"direction\": {\"formType\": {\"type\": \"RADIO\"}, \"key\": \"direction\", \"title\": \"\u6392\u5217\u65b9\u5411\", \"options\": [{\"label\": \"\u6a2a\u5411\u6392\u5217\", \"value\": \"horizontal\"}, {\"label\": \"\u7eb5\u5411\u6392\u5217\", \"value\": \"vertical\"}], \"default\": \"horizontal\", \"value\": \"horizontal\"}, \"bind\": \"radio_box_1\"}]}", "result_button": "confirm", "outputkey": "dialog_result"}
  option_end
  ```

  ![](./自定义对话框示例图片.png)

  ```cmd
  // 比较全的示例
  iflyrpa-window.exe --url=tauri://localhost/userform.html
  option_start
  {"key": "Dialog.custom_box", "box_title": "\u81ea\u5b9a\u4e49\u5bf9\u8bdd\u6846", "design_interface": "{\"mode\": \"window\", \"title\": \"\u81ea\u5b9a\u4e49\u5bf9\u8bdd\u6846\", \"buttonType\": \"confirm_cancel\", \"formList\": [{\"id\": \"bh671862937137221\", \"dialogFormType\": \"PASSWORD\", \"dialogFormName\": \"\u5bc6\u7801\u6846\", \"configKeys\": [\"label\", \"placeholder\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u5bc6\u7801\u6846\", \"placeholder\": \"\u8bf7\u8f93\u5165\u6587\u672c\u5bc6\u7801\", \"defaultValue\": \"\", \"bind\": \"password_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}}, {\"id\": \"bh671862946177093\", \"dialogFormType\": \"INPUT\", \"dialogFormName\": \"\u8f93\u5165\u6846\", \"configKeys\": [\"label\", \"placeholder\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u8f93\u5165\u6846\", \"plac

  eholder\": \"\u8bf7\u8f93\u5165\u6587\u672c\u5185\u5bb9\", \"defaultValue\": \"\", \"bind\": \"input_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}}, {\"id\": \"bh671862951936069\", \"dialogFormType\": \"DATEPICKER\", \"dialogFormName\": \"\u65e5\u671f\u65f6\u95f4\", \"configKeys\": [\"label\", \"format\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u65e5\u671f\u65f6\u95f4\", \"format\": {\"formType\": {\"type\": \"SELECT\"}, \"key\": \"time_format_select\", \"title\": \"\u65f6\u95f4\u683c\u5f0f\", \"options\": [{\"label\": \"\u5e74-\u6708-\u65e5\", \"value\": \"YYYY-MM-DD\"}, {\"label\": \"\u5e74-\u6708-\u65e5 \u65f6:\u5206\", \"value\": \"YYYY-MM-DD HH:mm\"}, {\"label\": \"\u5e74-\u6708-\u65e5 \u65f6:\u5206:\u79d2\", \"value\": \"YYYY-MM-DD HH:mm:ss\"}, {\"label\": \"\u5e74/\u6708/\u65e5\", \"value\": \"YYYY/MM/DD\"}, {\"label\": \"\u5e74/\u6708/\u65e5 \u65f6:\u5206\", \"value\": \"YYYY/MM/DD HH:mm\"}, {\"label\": \"\u5e74/\u6708/\u65e5 \u65f6:\u5206:\u79d2\", \"value\": \"YYYY/MM/DD HH:mm:ss\"}], \"default\": \"YYYY-MM-DD\", \"required\": false, \"value\": \"YYYY-MM-DD\"}, \"defaultValue\": {\"formType\": {\"type\": \"DEFAULTDATEPICKER\", \"params\": {\"format\": \"YYYY-MM-DD\"}}, \"key\": \"default_time\", \"title\": \"\u9ed8\u8ba4\u65f6\u95f4\", \"default\": \"\", \"value\": \"\"}, \"b

  ind\": \"datepicker_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"DATEPICKER_LINK\"}, {\"id\": \"bh671862964035653\", \"dialogFormType\": \"INPUT\", \"dialogFormName\": \"\u8f93\u5165\u6846\", \"configKeys\": [\"label\", \"placeholder\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u8f93\u5165\u6846\", \"placeholder\": \"\u8bf7\u8f93\u5165\u6587\u672c\u5185\u5bb9\", \"defaultValue\": \"\", \"bind\": \"input_box_2\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}}, {\"id\": \"bh671862968197189\", \"dialogFormType\": \"CHECKBOX_GROUP\", \"dialogFormName\": \"\u590d\u9009\u6846\", \"configKeys\": [\"label\", \"options\", \"defaultValue\", \"direction\", \"bind\", \"required\"], \"label\": \"\u590d\u9009\u6846\", \"options\": {\"formType\": {\"type\": \"OPTIONSLIST\"}, \"key\": \"options\", \"title\": \"\u9009\u9879\", \"default\": [], \"required\": true, \"value\": [{\"rId\": \"Ku7Hp_bvAG7L7XAgcUP-B\", \"value\": \"\u9009\u98791\"}]}, \"defaultValue\": {\"formType\": {\"type\": \"SELECT\", \"params\": {\"multiple\": true}}, \"key\": \"default_option_multi_select\", \"title\": \"\u9ed8\u8ba4\u503c\", \"options\": [{\"label\": \"\u9009\u98791\", \"value\": \"Ku7Hp_bvAG7L7XAgcUP-B\"}], \"allowReverse\": true, \"default\": [], \"value\": []}, \"direction\": {\"formType\": {\"type\": \"RADIO\"}, \"key\": \"direction\", \"title\": \"\u6392\u5217\u65b9\u5411\", \"options\": [{\"label\": \"\u6a2a\u5411\u6392\u5217\", \"value\": \"horizontal\"}, {\"label\": \"\u7eb5\u5411\u6392\u5217\", \"val

  ue\": \"vertical\"}], \"default\": \"horizontal\", \"value\": \"horizontal\"}, \"bind\": \"check_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"OPTIONS_MULTI_LINK\"}, {\"id\": \"bh671862972653637\", \"dialogFormType\": \"SINGLE_SELECT\", \"dialogFormName\": \"\u5355\u9009\u4e0b\u62c9\u6846\", \"configKeys\": [\"label\", \"options\", \"placeholder\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u5355\u9009\u4e0b\u62c9\u6846\", \"options\": {\"formType\": {\"type\": \"OPTIONSLIST\"}, \"key\": \"options\", \"title\": \"\u9009\u9879\", \"default\": [], \"required\": true, \"value\": [{\"rId\": \"ZMT7R5z9Zsu1O6ZnbwQ42\", \"value\": \"\u9009\u98791\"}]}, \"placeholder\": \"\u8bf7\u9009\u62e9\u4e00\u9879\", \"defaultValue\": {\"formType\": {\"type\": \"SELECT\"}, \"key\": \"default_option_single_select\", \"title\": \"\u9ed8\u8ba4\u503c\", \"options\": [{\"label\": \"\u9009\u98791\", \"value\": \"ZMT7R5z9Zsu1O6ZnbwQ42\"}], \"allowReverse\": true, \"default\": \"\", \"value\": \"\"}, \"bind\": \"single_select_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"OPTIONS_SINGLE_LINK\"}, {\"id\": \"bh671862975144005\", \"dialogFormType\": \"MULTI_SELECT\", \"dialogFormName\": \"\u591a\u9009\u4e0b\u62c9\u6846\", \"configKeys\": [\"label\", \"options\", \"placeholder\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u591a\u9009\u4e0b\u62c9\u6846\", \"options\": {\"formType\": {\"type\": \"OPTIONSLIST\"}, \"key\": \"options\", \"title\": \"\u9009\u9879\", \"de

  fault\": [], \"required\": true, \"value\": [{\"rId\": \"VDUeCl--r_mXnocoA_6sF\", \"value\": \"\u9009\u98791\"}]}, \"placeholder\": \"\u8bf7\u9009\u62e9\u4e00\u9879\u6216\u591a\u9879\", \"defaultValue\": {\"formType\": {\"type\": \"SELECT\", \"params\": {\"multiple\": true}}, \"key\": \"default_option_multi_select\", \"title\": \"\u9ed8\u8ba4\u503c\", \"options\": [{\"label\": \"\u9009\u98791\", \"value\": \"VDUeCl--r_mXnocoA_6sF\"}], \"allowReverse\": true, \"default\": [], \"value\": []}, \"bind\": \"multi_select_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"OPTIONS_MULTI_LINK\"}, {\"id\": \"bh671862978039877\", \"dialogFormType\": \"TEXT_DESC\", \"dialogFormName\": \"\u6587\u672c\", \"configKeys\": [\"fontFamily\", \"fontSize\", \"fontStyle\", \"textContent\"], \"fontFamily\": {\"formType\": {\"type\": \"SELECT\"}, \"key\": \"fontFamily\", \"title\": \"\u5b57\u4f53\", \"options\": [{\"label\": \"\u5fae\u8f6f\u96c5\u9ed1\", \"value\": \"msyh\"}, {\"label\": \"\u5b8b\u4f53\", \"value\": \"simsun\"}, {\"label\": \"\u9ed1\u4f53\", \"value\": \"simhei\"}, {\"label\": \"\u4eff\u5b8b\", \"value\": \"simfang\"}, {\"label\": \"Times New Roman\", \"value\": \"times\"}, {\"label\": \"\u6977\u4f53\", \"value\": \"KaiTi\"}, {\"label\": \"\u96b6\u4e66\", \"value\": \"LiShu\"}, {\"label\": \"\u65b0\u5b8b\u4f53\", \"value\": \"NSimSun\"}, {\"label\": \"\u5e7c\u5706\", \"value\": \"YouYuan\"}, {\"label\": \"Arial\", \"value\": \"Arial\"}, {\"label\": \"Microsoft JhengHei\", \"value\": \"MicrosoftJhengHei\"}, {\"label\": \"Calibri\", \"value\": \"Calibri\"}], \"default\": \"msyh\", \"required\": false, \"value\": \"msyh\"}, \"fontSize\": {\"formType\": {\"type\": \"FONTSIZENUMBER\"}, \"key\": \"fontSize\", \"title\": \"\u5b57\u53f7\", \"min\": 12, \"max\": 72, \"step\": 2, \"default\": 12, \"required\": true, \"value\": 12}, \"fontStyle\": {\"formType\": {\"ty

  pe\": \"CHECKBOXGROUP\"}, \"key\": \"fontStyle\", \"title\": \"\u5b57\u4f53\u5c5e\u6027\", \"options\": [{\"label\": \"\u52a0\u7c97\", \"value\": \"bold\"}, {\"label\": \"\u659c\u4f53\", \"value\": \"italic\"}, {\"label\": \"\u4e0b\u5212\u7ebf\", \"value\": \"underline\"}], \"default\": [], \"value\": []}, \"textContent\": \"\u6587\u672c\u63cf\u8ff0\"}, {\"id\": \"bh671863017250885\", \"dialogFormType\": \"PATH_INPUT\", \"dialogFormName\": \"\u6587\u4ef6\u9009\u62e9\", \"configKeys\": [\"label\", \"selectType\", \"filter\", \"placeholder\", \"defaultPath\", \"bind\", \"required\"], \"label\": \"\u6587\u4ef6\u9009\u62e9\", \"selectType\": {\"formType\": {\"type\": \"RADIO\"}, \"key\": \"file_type\", \"title\": \"\u9009\u62e9\u7c7b\u578b\", \"options\": [{\"label\": \"\u6587\u4ef6\", \"value\": \"file\"}, {\"label\": \"\u6587\u4ef6\u5939\", \"value\": \"folder\"}], \"default\": \"file\", \"value\": \"file\"}, \"filter\": {\"formType\": {\"type\": \"SELECT\"}, \"key\": \"file_filter_select\", \"title\": \"\u6587\u4ef6\u7c7b\u578b\", \"options\": [{\"label\": \"\u6240\u6709\u6587\u4ef6\", \"value\": \"*\"}, {\"label\": \"Excel\u6587\u4ef6\", \"value\": \".xls,.xlsx\"}, {\"label\": \"Word\u6587\u4ef6\", \"value\": \".doc,.docx\"}, {\"label\": \"\u6587\u672c\u6587\u4ef6\", \"value\": \".txt\"}, {\"label\": \"\u56fe\u50cf\u6587\u4ef6\", \"value\": \".png,.jpg,.bmp\"}, {\"label\": \"PPT\u6587\u4ef6\", \"value\": \".ppt,.pptx\"}, {\"label\": \"\u538b\u7f29\u6587\u4ef6\", \"value\": \".zip,.rar\"}], \"default\": \"*\", \"value\": \"*\"}, \"placeholder\": \"\u8bf7\u9009\u62e9\u6587\u4ef6\", \"defaultPath\": \"\", \"bind\": \"path_input_box_1\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"PATH_INPUT_LINK\"}, {\"id\": \"bh671863020036165\", \"dialogFormType\": \"CHECKBOX_GROUP\", \"dialogFormName\": \"\u590d\u9009\u6846\", \"configKeys\": [\"label\", \"options\", \"defaultValue\", \"direction\", \"bind\", \"required\"], \"label\": \"\u590d\u9009\u6846\", \"options\": {\"formType\": {\"type\": \"OPTIONSLIST\"}, \"key\": \"options\", \"title\": \"\u9009\u9879\", \"default\": [], \"required\": true, \"value\": [{\"rId\": \"Kp0IMj_Ru8n36oX84JCwl\", \"value\": \"\u9009\u98791\"}]}, \"defaultValue\": {\"formType\": {\"type\": \"SELECT\", \"params\": {\"multiple\": true}}, \"key\": \"default_option_multi_select\", \"title\": \"\u9ed8\u8ba4\u503c\", \"options\": [{\"label\": \"\u9009\u98791\", \"value\": \"Kp0IMj_Ru8n36oX84JCwl\"}], \"allowReverse\": true, \"default\": [], \"value\": []}, \"direction\": {\"formType\": {\"type\": \"RADIO\"}, \"key\": \"direction\", \"title\": \"\u6392\u5217\u65b9\u5411\", \"options\": [{\"label\": \"\u6a2a\u5411\u6392\u5217\", \"value\": \"horizontal\"}, {\"label\": \"\u7eb5\u5411\u6392\u5217\", \"value\": \"vertical\"}], \"default\": \"horizontal\", \"value\": \"horizontal\"}, \"b

  ind\": \"check_box_2\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"OPTIONS_MULTI_LINK\"}, {\"id\": \"bh671863022526533\", \"dialogFormType\": \"MULTI_SELECT\", \"dialogFormName\": \"\u591a\u9009\u4e0b\u62c9\u6846\", \"configKeys\": [\"label\", \"options\", \"placeholder\", \"defaultValue\", \"bind\", \"required\"], \"label\": \"\u591a\u9009\u4e0b\u62c9\u6846\", \"options\": {\"formType\": {\"type\": \"OPTIONSLIST\"}, \"key\": \"options\", \"title\": \"\u9009\u9879\", \"default\": [], \"required\": true, \"value\": [{\"rId\": \"iAX_JbNafuvka3DWFNOS9\", \"value\": \"\u9009\u98791\"}]}, \"placeholder\": \"\u8bf7\u9009\u62e9\u4e00\u9879\u6216\u591a\u9879\", \"defaultValue\": {\"formType\": {\"type\": \"SELECT\", \"params\": {\"multiple\": true}}, \"key\": \"default_option_multi_select\", \"title\": \"\u9ed8\u8ba4\u503c\", \"options\": [{\"label\": \"\u9009\u98791\", \"value\": \"iAX_JbNafuvka3DWFNOS9\"}], \"allowReverse\": true, \"default\": [], \"value\": []}, \"bind\": \"multi_select_box_2\", \"required\": {\"formType\": {\"type\": \"CHECKBOX\"}, \"title\": \"\u8bbe\u7f6e\u8be5\u8868\u5355\u63a7\u4ef6\u4e3a\u5fc5\u586b\", \"options\": [{\"label\": \"\u662f\", \"value\": true}, {\"label\": \"\u5426\", \"value\": false}], \"default\": false, \"required\": false, \"value\": false}, \"conditionalFnKey\": \"OPTIONS_MULTI_LINK\"}], \"table_required\": false}", "result_button": "confirm", "outputkey": "dialog_result"}
  option_end
  ```

## AI组件交互窗口(不提测，只在dev环境)

- cmd启动命令示例

```cmd
# 多轮问答窗口
iflyrpa-window.exe --url="tauri://localhost/multichat.html?max_turns=10&is_save=1&title=1111111"

# 知识问答
iflyrpa-window.exe --url="tauri://localhost/multichat.html?max_turns=10&is_save=1&questions=你好$-$再见$-$拜拜&file_path=C:\Users\wrjin\Desktop\前端规范文档.pdf" --content=asdasdasdas

```

# 多窗口包打包说明

## 新增监听标准输入前

- D:\work\client-ui\packages\tauri-app-window直接打开该目录下的终端，输入打包命令

  ```bash
  ## package.json
  # 打release包，生产环境需要
  npm run build
  # 打debug包，日常联调自测可用
  npm run build:debug
  ```

## 新增监听标准输入后第一次打包

- 因为`Rust`默认的`release`包是`GUI`形式的，无法支持我们多窗口业务中的标准输入功能，针对这个问题，我们单独对tauri-app-window目录(多窗口的方案实现目录)使用非稳定版本的Rust特性， 在该目录下的`Cargo.toml`文件中新增了三行，详见Cargo.toml文件：

  - cargo-features = ["profile-rustflags"]
  - [profile.release]
    rustflags = ["-C", "link-args=/SUBSYSTEM:console"]

- 新增完成之后，尝试使用`npm run build`打包会提示你要切换`Rust`版本
  - 随便起一个cmd窗口，使用命令`rustup override set nightly `切换到不稳定版本，切换是全局的
  - 如果是初次切换会先下载(需要科学上网)，等待下载完成
  - 再次输入`rustup override set nightly `切换成功之后，按照之前的打包命令直接打包即可
    - 如果再遇到类似`supurios network`的网络警告提示，可切换中科大源：[rust更新crate.io慢并更换国内镜像源](https://blog.csdn.net/Martin12111/article/details/130591111)
  - 可以选择使用`rustup override set stable`切换回原先的稳定版本
