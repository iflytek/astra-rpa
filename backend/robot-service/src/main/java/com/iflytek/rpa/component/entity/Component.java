package com.iflytek.rpa.component.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import javax.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

/**
 * 组件表(Component)实体类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Component implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 机器人唯一id，获取的应用id
     */
    private String componentId;

    /**
     * 当前名字，用于列表展示
     */
    @NotBlank(message = "组件名称不能为空")
    @Length(max = 100, message = "组件名称不能超过100个字符")
    private String name;

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
     * 是否在用户列表页显示 0：不显示，1：显示
     */
    private Integer isShown;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * appmarketResource中的应用id
     */
    private String appId;

    /**
     * 获取的应用：应用市场版本
     */
    private Integer appVersion;

    /**
     * 获取的应用：市场id
     */
    private String marketId;

    /**
     * 资源状态：toObtain, obtained, toUpdate
     */
    private String resourceStatus;

    /**
     * 来源：create 自己创建 ； market 市场获取
     */
    private String dataSource;

    /**
     * editing 编辑中，published 已发版，shared 已上架，locked锁定（无法编辑）
     */
    private String transformStatus;
}
