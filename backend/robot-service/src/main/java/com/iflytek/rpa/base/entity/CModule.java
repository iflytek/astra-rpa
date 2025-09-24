package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.Null;
import lombok.Data;

/**
 * 客户端-python模块
 *
 * @author bywei4
 */
@Data
public class CModule implements Serializable {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    /**
     * 模块id
     */
    @Null
    private String moduleId;
    /**
     * 全量python代码数据
     */
    @Null
    private String moduleContent;
    /**
     * python文件名
     */
    @Null
    private String moduleName;

    private Integer deleted;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;

    @NotBlank
    private String robotId;

    @NotBlank
    private Integer robotVersion;
}
