package com.iflytek.rpa.robot.entity.vo;

import lombok.Data;

@Data
public class RobotExecutionTrendData {
    /**
     * 统计时间
     */
    private String countTime;
    /**
     * 执行成功次数
     */
    private Long executeSuccess = 0L;
    /**
     * 执行失败次数
     */
    private Long executeFail = 0L;
    /**
     * 执行中止次数
     */
    private Long executeAbort = 0L;
}
