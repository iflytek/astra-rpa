package com.iflytek.rpa.robot.entity.vo;

import java.util.Date;
import lombok.Data;

@Data
public class MyRobotDetailVo {
    String name;
    Integer version;
    String introduction; // 简介
    String useDescription; // 使用说明

    String fileName; // 文件名称
    String filePath; // 文件路径

    String videoName; // 视频名称
    String videoPath; // 视频路径

    String creatorName;
    Date createTime;
    /**
     * 所属部门
     */
    String deptName;
    /**
     * 更新时间
     */
    Date updateTime;
    /**
     * 机器人Id
     */
    String robotId;
}
