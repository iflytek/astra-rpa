package com.iflytek.rpa.component.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 机器人对组件屏蔽视图对象
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ComponentRobotBlockVo {

    /**
     * 主键id
     */
    private Long id;

    /**
     * 机器人id
     */
    private String robotId;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;

    /**
     * 组件id
     */
    private String componentId;

    /**
     * 组件名称（关联查询）
     */
    private String componentName;

    /**
     * 机器人名称（关联查询）
     */
    private String robotName;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 创建者名称（关联查询）
     */
    private String creatorName;

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
     * 更新者名称（关联查询）
     */
    private String updaterName;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;

    /**
     * 租户id
     */
    private String tenantId;
}
