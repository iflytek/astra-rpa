package com.iflytek.rpa.starter.entity;

public class Actor {
    private Long id;
    private String account;
    private String name;

    public Actor() {}

    public Long getId() {
        return this.id;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public String getAccount() {
        return this.account;
    }

    public void setAccount(final String account) {
        this.account = account;
    }

    public String getName() {
        return this.name;
    }

    public void setName(final String name) {
        this.name = name;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof Actor)) {
            return false;
        } else {
            Actor other = (Actor) o;
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

                Object this$account = this.getAccount();
                Object other$account = other.getAccount();
                if (this$account == null) {
                    if (other$account != null) {
                        return false;
                    }
                } else if (!this$account.equals(other$account)) {
                    return false;
                }

                Object this$name = this.getName();
                Object other$name = other.getName();
                if (this$name == null) {
                    return other$name == null;
                } else return this$name.equals(other$name);
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof Actor;
    }

    public int hashCode() {
        boolean PRIME = true;
        int result = 1;
        Object $id = this.getId();
        result = result * 59 + ($id == null ? 43 : $id.hashCode());
        Object $account = this.getAccount();
        result = result * 59 + ($account == null ? 43 : $account.hashCode());
        Object $name = this.getName();
        result = result * 59 + ($name == null ? 43 : $name.hashCode());
        return result;
    }

    public String toString() {
        return "Actor(id=" + this.getId() + ", account=" + this.getAccount() + ", name=" + this.getName() + ")";
    }
}
