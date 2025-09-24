package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

/**
 * 共享变量子变量VO
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class SharedSubVarVo {

    /**
     * 子变量id
     */
    private Long id;

    /**
     * 共享变量id
     */
    private Long sharedVarId;

    /**
     * 子变量名
     */
    private String varName;

    /**
     * 类型：文本/密码/数组
     */
    private String varType;

    /**
     * 变量具体值
     */
    private String varValue;

    /**
     * 是否加密:1-加密
     */
    private Integer encrypt;
}
