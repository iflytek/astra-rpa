package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class RobotExecutionTrendDataVo {
    /**
     * 日列表
     */
    List<RobotExecutionTrendData> dayList;
    /**
     * 月列表
     */
    List<RobotExecutionTrendData> monthList;
}
