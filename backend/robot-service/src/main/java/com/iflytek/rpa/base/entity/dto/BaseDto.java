package com.iflytek.rpa.base.entity.dto;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class BaseDto {

    private String id;

    private String name;

    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    private Integer robotVersion;

    @NotBlank(message = "运行位置不能为空")
    private String mode = EDIT_PAGE;

    private String processId;

    private String groupId;

    private String elementId;

    private String globalId;

    private String elementType;

    private String creatorId;
}
