package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class RecordBaseInfoVo {
    /**
     * 执行者id
     */
    private String creatorId;
    /**
     * 执行者名称
     */
    private String executorName;
    /**
     * 开始时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date startTime;
    /**
     * 执行耗时 单位秒
     */
    private Long executeTime;
    /**
     * 执行结果
     * robotFail:失败
     * robotSuccess:成功
     * robotCancel:取消(中止)
     * robotExecute:正在执行
     */
    private String result;
    /**
     * 机器人版本号
     */
    private Integer robotVersion;
    /**
     * 执行id
     */
    private String executeId;
}
