package com.iflytek.rpa.base.entity.dto;

import java.util.Date;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CRequireDto {
    /**
     * ID
     */
    private Integer id;
    /**
     * 工程ID
     */
    @NotBlank
    private String robotId;
    /**
     * 机器人版本
     */
    private Integer robotVersion;
    /**
     * 名称
     */
    private String packageName;
    /**
     * 版本
     */
    private String packageVersion;
    /**
     * 镜像源
     */
    private String mirror;
    /**
     * 创建者
     */
    private String creatorId;
    /**
     * 创建时间
     */
    private Date createTime;
    /**
     * 更新者
     */
    private String updaterId;
    /**
     * 更新时间
     */
    private Date updateTime;
    /**
     * 删除标志（0代表存在 1代表删除）
     */
    private Integer deleted = 0;
}
