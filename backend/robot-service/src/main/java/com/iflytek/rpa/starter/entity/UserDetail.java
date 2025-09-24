package com.iflytek.rpa.starter.entity;

import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.List;

public class UserDetail {
    private Long id;
    private String uuid;
    private String redisUUid;
    private String username;
    private String phone;
    private String email;
    private ZonedDateTime registerTime;
    private Integer oauthTypeId;
    private Integer authFlag;
    private String password;
    private ZonedDateTime createTime;
    private ZonedDateTime updateTime;
    private String nickName;
    private Integer gender;
    private String avatorUrl;
    private Integer lastLoginOauthTypeId;
    private ZonedDateTime lastLoginTime;
    private Boolean deleted;
    private Boolean hasPassword = false;
    private Boolean accountNonExpired;
    private Boolean accountNonLocked;
    private Boolean credentialsNonExpired;
    private List<String> userOwnedPath = new ArrayList();

    public UserDetail() {}

    public Long getId() {
        return this.id;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(final String uuid) {
        this.uuid = uuid;
    }

    public String getRedisUUid() {
        return this.redisUUid;
    }

    public void setRedisUUid(final String redisUUid) {
        this.redisUUid = redisUUid;
    }

    public String getUsername() {
        return this.username;
    }

    public void setUsername(final String username) {
        this.username = username;
    }

    public String getPhone() {
        return this.phone;
    }

    public void setPhone(final String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(final String email) {
        this.email = email;
    }

    public ZonedDateTime getRegisterTime() {
        return this.registerTime;
    }

    public void setRegisterTime(final ZonedDateTime registerTime) {
        this.registerTime = registerTime;
    }

    public Integer getOauthTypeId() {
        return this.oauthTypeId;
    }

    public void setOauthTypeId(final Integer oauthTypeId) {
        this.oauthTypeId = oauthTypeId;
    }

    public Integer getAuthFlag() {
        return this.authFlag;
    }

    public void setAuthFlag(final Integer authFlag) {
        this.authFlag = authFlag;
    }

    public String getPassword() {
        return this.password;
    }

    public void setPassword(final String password) {
        this.password = password;
    }

    public ZonedDateTime getCreateTime() {
        return this.createTime;
    }

    public void setCreateTime(final ZonedDateTime createTime) {
        this.createTime = createTime;
    }

    public ZonedDateTime getUpdateTime() {
        return this.updateTime;
    }

    public void setUpdateTime(final ZonedDateTime updateTime) {
        this.updateTime = updateTime;
    }

    public String getNickName() {
        return this.nickName;
    }

    public void setNickName(final String nickName) {
        this.nickName = nickName;
    }

    public Integer getGender() {
        return this.gender;
    }

    public void setGender(final Integer gender) {
        this.gender = gender;
    }

    public String getAvatorUrl() {
        return this.avatorUrl;
    }

    public void setAvatorUrl(final String avatorUrl) {
        this.avatorUrl = avatorUrl;
    }

    public Integer getLastLoginOauthTypeId() {
        return this.lastLoginOauthTypeId;
    }

    public void setLastLoginOauthTypeId(final Integer lastLoginOauthTypeId) {
        this.lastLoginOauthTypeId = lastLoginOauthTypeId;
    }

    public ZonedDateTime getLastLoginTime() {
        return this.lastLoginTime;
    }

    public void setLastLoginTime(final ZonedDateTime lastLoginTime) {
        this.lastLoginTime = lastLoginTime;
    }

    public Boolean getDeleted() {
        return this.deleted;
    }

    public void setDeleted(final Boolean deleted) {
        this.deleted = deleted;
    }

    public Boolean getHasPassword() {
        return this.hasPassword;
    }

    public void setHasPassword(final Boolean hasPassword) {
        this.hasPassword = hasPassword;
    }

    public Boolean getAccountNonExpired() {
        return this.accountNonExpired;
    }

    public void setAccountNonExpired(final Boolean accountNonExpired) {
        this.accountNonExpired = accountNonExpired;
    }

    public Boolean getAccountNonLocked() {
        return this.accountNonLocked;
    }

    public void setAccountNonLocked(final Boolean accountNonLocked) {
        this.accountNonLocked = accountNonLocked;
    }

    public Boolean getCredentialsNonExpired() {
        return this.credentialsNonExpired;
    }

    public void setCredentialsNonExpired(final Boolean credentialsNonExpired) {
        this.credentialsNonExpired = credentialsNonExpired;
    }

    public List<String> getUserOwnedPath() {
        return this.userOwnedPath;
    }

    public void setUserOwnedPath(final List<String> userOwnedPath) {
        this.userOwnedPath = userOwnedPath;
    }

    public boolean equals(final Object o) {
        if (o == this) {
            return true;
        } else if (!(o instanceof UserDetail)) {
            return false;
        } else {
            UserDetail other = (UserDetail) o;
            if (!other.canEqual(this)) {
                return false;
            } else {
                label287:
                {
                    Object this$id = this.getId();
                    Object other$id = other.getId();
                    if (this$id == null) {
                        if (other$id == null) {
                            break label287;
                        }
                    } else if (this$id.equals(other$id)) {
                        break label287;
                    }

                    return false;
                }

                Object this$oauthTypeId = this.getOauthTypeId();
                Object other$oauthTypeId = other.getOauthTypeId();
                if (this$oauthTypeId == null) {
                    if (other$oauthTypeId != null) {
                        return false;
                    }
                } else if (!this$oauthTypeId.equals(other$oauthTypeId)) {
                    return false;
                }

                Object this$authFlag = this.getAuthFlag();
                Object other$authFlag = other.getAuthFlag();
                if (this$authFlag == null) {
                    if (other$authFlag != null) {
                        return false;
                    }
                } else if (!this$authFlag.equals(other$authFlag)) {
                    return false;
                }

                label266:
                {
                    Object this$gender = this.getGender();
                    Object other$gender = other.getGender();
                    if (this$gender == null) {
                        if (other$gender == null) {
                            break label266;
                        }
                    } else if (this$gender.equals(other$gender)) {
                        break label266;
                    }

                    return false;
                }

                label259:
                {
                    Object this$lastLoginOauthTypeId = this.getLastLoginOauthTypeId();
                    Object other$lastLoginOauthTypeId = other.getLastLoginOauthTypeId();
                    if (this$lastLoginOauthTypeId == null) {
                        if (other$lastLoginOauthTypeId == null) {
                            break label259;
                        }
                    } else if (this$lastLoginOauthTypeId.equals(other$lastLoginOauthTypeId)) {
                        break label259;
                    }

                    return false;
                }

                Object this$deleted = this.getDeleted();
                Object other$deleted = other.getDeleted();
                if (this$deleted == null) {
                    if (other$deleted != null) {
                        return false;
                    }
                } else if (!this$deleted.equals(other$deleted)) {
                    return false;
                }

                Object this$hasPassword = this.getHasPassword();
                Object other$hasPassword = other.getHasPassword();
                if (this$hasPassword == null) {
                    if (other$hasPassword != null) {
                        return false;
                    }
                } else if (!this$hasPassword.equals(other$hasPassword)) {
                    return false;
                }

                label238:
                {
                    Object this$accountNonExpired = this.getAccountNonExpired();
                    Object other$accountNonExpired = other.getAccountNonExpired();
                    if (this$accountNonExpired == null) {
                        if (other$accountNonExpired == null) {
                            break label238;
                        }
                    } else if (this$accountNonExpired.equals(other$accountNonExpired)) {
                        break label238;
                    }

                    return false;
                }

                label231:
                {
                    Object this$accountNonLocked = this.getAccountNonLocked();
                    Object other$accountNonLocked = other.getAccountNonLocked();
                    if (this$accountNonLocked == null) {
                        if (other$accountNonLocked == null) {
                            break label231;
                        }
                    } else if (this$accountNonLocked.equals(other$accountNonLocked)) {
                        break label231;
                    }

                    return false;
                }

                Object this$credentialsNonExpired = this.getCredentialsNonExpired();
                Object other$credentialsNonExpired = other.getCredentialsNonExpired();
                if (this$credentialsNonExpired == null) {
                    if (other$credentialsNonExpired != null) {
                        return false;
                    }
                } else if (!this$credentialsNonExpired.equals(other$credentialsNonExpired)) {
                    return false;
                }

                label217:
                {
                    Object this$uuid = this.getUuid();
                    Object other$uuid = other.getUuid();
                    if (this$uuid == null) {
                        if (other$uuid == null) {
                            break label217;
                        }
                    } else if (this$uuid.equals(other$uuid)) {
                        break label217;
                    }

                    return false;
                }

                Object this$redisUUid = this.getRedisUUid();
                Object other$redisUUid = other.getRedisUUid();
                if (this$redisUUid == null) {
                    if (other$redisUUid != null) {
                        return false;
                    }
                } else if (!this$redisUUid.equals(other$redisUUid)) {
                    return false;
                }

                label203:
                {
                    Object this$username = this.getUsername();
                    Object other$username = other.getUsername();
                    if (this$username == null) {
                        if (other$username == null) {
                            break label203;
                        }
                    } else if (this$username.equals(other$username)) {
                        break label203;
                    }

                    return false;
                }

                Object this$phone = this.getPhone();
                Object other$phone = other.getPhone();
                if (this$phone == null) {
                    if (other$phone != null) {
                        return false;
                    }
                } else if (!this$phone.equals(other$phone)) {
                    return false;
                }

                Object this$email = this.getEmail();
                Object other$email = other.getEmail();
                if (this$email == null) {
                    if (other$email != null) {
                        return false;
                    }
                } else if (!this$email.equals(other$email)) {
                    return false;
                }

                label182:
                {
                    Object this$registerTime = this.getRegisterTime();
                    Object other$registerTime = other.getRegisterTime();
                    if (this$registerTime == null) {
                        if (other$registerTime == null) {
                            break label182;
                        }
                    } else if (this$registerTime.equals(other$registerTime)) {
                        break label182;
                    }

                    return false;
                }

                label175:
                {
                    Object this$password = this.getPassword();
                    Object other$password = other.getPassword();
                    if (this$password == null) {
                        if (other$password == null) {
                            break label175;
                        }
                    } else if (this$password.equals(other$password)) {
                        break label175;
                    }

                    return false;
                }

                Object this$createTime = this.getCreateTime();
                Object other$createTime = other.getCreateTime();
                if (this$createTime == null) {
                    if (other$createTime != null) {
                        return false;
                    }
                } else if (!this$createTime.equals(other$createTime)) {
                    return false;
                }

                Object this$updateTime = this.getUpdateTime();
                Object other$updateTime = other.getUpdateTime();
                if (this$updateTime == null) {
                    if (other$updateTime != null) {
                        return false;
                    }
                } else if (!this$updateTime.equals(other$updateTime)) {
                    return false;
                }

                label154:
                {
                    Object this$nickName = this.getNickName();
                    Object other$nickName = other.getNickName();
                    if (this$nickName == null) {
                        if (other$nickName == null) {
                            break label154;
                        }
                    } else if (this$nickName.equals(other$nickName)) {
                        break label154;
                    }

                    return false;
                }

                label147:
                {
                    Object this$avatorUrl = this.getAvatorUrl();
                    Object other$avatorUrl = other.getAvatorUrl();
                    if (this$avatorUrl == null) {
                        if (other$avatorUrl == null) {
                            break label147;
                        }
                    } else if (this$avatorUrl.equals(other$avatorUrl)) {
                        break label147;
                    }

                    return false;
                }

                Object this$lastLoginTime = this.getLastLoginTime();
                Object other$lastLoginTime = other.getLastLoginTime();
                if (this$lastLoginTime == null) {
                    if (other$lastLoginTime != null) {
                        return false;
                    }
                } else if (!this$lastLoginTime.equals(other$lastLoginTime)) {
                    return false;
                }

                Object this$userOwnedPath = this.getUserOwnedPath();
                Object other$userOwnedPath = other.getUserOwnedPath();
                if (this$userOwnedPath == null) {
                    return other$userOwnedPath == null;
                } else return this$userOwnedPath.equals(other$userOwnedPath);
            }
        }
    }

    protected boolean canEqual(final Object other) {
        return other instanceof UserDetail;
    }

    public int hashCode() {
        boolean PRIME = true;
        int result = 1;
        Object $id = this.getId();
        result = result * 59 + ($id == null ? 43 : $id.hashCode());
        Object $oauthTypeId = this.getOauthTypeId();
        result = result * 59 + ($oauthTypeId == null ? 43 : $oauthTypeId.hashCode());
        Object $authFlag = this.getAuthFlag();
        result = result * 59 + ($authFlag == null ? 43 : $authFlag.hashCode());
        Object $gender = this.getGender();
        result = result * 59 + ($gender == null ? 43 : $gender.hashCode());
        Object $lastLoginOauthTypeId = this.getLastLoginOauthTypeId();
        result = result * 59 + ($lastLoginOauthTypeId == null ? 43 : $lastLoginOauthTypeId.hashCode());
        Object $deleted = this.getDeleted();
        result = result * 59 + ($deleted == null ? 43 : $deleted.hashCode());
        Object $hasPassword = this.getHasPassword();
        result = result * 59 + ($hasPassword == null ? 43 : $hasPassword.hashCode());
        Object $accountNonExpired = this.getAccountNonExpired();
        result = result * 59 + ($accountNonExpired == null ? 43 : $accountNonExpired.hashCode());
        Object $accountNonLocked = this.getAccountNonLocked();
        result = result * 59 + ($accountNonLocked == null ? 43 : $accountNonLocked.hashCode());
        Object $credentialsNonExpired = this.getCredentialsNonExpired();
        result = result * 59 + ($credentialsNonExpired == null ? 43 : $credentialsNonExpired.hashCode());
        Object $uuid = this.getUuid();
        result = result * 59 + ($uuid == null ? 43 : $uuid.hashCode());
        Object $redisUUid = this.getRedisUUid();
        result = result * 59 + ($redisUUid == null ? 43 : $redisUUid.hashCode());
        Object $username = this.getUsername();
        result = result * 59 + ($username == null ? 43 : $username.hashCode());
        Object $phone = this.getPhone();
        result = result * 59 + ($phone == null ? 43 : $phone.hashCode());
        Object $email = this.getEmail();
        result = result * 59 + ($email == null ? 43 : $email.hashCode());
        Object $registerTime = this.getRegisterTime();
        result = result * 59 + ($registerTime == null ? 43 : $registerTime.hashCode());
        Object $password = this.getPassword();
        result = result * 59 + ($password == null ? 43 : $password.hashCode());
        Object $createTime = this.getCreateTime();
        result = result * 59 + ($createTime == null ? 43 : $createTime.hashCode());
        Object $updateTime = this.getUpdateTime();
        result = result * 59 + ($updateTime == null ? 43 : $updateTime.hashCode());
        Object $nickName = this.getNickName();
        result = result * 59 + ($nickName == null ? 43 : $nickName.hashCode());
        Object $avatorUrl = this.getAvatorUrl();
        result = result * 59 + ($avatorUrl == null ? 43 : $avatorUrl.hashCode());
        Object $lastLoginTime = this.getLastLoginTime();
        result = result * 59 + ($lastLoginTime == null ? 43 : $lastLoginTime.hashCode());
        Object $userOwnedPath = this.getUserOwnedPath();
        result = result * 59 + ($userOwnedPath == null ? 43 : $userOwnedPath.hashCode());
        return result;
    }

    public String toString() {
        return "UserDetail(id=" + this.getId() + ", uuid=" + this.getUuid() + ", redisUUid=" + this.getRedisUUid()
                + ", username=" + this.getUsername() + ", phone=" + this.getPhone() + ", email=" + this.getEmail()
                + ", registerTime=" + this.getRegisterTime() + ", oauthTypeId=" + this.getOauthTypeId() + ", authFlag="
                + this.getAuthFlag() + ", password=" + this.getPassword() + ", createTime=" + this.getCreateTime()
                + ", updateTime=" + this.getUpdateTime() + ", nickName=" + this.getNickName() + ", gender="
                + this.getGender() + ", avatorUrl=" + this.getAvatorUrl() + ", lastLoginOauthTypeId="
                + this.getLastLoginOauthTypeId() + ", lastLoginTime=" + this.getLastLoginTime() + ", deleted="
                + this.getDeleted() + ", hasPassword=" + this.getHasPassword() + ", accountNonExpired="
                + this.getAccountNonExpired() + ", accountNonLocked=" + this.getAccountNonLocked()
                + ", credentialsNonExpired=" + this.getCredentialsNonExpired() + ", userOwnedPath="
                + this.getUserOwnedPath() + ")";
    }
}
