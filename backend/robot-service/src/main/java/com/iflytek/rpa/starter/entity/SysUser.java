package com.iflytek.rpa.starter.entity;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class SysUser implements Serializable {
    private Long id;
    private String name;
    private String username;
    private String password;
    private String phone;
    private String telephone;
    private String email;
    private Boolean enabled;
    private Boolean accountNonExpired;
    private Boolean accountNonLocked;
    private Boolean credentialsNonExpired;
    private List<String> userOwnedPath = new ArrayList();

    public SysUser() {}

    public String toString() {
        return "User{id=" + this.id + ", username='" + this.name + '\'' + ", password='" + this.password + '\''
                + ", enabled=" + this.enabled + ", accountNonExpired=" + this.accountNonExpired + ", accountNonLocked="
                + this.accountNonLocked + ", credentialsNonExpired=" + this.credentialsNonExpired + ", roles="
                + this.userOwnedPath + '}';
    }

    public Long getId() {
        return this.id;
    }

    public void setId(final Long id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(final String name) {
        this.name = name;
    }

    public String getUsername() {
        return this.username;
    }

    public void setUsername(final String username) {
        this.username = username;
    }

    public String getPassword() {
        return this.password;
    }

    public void setPassword(final String password) {
        this.password = password;
    }

    public String getPhone() {
        return this.phone;
    }

    public void setPhone(final String phone) {
        this.phone = phone;
    }

    public String getTelephone() {
        return this.telephone;
    }

    public void setTelephone(final String telephone) {
        this.telephone = telephone;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(final String email) {
        this.email = email;
    }

    public Boolean getEnabled() {
        return this.enabled;
    }

    public void setEnabled(final Boolean enabled) {
        this.enabled = enabled;
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
}
