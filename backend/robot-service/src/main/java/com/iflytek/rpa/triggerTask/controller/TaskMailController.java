package com.iflytek.rpa.triggerTask.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.triggerTask.entity.TaskMail;
import com.iflytek.rpa.triggerTask.entity.dto.EnableBo;
import com.iflytek.rpa.triggerTask.service.ITaskMailService;
import java.util.HashMap;
import java.util.Map;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/taskMail")
public class TaskMailController {

    @Autowired
    private ITaskMailService taskMailService;

    /**
     * 邮箱列表分页
     *
     * @param pageNo
     * @param pageSize
     * @param userId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/page/list")
    public AppResponse<IPage<TaskMail>> getTaskExecute(
            @RequestParam(value = "pageNo", defaultValue = "1") Long pageNo,
            @RequestParam(value = "pageSize", defaultValue = "20") Long pageSize,
            @RequestParam(value = "userId", required = false) String userId)
            throws NoLoginException {
        return AppResponse.success(taskMailService.getTaskMailPage(pageNo, pageSize, userId));
    }

    /**
     * 邮箱链接测试 todo 时间紧迫，这是搬运老客户端，后续还需要规整
     *
     * @param mail
     * @return
     */
    @PostMapping("/connect")
    public Map<String, String> connectMail(@RequestBody TaskMail mail) {
        String msg = taskMailService.connectMail(mail);
        return new HashMap<String, String>() {
            {
                put("code", "000000");
                put("data", StringUtils.isEmpty(msg) ? "1" : "0");
                put("message", msg);
            }
        };
    }

    /**
     * 保存邮箱接口
     *
     * @param mail
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/save")
    public AppResponse<ErrorCodeEnum> saveMail(@RequestBody TaskMail mail) throws NoLoginException {
        taskMailService.saveMail(mail);
        return AppResponse.success(ErrorCodeEnum.S_SUCCESS);
    }

    /**
     * 删除邮箱接口
     *
     * @param enableBo
     * @return
     */
    @PostMapping("/delete")
    public AppResponse<ErrorCodeEnum> deleteMail(@RequestBody EnableBo enableBo) {
        if (taskMailService.deleteMail(enableBo.getResourceId())) {
            return AppResponse.success(ErrorCodeEnum.S_SUCCESS);
        }
        throw new ServiceException("邮箱被计划任务占用");
    }
}
