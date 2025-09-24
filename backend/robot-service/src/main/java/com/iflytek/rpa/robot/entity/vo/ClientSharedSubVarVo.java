package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

/**
 * 客户端共享子变量VO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class ClientSharedSubVarVo {

    /**
     * 子变量名
     */
    private String varName;

    /**
     * 子变量类型
     */
    private String varType;

    /**
     * 子变量是否加密
     */
    private Integer encrypt;

    /**
     * 子变量值（加密后的数据）
     */
    private String varValue;
}
