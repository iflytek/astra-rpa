package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * 查询组件使用情况DTO
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class GetComponentUseDto {

    /**
     * 机器人ID
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 运行位置
     */
    @NotBlank(message = "运行位置不能为空")
    private String mode;

    /**
     * 机器人版本（允许为空）
     */
    private Integer version;
}
