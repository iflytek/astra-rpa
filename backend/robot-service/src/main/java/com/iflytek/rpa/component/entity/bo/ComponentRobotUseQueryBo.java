package com.iflytek.rpa.component.entity.bo;

import lombok.Data;

/**
 * 组件机器人使用查询BO
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class ComponentRobotUseQueryBo {

    /**
     * 机器人ID
     */
    private String robotId;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;

    /**
     * 组件ID
     */
    private String componentId;

    /**
     * 组件版本号
     */
    private Integer componentVersion;

    /**
     * 租户ID
     */
    private String tenantId;
}
