package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.fasterxml.jackson.annotation.JsonFormat;
import java.io.Serializable;
import java.util.Date;
import lombok.Data;

/**
 * 云端机器人表(RobotExecute)实体类
 *
 * @author mjren
 * @since 2024-10-22 16:07:33
 */
@Data
public class RobotExecute implements Serializable {
    private static final long serialVersionUID = -49733269650418210L;
    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;
    /**
     * 机器人唯一id，获取的应用id
     */
    private String robotId;
    /**
     * 当前名字，用于列表展示
     */
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
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;

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
     * 资源状态：toObtain, obtaining, obtained, toUpdate, updating
     */
    private String resourceStatus;
    /**
     * 来源：create 自己创建 ； market 市场获取
     */
    private String dataSource;

    private String paramDetail;

    /**
     * 部门id路径，用于根据部门统计机器人数量
     */
    private String deptIdPath;

    @TableField(exist = false)
    private Boolean isCreator;

    /**
     * 最新版本机器人的类型，web，other
     */
    private String type;

    /**
     * 最新版本 发版时间
     */
    private Date latestReleaseTime;

    @TableField(exist = false)
    private Integer robotVersion;

    @TableField(exist = false)
    private String introduction;
}
