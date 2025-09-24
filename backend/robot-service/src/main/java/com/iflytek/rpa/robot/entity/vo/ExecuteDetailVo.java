package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class ExecuteDetailVo {
    // 基本信息
    String robotName;
    Integer versionNum;
    String fileName;
    String filePath;
    String videoName; // 视频名称
    String videoPath; // 视频路径
    String introduction;
    String useDescription;

    // 版本信息
    String sourceName; // 来源
    List<VersionInfo> versionInfoList; // 版本信息表

    // 创建者信息
    String creatorName;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    Date createTime;
}
