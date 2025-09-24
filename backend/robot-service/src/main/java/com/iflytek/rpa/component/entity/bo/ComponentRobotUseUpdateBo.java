package com.iflytek.rpa.component.entity.bo;

import lombok.Data;

/**
 * 组件机器人使用更新BO
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class ComponentRobotUseUpdateBo {

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
     * 旧组件版本号
     */
    private Integer oldComponentVersion;

    /**
     * 新组件版本号
     */
    private Integer newComponentVersion;

    /**
     * 租户ID
     */
    private String tenantId;

    /**
     * 更新人ID
     */
    private String updaterId;
}
