package com.iflytek.rpa.robot.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

@Data
public class RobotPageListDto {
    Integer pageSize = 10;

    Integer pageNo = 1;
    /**
     * 默认更新时间 (机器人产生新发版的时间)  可选 createTime 按照 创建时间
     */
    String sortBy = "latestReleaseTime";
    /**
     * 默认降序
     */
    String sortType = "desc";

    /**
     * 机器人名称
     */
    String robotName;
    /**
     * 所属部门id
     */
    String deptId;

    /**
     * 部门id全路径
     */
    String deptIdPath;

    /**
     * 创建人id
     */
    String creatorId;
    /**
     * 创建人姓名
     */
    String creatorName;
    /**
     * 租户id
     */
    String tenantId;

    /**
     * 创建时间起始
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date createTimeStart;
    /**
     * 创建时间结束
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date createTimeEnd;

    /**
     * 更新时间起始
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date latestReleaseTimeStart;
    /**
     * 更新时间结束
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    Date latestReleaseTimeEnd;
}
