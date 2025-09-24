package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 云端机器人版本表(RobotVersion)实体类
 *
 * @author makejava
 * @since 2024-09-29 15:34:14
 */
@Data
public class RobotVersion implements Serializable {
    private static final long serialVersionUID = 221473423657236377L;
    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    /**
     * 机器人id
     */
    @NotBlank(message = "机器人id不能为空")
    private String robotId;

    // 表名该字段不在数据库中
    @TableField(exist = false)
    private String name;

    @NotBlank(message = "机器人图标不能为空")
    private String icon;

    /**
     * 版本号
     */
    private Integer version;
    /**
     * 简介
     */
    private String introduction;
    /**
     * 更新日志
     */
    private String updateLog;
    /**
     * 使用说明
     */
    private String useDescription;
    /**
     * 是否启用 0:未启用,1:已启用
     */
    private Integer online;
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

    private String tenantId;

    private String param;

    /**
     * 视频地址id
     */
    private String videoId;
    /**
     * 附件地址id
     */
    private String appendixId;

    @TableField(exist = false)
    private Integer editFlag;

    @TableField(exist = false)
    private String category;
}
