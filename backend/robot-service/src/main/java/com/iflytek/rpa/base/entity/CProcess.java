package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Null;
import lombok.Data;

/**
 * 流程项id数据(CProcess)实体类
 *
 * @author mjren
 * @since 2024-10-09 17:11:13
 */
@Data
public class CProcess implements Serializable {
    private static final long serialVersionUID = 533171820128533990L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    /**
     * 流程id
     */
    @Null
    private String processId;
    /**
     * 全量流程数据
     */
    @Null
    private String processContent;
    /**
     * 流程名称
     */
    @Null
    private String processName;

    private Integer deleted;

    private String creatorId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    private String updaterId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    @NotBlank
    private String robotId;

    @NotBlank
    private Integer robotVersion;
}
