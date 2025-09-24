package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import javax.validation.constraints.NotNull;
import lombok.Data;

@Data
public class RobotExecuteRecordsBatchDeleteDto {

    /**
     * 机器人执行记录ID List
     */
    @NotNull(message = "执行记录ID-List不能为空")
    private List<String> recordIds;
}
