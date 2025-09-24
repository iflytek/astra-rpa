package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

/**
 * 共享变量分页查询返回VO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarPageVo {

    /**
     * 主键id
     */
    private Long id;

    /**
     * 变量名
     */
    private String sharedVarName;

    /**
     * 变量类型：text/password/array/group
     */
    private String sharedVarType;
    /**
     * 变量具体值
     */
    private String sharedVarValue;
    /**
     * 是否加密:1-加密
     */
    private Integer sharedVarEncrypt;
    /**
     * 变量值列表
     */
    private List<SharedSubVarVo> varList;
    /**
     * 变量说明
     */
    private String remark;

    /**
     * 所属部门ID
     */
    private String deptId;

    /**
     * 所属部门名称
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

    //    /**
    //     * 用户列表
    //     */
    //    private List<UserVo> userList;
}
