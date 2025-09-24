package com.iflytek.rpa.robot.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class MarketRobotDetailVo {

    MyRobotDetailVo myRobotDetailVo;

    // 原版本信息
    String sourceName;
    List<VersionInfo> versionInfoList;
}
