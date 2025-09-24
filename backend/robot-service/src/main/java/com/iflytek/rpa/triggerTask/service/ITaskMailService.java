package com.iflytek.rpa.triggerTask.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.triggerTask.entity.TaskMail;
import java.util.List;

/**
 * <p>
 * 任务执行队列 服务类
 * </p>
 *
 * @author jiechen39
 * @since 2022-12-16
 */
public interface ITaskMailService extends IService<TaskMail> {

    IPage<TaskMail> getTaskMailPage(Long pageNum, Long pageSize, String userId) throws NoLoginException;

    void saveMail(TaskMail mail) throws NoLoginException;

    String connectMail(TaskMail mail);

    boolean deleteMail(String resourceId);

    List<TaskMail> getTaskMailsByResourceIds(List<String> mailIds);
}
