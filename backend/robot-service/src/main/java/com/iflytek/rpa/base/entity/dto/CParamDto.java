package com.iflytek.rpa.base.entity.dto;

import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CParamDto {

    private String id;

    /**
     * 输入输出
     */
    @NotNull(message = "varDirection不能为null")
    private int varDirection;

    /**
     * 参数名称
     */
    @NotNull(message = "varName不能为null")
    private String varName;

    /**
     * 参数类型
     */
    @NotNull(message = "varType不能为null")
    private String varType;

    /**
     * 默认值
     */
    private String varValue;

    /**
     * 参数描述
     */
    private String varDescribe;

    /**
     * 机器人id
     */
    @NotNull(message = "robotId不能为null")
    private String robotId;

    /**
     * 机器人版本
     */
    // 机器人版本可以为null，因为新增指挥发生在编辑状态
    private Integer robotVersion;

    /**
     * 流程id
     */
    @NotNull(message = "processId不能为null")
    private String processId;
}
