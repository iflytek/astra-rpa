package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/*
 * 共享文件实体类
 */
@Data
public class SharedFile implements Serializable {
    private static final long serialVersionUID = -491204885219115201L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 文件id
     */
    private String fileId;
    /**
     * 共享文件名
     */
    private String fileName;
    /**
     * 文件类型
     */
    private Integer fileType;

    /**
     * 租户id
     */
    private String tenantId;
    /**
     * 文件向量化状态
     */
    private Integer fileIndexStatus;
    /**
     * 部门id
     */
    private String deptId;

    /**
     * 标签id集合
     */
    private String tags;

    /**
     * S3存储路径
     */
    private String path;

    /**
     * 创建者id
     */
    private String creatorId;

    /**
     * 创建时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    /**
     * 更新者id
     */
    private String updaterId;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}
