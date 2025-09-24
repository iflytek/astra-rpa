package com.iflytek.rpa.resource.file.entity;

import com.baomidou.mybatisplus.annotation.*;
import java.util.Date;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 文件表实体类
 *
 * @author system
 * @since 2024-01-01
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("file")
public class File {

    /**
     * 主键ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;

    /**
     * 文件对应的uuid
     */
    @TableField("file_id")
    private String fileId;

    /**
     * 文件在s3上对应的路径
     */
    @TableField("path")
    private String path;

    /**
     * 创建时间
     */
    @TableField(value = "create_time", fill = FieldFill.INSERT)
    private Date createTime;

    /**
     * 更新时间
     */
    @TableField(value = "update_time", fill = FieldFill.INSERT_UPDATE)
    private Date updateTime;

    /**
     * 逻辑删除标志位
     */
    @TableLogic
    @TableField("deleted")
    private Integer deleted;

    /**
     * 文件真实名称
     */
    @TableField("file_name")
    private String fileName;
}
