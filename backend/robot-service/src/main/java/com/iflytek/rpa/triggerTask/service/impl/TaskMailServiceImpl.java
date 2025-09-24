package com.iflytek.rpa.triggerTask.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.task.entity.enums.SourceTypeEnum;
import com.iflytek.rpa.triggerTask.dao.TaskMailMapper;
import com.iflytek.rpa.triggerTask.entity.TaskMail;
import com.iflytek.rpa.triggerTask.service.ITaskMailService;
import com.iflytek.rpa.triggerTask.service.TriggerTaskService;
import com.iflytek.rpa.utils.HttpUtils;
import com.iflytek.rpa.utils.MonitorUtils;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.List;
import org.casbin.casdoor.entity.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * <p>
 * 计划任务执行结果 服务实现类
 * </p>
 *
 * @author keler
 * @since 2021-10-08
 */
@Service
public class TaskMailServiceImpl extends ServiceImpl<TaskMailMapper, TaskMail> implements ITaskMailService {

    @Autowired
    private TriggerTaskService triggerTaskService;

    @Override
    public IPage<TaskMail> getTaskMailPage(Long pageNo, Long pageSize, String userId) throws NoLoginException {

        IPage<TaskMail> page = new Page<>(pageNo, pageSize);
        LambdaQueryWrapper<TaskMail> wrapper = new LambdaQueryWrapper<>();
        User userDetail = UserUtils.nowLoginUser();
        String sourceType = HttpUtils.getSourceType();
        if (SourceTypeEnum.WEB.getCode().equals(sourceType) && userId != null) {
            userDetail.id = userId;
        }
        wrapper.eq(TaskMail::getUserId, userDetail.id);
        wrapper.eq(TaskMail::getTenantId, TenantUtils.getTenantId());
        wrapper.orderByDesc(TaskMail::getId);
        page = this.page(page, wrapper);
        //        if(CollectionUtils.isEmpty(page.getRecords())){
        //            return page;
        //        }
        //        for(TaskMail mail:page.getRecords()){
        //            mail.setEnableSSL(mail.getSslFlag());
        //        }
        return page;
    }

    @Override
    public void saveMail(TaskMail mail) throws NoLoginException {
        TaskMail existMail = baseMapper.selectOne(new LambdaQueryWrapper<TaskMail>()
                .eq(TaskMail::getResourceId, mail.getResourceId())
                .orderByDesc(TaskMail::getId)
                .last("limit 1"));
        if (existMail != null) {
            mail.setId(existMail.getId());
        }
        preDealMailInfo(mail);
        checkMailInfo(mail);
        saveOrUpdate(mail);
    }

    private void checkMailInfo(TaskMail mail) {
        LambdaQueryWrapper<TaskMail> wrapper = new LambdaQueryWrapper<TaskMail>()
                .eq(TaskMail::getEmailAccount, mail.getEmailAccount())
                .eq(TaskMail::getUserId, mail.getUserId())
                .eq(TaskMail::getTenantId, mail.getTenantId());
        if (mail.getId() != null) {
            // 编辑,查重排除自己
            wrapper.ne(TaskMail::getId, mail.getId());
        }
        Integer count = baseMapper.selectCount(wrapper);
        if (count != null && count > 0) {
            throw new ServiceException("邮箱账号已存在");
        }
    }

    private void preDealMailInfo(TaskMail mail) throws NoLoginException {
        if ("qqEmail".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("imap.qq.com");
            mail.setPort("993");
        } else if ("163Email".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("imap.163.com");
            mail.setPort("993");
        } else if ("126Email".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("imap.126.com");
            mail.setPort("993");
        }
        if (mail.getUserId() == null) {
            mail.setUserId(UserUtils.nowLoginUser().id);
        }
        mail.setTenantId(TenantUtils.getTenantId());
        mail.setPort(mail.getPort().replaceAll(" ", ""));
        mail.setEmailServiceAddress(mail.getEmailServiceAddress().replaceAll(" ", ""));
        mail.setEmailService(mail.getEmailService().replaceAll(" ", ""));
        mail.setEmailAccount(mail.getEmailAccount().replaceAll(" ", ""));
        mail.setEmailProtocol(mail.getEmailProtocol().replaceAll(" ", ""));
        mail.setAuthorizationCode(mail.getAuthorizationCode().replaceAll(" ", ""));
    }

    @Override
    public String connectMail(TaskMail mail) {
        if ("qqEmail".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("imap.qq.com");
            mail.setPort("993");
        } else if ("163Email".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("imap.163.com");
            mail.setPort("993");
        } else if ("126Email".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("imap.126.com");
            mail.setPort("993");
        } else if ("iflytekEmail".equals(mail.getEmailService())) {
            mail.setEmailServiceAddress("mail.iflytek.com");
            mail.setPort("993");
        }
        mail.setPort(mail.getPort().replaceAll(" ", ""));
        mail.setEmailServiceAddress(mail.getEmailServiceAddress().replaceAll(" ", ""));
        mail.setEmailService(mail.getEmailService().replaceAll(" ", ""));
        mail.setEmailAccount(mail.getEmailAccount().replaceAll(" ", ""));
        mail.setEmailProtocol(mail.getEmailProtocol().replaceAll(" ", ""));
        mail.setAuthorizationCode(mail.getAuthorizationCode().replaceAll(" ", ""));
        return MonitorUtils.connectMail(
                mail.getEmailProtocol().toLowerCase().trim(),
                Integer.valueOf(mail.getPort()),
                mail.getEmailServiceAddress().trim(),
                mail.getEnableSSL(),
                mail.getEmailAccount().trim(),
                mail.getAuthorizationCode().trim());
    }

    @Override
    public boolean deleteMail(String resourceId) {
        List<String> usingTasksNames = triggerTaskService.getUsingTasksByMail(resourceId); // todo 此处迁移不一定能奏效，数据结构设计不同
        if (!CollectionUtils.isEmpty(usingTasksNames)) {
            return false;
        }
        baseMapper.delete(new LambdaQueryWrapper<TaskMail>().eq(TaskMail::getResourceId, resourceId));
        return true;
    }

    @Override
    public List<TaskMail> getTaskMailsByResourceIds(List<String> mailIds) {
        return baseMapper.selectList(new LambdaQueryWrapper<TaskMail>().in(TaskMail::getResourceId, mailIds));
    }
}
