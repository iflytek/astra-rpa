package com.iflytek.rpa.starter.utils.response;

import java.io.Serializable;
import org.springframework.util.StringUtils;

public class AppResponse<T> implements Serializable {
    private String code;
    private T data;
    private String message;

    private AppResponse() {}

    public static <T> AppResponse<T> error(ErrorCodeEnum codeEnum) {
        return error(codeEnum, null);
    }

    public static <T> AppResponse<T> error(ErrorCodeEnum codeEnum, String message) {
        if (StringUtils.isEmpty(message)) {
            message = codeEnum.getFlag();
        }

        AppResponse<T> response = new AppResponse();
        response.setCode(codeEnum.getCode());
        response.setData(null);
        response.setMessage(message);
        return response;
    }

    public static AppResponse<String> error(String code, String message) {
        AppResponse<String> response = new AppResponse();
        response.setCode(code);
        response.setData("");
        response.setMessage(message);
        return response;
    }

    public static AppResponse<String> error(String message) {
        return error(ErrorCodeEnum.E_COMMON.getCode(), message);
    }

    public static <T> AppResponse<T> success(T data) {
        AppResponse<T> response = new AppResponse();
        response.setCode(ErrorCodeEnum.S_SUCCESS.getCode());
        response.setData(data);
        response.setMessage("");
        return response;
    }

    public boolean ok() {
        return this.code.equals(ErrorCodeEnum.S_SUCCESS.getCode());
    }

    public String getCode() {
        return this.code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public T getData() {
        return this.data;
    }

    public void setData(T data) {
        this.data = data;
    }

    public String getMessage() {
        return this.message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
