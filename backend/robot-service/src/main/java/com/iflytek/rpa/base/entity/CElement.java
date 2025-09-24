package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 客户端，元素信息(CElement)实体类
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Data
public class CElement implements Serializable {
    private static final long serialVersionUID = -53914169890628551L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 分组id
     */
    private String groupId;

    /**
     * 元素拾取类型：sigle普通拾取，batch数据抓取
     */
    private String commonSubType;

    /**
     * 元素id
     */
    private String elementId;
    /**
     * 元素名称
     */
    private String elementName;
    /**
     * 图标
     */
    private String icon;
    /**
     * 图片下载id
     */
    private String imageId;
    /**
     * 元素内容
     */
    private String elementData;

    private Integer deleted;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;
    /**
     * 元素的父级图片id
     */
    private String parentImageId;

    private String robotId;

    private Integer robotVersion;
}
