package com.iflytek.rpa.component.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class ComponentInfoVo {
    String name; // 组件名称
    String icon; // 图像
    Integer latestVersion; // 最新版本
    String creatorName; // 创建者名称
    String introduction; // 最新版本的简介

    List<VersionInfo> versionInfoList;
}
