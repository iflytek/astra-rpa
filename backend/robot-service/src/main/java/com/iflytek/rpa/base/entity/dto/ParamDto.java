package com.iflytek.rpa.base.entity.dto;

import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-04-03 11:01
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class ParamDto {

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
     * 流程id
     */
    @NotNull(message = "processId不能为null")
    private String processId;
}
