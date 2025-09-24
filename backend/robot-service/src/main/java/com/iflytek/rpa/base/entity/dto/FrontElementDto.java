package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

@Data
public class FrontElementDto extends FrontCommonDto {

    /**
     * 图标
     */
    private String icon;
    /**
     * 图片id
     */
    private String imageId;

    /**
     * 元素的父级图片id
     */
    private String parentImageId;

    /**
     * 元素内容
     */
    private String elementData;

    private String commonSubType;
}
