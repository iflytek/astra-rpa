package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 共享变量信息(SharedVar)实体类
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVar implements Serializable {
    private static final long serialVersionUID = 221473413657231317L;

    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 共享变量名
     */
    private String sharedVarName;
    /**
     * 共享变量类型：text/password/array/group
     */
    private String sharedVarType;
    /**
     * 启用状态：1启用，0禁用
     */
    private Integer status;

    /**
     * 变量说明
     */
    private String remark;

    /**
     * 所属部门ID
     */
    private String deptId;

    /**
     * 可使用账号类别(all/dept/select)：所有人：all、所属部门所有人：dept、指定人：select
     */
    private String usageType;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新者id
     */
    private String updaterId;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}
