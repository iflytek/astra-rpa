package com.iflytek.rpa.robot.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class SharedFilePageVo {
    private Long id;
    /*
     *  文件ID
     */
    private String fileId; // 文件ID
    /*
     *  文件名
     */
    private String fileName; // 文件名
    /**
     * 文件类型
     */
    private Integer fileType;
    /*
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime; // 创建时间
    /*
     *  更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;
    /*
     *  创建者名称
     */
    private String creatorName; // 创建者
    /*
     *  账号
     */
    private String phone;
    /*
     *  部门id
     */
    private String deptId;
    /*
     *  部门名称
     */
    private String deptName;
    /**
     * 文件标签id集合
     */
    private List<String> tags;
    /**
     * 文件标签名称集合
     */
    private List<String> tagsNames;

    /*
     * 文件路径
     */
    private String filePath; // 文件路径
}
