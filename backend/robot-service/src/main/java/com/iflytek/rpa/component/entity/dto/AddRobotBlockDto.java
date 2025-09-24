package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 添加机器人屏蔽记录数据传输对象
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class AddRobotBlockDto {

    /**
     * 机器人id
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 发起请求的位置
     */
    @NotBlank(message = "mode不能为空")
    private String mode;

    /**
     * 机器人版本号
     */
    private Integer robotVersion;

    /**
     * 组件id
     */
    @NotBlank(message = "组件ID不能为空")
    private String componentId;
}
