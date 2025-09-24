package com.iflytek.rpa.starter.entity;

public class Role {
    private Integer id;
    private String name;
    private String nameZh;

    public Role() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(final Integer id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(final String name) {
        this.name = name;
    }

    public String getNameZh() {
        return this.nameZh;
    }

    public void setNameZh(final String nameZh) {
        this.nameZh = nameZh;
    }
}
