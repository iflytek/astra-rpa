package com.iflytek.rpa.robot.entity.vo;

import java.util.Date;
import lombok.Data;

@Data
public class VersionDetailVo {
    Integer versionNum;
    Date updateTime;
    String updateLog;
    String online; // enable 启动 ； disable 未启用
    String robotId;
}
