package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.Min;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class CreateVersionDto {
    @NotBlank(message = "组件id不能为空")
    String componentId; // 组件id

    @NotNull
    @Min(value = 1, message = "下一个版本号必须大于0")
    Integer nextVersion; // 版本

    @NotBlank(message = "更新日志不能为空")
    String updateLog; // 更新日志

    @NotBlank(message = "组件名字不能为空")
    String name; // 组件名字

    @NotBlank(message = "图像不能为空")
    String icon; // 图像

    @NotBlank(message = "简介不能为空")
    String introduction; // 简介
}
