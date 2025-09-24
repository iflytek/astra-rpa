package com.iflytek.rpa.base.entity.vo;

import lombok.Data;

@Data
public class ElementVo {
    /**
     * 元素id
     */
    private String id;

    /**
     * 元素名称
     */
    private String name;
    /**
     * 图标
     */
    private String icon;
    //    /**
    //     * 图片id
    //     */
    //    @JsonIgnore
    //    private String imageId;
    //
    //    /**
    //     * 元素的父级图片id
    //     */
    //    @JsonIgnore
    //    private String parentImageId;

    /**
     * 图片下载地址
     */
    private String imageUrl;

    /**
     * 元素的父级图片下载地址
     */
    private String parentImageUrl;

    /**
     * 元素内容
     */
    private String elementData;
}
