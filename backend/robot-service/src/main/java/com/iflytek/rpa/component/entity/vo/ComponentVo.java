package com.iflytek.rpa.component.entity.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 组件视图对象
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class ComponentVo implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 机器人唯一id，获取的应用id
     */
    private String componentId;

    /**
     * 当前名字，用于列表展示
     */
    private String name;

    /**
     * 更新时间
     */
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateTime;

    /**
     * editing 编辑中，published 已发版，shared 已上架，locked锁定（无法编辑）
     */
    private String transformStatus;

    /**
     * 组件对应的最新版本号，如果没有componentVersion，为空即可
     */
    private Integer version;
}
