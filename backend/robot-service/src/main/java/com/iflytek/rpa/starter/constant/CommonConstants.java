package com.iflytek.rpa.starter.constant;

import java.util.Arrays;
import java.util.List;

public class CommonConstants {
    public static final String GLOBAL_TOKEN = "global-token";
    public static final String AUTH_TOKEN = "auth-token";
    public static final String USER_INFO = "user-info";
    public static final String IP_ADDRESS = "ip-address";

    public static final String CONTENT_TYPE = "application/json; charset=UTF-8";

    /**
     * 是否删除 1是 0否
     */
    public static final int DELETED = 1;

    public static final int NOT_DELETED = 0;

    public static final int CODE_YES = 1;
    public static final int CODE_NO = 0;

    public static final List<Integer> CHECK_IS_OR_NO = Arrays.asList(CODE_YES, CODE_NO);

    /**
     * 超管角色编号
     */
    public static final String SUPER_ROLE_CODE = "999999";
}
