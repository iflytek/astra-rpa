package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 流程参数表
 *
 * @author tzzhang
 * @since
 */
@Data
public class CParam implements Serializable {
    private static final long serialVersionUID = -2745694034538081329L;

    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private String id;

    /**
     * 参数流向
     */
    private int varDirection;

    /**
     * 参数名称
     */
    private String varName;

    /**
     * 参数类型
     */
    private String varType;

    /**
     * 参数内容
     */
    private String varValue;

    /**
     * 参数描述
     */
    private String varDescribe;

    /**
     * 流程id
     */
    private String processId;

    private String creatorId;

    private String updaterId;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createTime;

    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    private Integer deleted;

    private String robotId;

    private Integer robotVersion;
}
