package com.iflytek.rpa.robot.entity.dto;

import com.iflytek.rpa.robot.entity.RobotVersion;
import lombok.Data;

@Data
// @ToString(callSuper = true)
public class RobotVersionDto extends RobotVersion {

    private String name;

    private String appendixName;

    private String videoName;

    private Integer enableLastVersion;

    //    @Valid
    //    private List<CProcess> processInfo;
    //
    //    public @Valid List<CProcess> getProcessInfo() {
    //        return processInfo;
    //    }
    //
    //    public void setProcessInfo(@Valid List<CProcess> processInfo) {
    //        this.processInfo = processInfo;
    //    }
}
