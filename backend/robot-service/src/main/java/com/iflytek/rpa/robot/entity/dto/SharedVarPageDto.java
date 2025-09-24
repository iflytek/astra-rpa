package com.iflytek.rpa.robot.entity.dto;

import lombok.Data;

/**
 * 共享变量分页查询DTO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarPageDto {
    /**
     * 变量名
     */
    private String sharedVarName;
    /**
     * 启用状态：1启用，0禁用
     */
    private Integer status;
    /**
     * 所属部门
     */
    private String deptId;
    /**
     * 页数
     */
    private Long pageNo;
    /**
     * 页面大小
     */
    private Long pageSize;
}
