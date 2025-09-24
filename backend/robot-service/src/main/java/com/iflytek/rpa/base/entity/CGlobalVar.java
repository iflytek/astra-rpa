package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 客户端-全局变量(CGlobalVar)实体类
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Data
public class CGlobalVar implements Serializable {
    private static final long serialVersionUID = 717602017394683626L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String projectId;

    private String globalId;

    private String varName;

    private String varType;

    private String varValue;

    private String varDescribe;

    private Integer deleted;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;

    private String robotId;

    private Integer robotVersion;
}
