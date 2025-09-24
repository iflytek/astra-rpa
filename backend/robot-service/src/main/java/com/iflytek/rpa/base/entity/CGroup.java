package com.iflytek.rpa.base.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * 元素或图像的分组(CGroup)实体类
 *
 * @author mjren
 * @since 2024-12-04 10:28:54
 */
public class CGroup implements Serializable {
    private static final long serialVersionUID = -75854014685303649L;

    private Long id;

    private String groupId;

    private String groupName;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;

    private Integer deleted;

    private String robotId;

    private Integer robotVersion;

    private String elementType;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getGroupId() {
        return groupId;
    }

    public void setGroupId(String groupId) {
        this.groupId = groupId;
    }

    public String getGroupName() {
        return groupName;
    }

    public void setGroupName(String groupName) {
        this.groupName = groupName;
    }

    public String getCreatorId() {
        return creatorId;
    }

    public void setCreatorId(String creatorId) {
        this.creatorId = creatorId;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
    }

    public String getUpdaterId() {
        return updaterId;
    }

    public void setUpdaterId(String updaterId) {
        this.updaterId = updaterId;
    }

    public Date getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(Date updateTime) {
        this.updateTime = updateTime;
    }

    public Integer getDeleted() {
        return deleted;
    }

    public void setDeleted(Integer deleted) {
        this.deleted = deleted;
    }

    public String getRobotId() {
        return robotId;
    }

    public void setRobotId(String robotId) {
        this.robotId = robotId;
    }

    public Integer getRobotVersion() {
        return robotVersion;
    }

    public void setRobotVersion(Integer robotVersion) {
        this.robotVersion = robotVersion;
    }

    public String getElementType() {
        return elementType;
    }

    public void setElementType(String elementType) {
        this.elementType = elementType;
    }
}
