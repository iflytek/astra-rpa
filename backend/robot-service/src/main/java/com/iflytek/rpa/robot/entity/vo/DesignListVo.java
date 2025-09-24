package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class DesignListVo {
    String robotName; // 机器人名称

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    Date updateTime; // 更新时间

    String publishStatus; // 发布状态 editing published shared locked
    /**
     * 上架申请状态 pending:申请中 approved:申请已通过 none:无申请记录 null:上架审核未开启
     */
    String applicationStatus;

    Integer version; // 启用版本号
    Integer latestVersion; // 最新版本号
    String iconUrl; // 图标名字
    String robotId; // 机器人id
    Integer editEnable; // 是否允许编辑 1能编辑，0不能编辑
}
