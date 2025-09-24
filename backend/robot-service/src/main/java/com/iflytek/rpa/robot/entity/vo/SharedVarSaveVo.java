package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * 共享变量保存结果VO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarSaveVo {

    /**
     * 变量名
     */
    private String sharedVarName;

    /**
     * 变量类型
     */
    private String varType;

    /**
     * 变量值
     */
    private String varValue;

    /**
     * 变量说明
     */
    private String remark;

    /**
     * 所属部门
     */
    private String deptName;

    /**
     * 可使用账号
     */
    private String usageType;

    /**
     * 状态
     */
    private Integer status;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;
}
