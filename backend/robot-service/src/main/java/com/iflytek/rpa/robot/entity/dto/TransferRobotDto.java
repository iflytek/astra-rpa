package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-07-01 15:17
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class TransferRobotDto {

    private List<String> robotIdList;

    @NotBlank(message = "新所有者不能为空")
    private String userId;
}
