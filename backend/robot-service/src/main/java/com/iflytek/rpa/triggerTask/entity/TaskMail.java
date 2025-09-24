package com.iflytek.rpa.triggerTask.entity;

import com.baomidou.mybatisplus.annotation.*;
import java.io.Serializable;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * <p>
 * 调度任务
 * </p>
 *
 * @author keler
 * @since 2021-10-08
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("task_mail")
public class TaskMail implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String userId; // 用户id

    private String tenantId; // 租户id

    private String resourceId; // 邮箱id

    private String emailService; // 邮箱服务器，163Email、126Email、qqEmail、customEmail

    private String emailProtocol; // 使用协议，POP3,IMAP

    private String emailServiceAddress; // 邮箱服务器地址

    private String port; // 邮箱服务器端口

    @TableField(value = "enable_ssl")
    private Boolean enableSSL; // 是否使用SSL

    private String emailAccount; // 邮箱账号

    private String authorizationCode; // 邮箱授权码

    @TableLogic(value = "0", delval = "1")
    private Integer deleted; // 是否删除 0：未删除，1：已删除
}
