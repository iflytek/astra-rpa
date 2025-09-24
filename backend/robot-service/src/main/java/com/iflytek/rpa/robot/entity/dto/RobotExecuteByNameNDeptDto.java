package com.iflytek.rpa.robot.entity.dto;

import java.util.List;
import lombok.Data;

@Data
public class RobotExecuteByNameNDeptDto {
    String robotName;
    List<String> deptIdPathList; // 部门id全路径列表
    String deptIdPath; // 部门id全路径
    String tenantId;
}
