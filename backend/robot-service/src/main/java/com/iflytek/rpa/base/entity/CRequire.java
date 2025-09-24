package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * python依赖管理(CRequire)实体类
 *
 * @author mjren
 * @since 2024-10-14 17:21:35
 */
@Data
public class CRequire implements Serializable {
    private static final long serialVersionUID = -96631614802732786L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String projectId;
    /**
     * 项目名称
     */
    private String packageName;

    private String packageVersion;

    private String mirror;
    /**
     * 创建者id
     */
    private String creatorId;
    /**
     * 创建时间
     */
    private Date createTime;
    /**
     * 更新者id
     */
    private String updaterId;
    /**
     * 创建时间
     */
    private Date updateTime;
    /**
     * 逻辑删除 0：未删除 1：已删除
     */
    private Integer deleted;

    @NotBlank
    private String robotId;

    @NotBlank
    private Integer robotVersion;
}
