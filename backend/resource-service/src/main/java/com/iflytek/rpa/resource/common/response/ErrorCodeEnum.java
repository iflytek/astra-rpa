package com.iflytek.rpa.resource.common.response;

public enum ErrorCodeEnum {
    ANT_SUCCESS("200", "OK"),
    S_SUCCESS("000000", "操作成功"),
    OPEN_AUTH_UAC_SMS_VERIFY_CODE_ERROR("005001001", "验证码错误"),
    OPEN_AUTH_UAC_USER_IS_EMPTY("005001002", "用户数据为空"),
    OPEN_AUTH_XFYUN_OPEN_PLATFORM_DATA_IS_EMPTY("005002001", "讯飞开放平台数据为空"),
    OPEN_AUTH_XFYUN_OPEN_PLATFORM_BINDING_DATA_IS_EMPTY("005002002", "讯飞开放平台绑定数据为空"),
    OPEN_AUTH_XFYUN_OPEN_PLATFORM_ALREADY_IS_BINDING("005002003", "您已绑定讯飞开放平台"),
    E_PARAM("500000", "参数异常"),
    E_PARAM_LOSE("500001", "参数缺失"),
    E_PARAM_PARSE("500002", "参数解析失败"),
    E_PARAM_CHECK("500003", "参数校验失败"),
    E_SERVICE("600000", "业务异常"),
    E_SERVICE_NOT_SUPPORT("600001", "业务不支持"),
    E_SERVICE_INFO_LOSE("600002", "业务信息缺失"),
    E_SERVICE_POWER_LIMIT("600003", "业务权限限制"),
    E_SQL("700000", "数据异常"),
    E_SQL_EMPTY("700001", "数据为空"),
    E_SQL_REPEAT("700002", "数据重复"),
    E_SQL_EXCEPTION("700003", "数据操作异常"),
    E_REDIS("710000", "Redis数据异常"),
    E_REDIS_EMPTY("700001", "Redis数据为空"),
    E_REDIS_REPEAT("700002", "Redis数据重复"),
    E_REDIS_EXCEPTION("700003", "Redis数据操作异常"),
    E_MONGO("710000", "数据异常"),
    E_MONGO_EMPTY("710001", "数据为空"),
    E_MONGO_REPEAT("710002", "数据重复"),
    E_MONGO_EXCEPTION("710003", "数据操作异常"),
    E_API("800000", "第三方接口异常"),
    E_API_FAIL("800001", "第三方接口请求失败"),
    E_API_EXCEPTION("800002", "第三方接口请求异常"),
    E_COMMON("999999", "请求异常,请重试"),
    E_NOT_LOGIN("900001", "未登录"),
    E_NO_POWER("900002", "无权限"),
    E_NO_ACCOUNT("900003", "账号不存在"),
    E_EXCEPTION("900004", "未知异常");

    private String code;
    private String flag;

    private ErrorCodeEnum(String code, String flag) {
        this.code = code;
        this.flag = flag;
    }

    public String getCode() {
        return this.code;
    }

    public String getFlag() {
        return this.flag;
    }
}
