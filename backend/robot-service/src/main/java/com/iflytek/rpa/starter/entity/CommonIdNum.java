package com.iflytek.rpa.starter.entity;

public class CommonIdNum<T> {
    private Long id;
    private Long num;
    private T target;

    public CommonIdNum() {}

    public Long getId() {
        return this.id;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public Long getNum() {
        return this.num;
    }

    public void setNum(final Long num) {
        this.num = num;
    }

    public T getTarget() {
        return this.target;
    }

    public void setTarget(final T target) {
        this.target = target;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof CommonIdNum)) {
            return false;
        } else {
            CommonIdNum<?> other = (CommonIdNum) o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                label47:
                {
                    Object this$id = this.getId();
                    Object other$id = other.getId();
                    if (this$id == null) {
                        if (other$id == null) {
                            break label47;
                        }
                    } else if (this$id.equals(other$id)) {
                        break label47;
                    }

                    return false;
                }

                Object this$num = this.getNum();
                Object other$num = other.getNum();
                if (this$num == null) {
                    if (other$num != null) {
                        return false;
                    }
                } else if (!this$num.equals(other$num)) {
                    return false;
                }

                Object this$target = this.getTarget();
                Object other$target = other.getTarget();
                if (this$target == null) {
                    return other$target == null;
                } else return this$target.equals(other$target);
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof CommonIdNum;
    }

    public int hashCode() {
        boolean PRIME = true;
        int result = 1;
        Object $id = this.getId();
        result = result * 59 + ($id == null ? 43 : $id.hashCode());
        Object $num = this.getNum();
        result = result * 59 + ($num == null ? 43 : $num.hashCode());
        Object $target = this.getTarget();
        result = result * 59 + ($target == null ? 43 : $target.hashCode());
        return result;
    }

    public String toString() {
        return "CommonIdNum(id=" + this.getId() + ", num=" + this.getNum() + ", target=" + this.getTarget() + ")";
    }
}
