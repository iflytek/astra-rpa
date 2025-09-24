package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CheckNameDto {

    @NotBlank(message = "组件新名称不能为空")
    String name;

    String componentId; // 组件id
}
