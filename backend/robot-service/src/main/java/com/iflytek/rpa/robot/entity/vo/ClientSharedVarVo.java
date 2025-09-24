package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

/**
 * 客户端共享变量VO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class ClientSharedVarVo {

    /**
     * 共享变量ID
     */
    private Long id;

    /**
     * 共享变量名
     */
    private String sharedVarName;

    /**
     * 共享变量类型
     */
    private String sharedVarType;

    /**
     * 共享变量是否加密
     */
    private Integer encrypt;

    /**
     * 共享变量值（加密后数据）
     */
    private String sharedVarValue;

    /**
     * 子变量列表
     */
    private List<ClientSharedSubVarVo> subVarList;
}
