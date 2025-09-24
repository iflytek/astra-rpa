package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class ExecuteListVo {
    String robotName; // 机器人名称

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    Date updateTime; // 更新时间

    Integer version; // 版本号
    String sourceName; // 来源名称 : 市场名称(团队市场名称或者官方市场)、本地
    String robotId; // 机器人
    String appId; // 如果是从市场获取，对应appId
    Integer updateStatus; // 是否有更新 标识位 1 是 0 无
    Integer usePermission; // 使用权限 0 无 1 有
    Date expiryDate; // 红色密级标识的截止时间
    String expiryDateStr; // 红色密级标识的截止时间提示
}
