package com.iflytek.rpa.base.entity.dto;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import com.iflytek.rpa.base.entity.CElement;
import lombok.Data;

@Data
public class ServerBaseDto {

    /**
     * 指定工程在哪个阶段运行；工程编辑页 EDIT_PAGE ;工程列表页 PROJECT_LIST; 执行器运行 EXECUTOR; 计划任务启动 CRONTAB;
     */
    private String mode = EDIT_PAGE;

    private String elementType;

    private String robotId;

    private Integer robotVersion;

    private String groupId;

    private String groupName;

    private String elementName;

    private String elementId;

    private String creatorId;

    // =============================================================================

    private CElement element;

    private String processName;

    //    private String groupId;
    //    /**
    //     * 元素id
    //     */
    //    private String elementId;
    //    /**
    //     * 元素名称
    //     */
    //    private String elementName;
    //    /**
    //     * 图标
    //     */
    //    private String icon;
    //    /**
    //     * 图片id
    //     */
    //    private String imageId;
    //    /**
    //     * 元素的父级图片id
    //     */
    //    private String parentImageId;
    //    /**
    //     * 元素内容
    //     */
    //    private String elementData;

}
