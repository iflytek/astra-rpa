package com.iflytek.rpa.starter.utils;

import com.alibaba.fastjson.JSONObject;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.io.PrintWriter;
import java.util.Objects;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

public class HttpUtils {
    private static final Logger LOGGER = LoggerFactory.getLogger(HttpUtils.class);

    public HttpUtils() {}

    public static String getAuthToken() {
        return getHeader("auth-token");
    }

    public static String getHeader(String key) {
        return getRequest().getHeader(key);
    }

    public static String getGlobalToken() {
        return getHeader("global-token");
    }

    public static String getIp() {
        return getHeader("ip-address");
    }

    public static HttpServletRequest getRequest() {
        return ((ServletRequestAttributes) Objects.requireNonNull(RequestContextHolder.getRequestAttributes()))
                .getRequest();
    }

    public static HttpSession getSession() {
        return getRequest().getSession();
    }

    public static void print(AppResponse<String> response, ServletResponse servletResponse) {
        print(JSONObject.toJSONString(response), servletResponse);
    }

    public static void print(String response, ServletResponse servletResponse) {
        PrintWriter out = null;

        try {
            servletResponse.setCharacterEncoding("UTF-8");
            servletResponse.setContentType("application/json");
            out = servletResponse.getWriter();
            out.println(response);
        } catch (Exception var7) {
            LOGGER.error("输出JSON报错", var7);
        } finally {
            if (null != out) {
                out.flush();
                out.close();
            }
        }
    }
}
