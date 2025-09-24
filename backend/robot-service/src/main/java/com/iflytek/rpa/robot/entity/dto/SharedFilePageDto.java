package com.iflytek.rpa.robot.entity.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import lombok.Data;

/**
 * 共享文件分页查询DTO
 *
 * @author yfchen40
 * @date 2025-07-21
 */
@Data
public class SharedFilePageDto {
    // 文件名、创建时间、所有者、所属部门、更新时间、标签、分页信息
    /**
     * 共享文件名
     */
    private String fileName;

    /**
     * 开始创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date createTimeStart;

    /**
     * 结束创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date createTimeEnd;

    /**
     * 所有者
     */
    private String creator;

    /**
     * 所属部门
     */
    private String deptId;

    /**
     * 开始更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date updateTimeStart;

    /**
     * 结束更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd", timezone = "GMT+8")
    private Date updateTimeEnd;

    /**
     * 标签
     */
    private String tags;

    /**
     * 查询页数
     */
    private Integer pageNo = 1;

    /**
     * 每页大小
     */
    private Integer pageSize = 10;
}
