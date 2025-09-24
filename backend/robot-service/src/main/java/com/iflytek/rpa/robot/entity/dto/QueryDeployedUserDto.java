package com.iflytek.rpa.robot.entity.dto;

import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-15 10:12
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class QueryDeployedUserDto {

    @NotBlank(message = "手机号或姓名不能为空")
    private String keyword;

    @NotBlank(message = "机器人id不能为空")
    private String robotId;

    private Integer pageNo;

    private Integer pageSize;
}
