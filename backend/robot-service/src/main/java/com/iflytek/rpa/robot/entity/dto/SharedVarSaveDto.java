package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * 共享变量保存DTO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarSaveDto {

    /**
     * 变量名
     */
    @NotBlank(message = "变量名不能为空")
    private String sharedVarName;

    /**
     * 所属部门ID
     */
    @NotBlank(message = "所属部门不能为空")
    private String deptId;

    /**
     * 变量类型：text/password/array/group
     */
    @NotBlank(message = "变量类型不能为空")
    private String varType;

    /**
     * 启用状态：1启用，0禁用
     */
    @NotNull(message = "启用状态不能为空")
    private Integer status;

    /**
     * 变量说明
     */
    private String remark;

    /**
     * 可使用账号类别(all/dept/select)
     */
    @NotBlank(message = "可使用账号不能为空")
    private String usageType;

    /**
     * 已选择的用户列表
     */
    @Valid
    private List<SelectedUser> selectedUserList;

    /**
     * 变量组列表, 不是变量组类型，相当于一个元素的列表
     */
    @Valid
    private List<VarGroupItem> varList;

    /**
     * 选中的用户信息
     */
    @Data
    public static class SelectedUser {
        @NotBlank(message = "userId不能为空")
        private String userId; // 用户ID

        @NotBlank(message = "userName不能为空")
        private String userName; // 用户名

        @NotBlank(message = "userPhone不能为空")
        private String userPhone; // 用户手机号
    }

    /**
     * 变量组项
     */
    @Data
    public static class VarGroupItem {
        @NotBlank(message = "变量名不能为空")
        private String varName; // 变量名

        @NotBlank(message = "变量类型不能为空")
        private String varType; // 变量类型 text/password/array

        private String varValue; // 变量值
        private Integer encrypt; // 是否加密：1-加密，0-不加密
    }
}
