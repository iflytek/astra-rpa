package com.iflytek.rpa.starter.entity;

public class PageEntity {
    private Long pageNo = 1L;
    private Long pageSize = 10L;

    public PageEntity() {}

    public Long getPageNo() {
        return this.pageNo;
    }

    public void setPageNo(final Long pageNo) {
        this.pageNo = pageNo;
    }

    public Long getPageSize() {
        return this.pageSize;
    }

    public void setPageSize(final Long pageSize) {
        this.pageSize = pageSize;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof PageEntity)) {
            return false;
        } else {
            PageEntity other = (PageEntity) o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                Object this$pageNo = this.getPageNo();
                Object other$pageNo = other.getPageNo();
                if (this$pageNo == null) {
                    if (other$pageNo != null) {
                        return false;
                    }
                } else if (!this$pageNo.equals(other$pageNo)) {
                    return false;
                }

                Object this$pageSize = this.getPageSize();
                Object other$pageSize = other.getPageSize();
                if (this$pageSize == null) {
                    return other$pageSize == null;
                } else return this$pageSize.equals(other$pageSize);
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof PageEntity;
    }

    public int hashCode() {
        boolean PRIME = true;
        int result = 1;
        Object $pageNo = this.getPageNo();
        result = result * 59 + ($pageNo == null ? 43 : $pageNo.hashCode());
        Object $pageSize = this.getPageSize();
        result = result * 59 + ($pageSize == null ? 43 : $pageSize.hashCode());
        return result;
    }

    public String toString() {
        return "PageEntity(pageNo=" + this.getPageNo() + ", pageSize=" + this.getPageSize() + ")";
    }
}
