package com.iflytek.rpa.robot.entity.vo;

import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class ResourceVersionListVo {
    List<ResourceVersion> versionDetailList;

    @Data
    public static class ResourceVersion {
        Integer version;
        Date updateTime;
        String updateLog;
        String online; // enable 启动 ； disable 未启用
        String robotId;
    }
}
