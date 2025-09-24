package com.iflytek.rpa.robot.entity;

import java.io.Serializable;
import java.util.Date;

/**
 * 文件表(File)实体类
 *
 * @author mjren
 * @since 2024-11-07 10:26:27
 */
public class File implements Serializable {
    private static final long serialVersionUID = -82285542284681246L;
    /**
     * 主键ID
     */
    private Integer id;
    /**
     * 文件对应的uuid
     */
    private String fileId;
    /**
     * 文件在s3上对应的路径
     */
    private String path;
    /**
     * 创建时间
     */
    private Date createTime;
    /**
     * 更新时间
     */
    private Date updateTime;
    /**
     * 逻辑删除标志位
     */
    private Integer deleted;
    /**
     * 文件真实名称
     */
    private String fileName;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getFileId() {
        return fileId;
    }

    public void setFileId(String fileId) {
        this.fileId = fileId;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public Date getCreateTime() {
        return createTime;
    }

    public void setCreateTime(Date createTime) {
        this.createTime = createTime;
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

    public String getFileName() {
        return fileName;
    }

    public void setFileName(String fileName) {
        this.fileName = fileName;
    }
}
