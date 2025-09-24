package com.iflytek.rpa.starter.entity;

import java.util.List;

public class DataAuthDetailDo {
    private String dataAuthType;
    private List<String> deptIdList;
    private List<String> deptIdPathList;

    public DataAuthDetailDo() {}

    public String getDataAuthType() {
        return this.dataAuthType;
    }

    public void setDataAuthType(final String dataAuthType) {
        this.dataAuthType = dataAuthType;
    }

    public List<String> getDeptIdList() {
        return this.deptIdList;
    }

    public void setDeptIdList(final List<String> deptIdList) {
        this.deptIdList = deptIdList;
    }

    public List<String> getDeptIdPathList() {
        return this.deptIdPathList;
    }

    public void setDeptIdPathList(final List<String> deptIdPathList) {
        this.deptIdPathList = deptIdPathList;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof DataAuthDetailDo)) {
            return false;
        } else {
            DataAuthDetailDo other = (DataAuthDetailDo) o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                label47:
                {
                    Object this$dataAuthType = this.getDataAuthType();
                    Object other$dataAuthType = other.getDataAuthType();
                    if (this$dataAuthType == null) {
                        if (other$dataAuthType == null) {
                            break label47;
                        }
                    } else if (this$dataAuthType.equals(other$dataAuthType)) {
                        break label47;
                    }

                    return false;
                }

                Object this$deptIdList = this.getDeptIdList();
                Object other$deptIdList = other.getDeptIdList();
                if (this$deptIdList == null) {
                    if (other$deptIdList != null) {
                        return false;
                    }
                } else if (!this$deptIdList.equals(other$deptIdList)) {
                    return false;
                }

                Object this$deptIdPathList = this.getDeptIdPathList();
                Object other$deptIdPathList = other.getDeptIdPathList();
                if (this$deptIdPathList == null) {
                    return other$deptIdPathList == null;
                } else return this$deptIdPathList.equals(other$deptIdPathList);
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof DataAuthDetailDo;
    }

    public int hashCode() {
        boolean PRIME = true;
        int result = 1;
        Object $dataAuthType = this.getDataAuthType();
        result = result * 59 + ($dataAuthType == null ? 43 : $dataAuthType.hashCode());
        Object $deptIdList = this.getDeptIdList();
        result = result * 59 + ($deptIdList == null ? 43 : $deptIdList.hashCode());
        Object $deptIdPathList = this.getDeptIdPathList();
        result = result * 59 + ($deptIdPathList == null ? 43 : $deptIdPathList.hashCode());
        return result;
    }

    public String toString() {
        return "DataAuthDetailDo(dataAuthType=" + this.getDataAuthType() + ", deptIdList=" + this.getDeptIdList()
                + ", deptIdPathList=" + this.getDeptIdPathList() + ")";
    }
}
