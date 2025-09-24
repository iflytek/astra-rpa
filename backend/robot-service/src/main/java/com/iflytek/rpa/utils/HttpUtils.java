package com.iflytek.rpa.utils;

import com.alibaba.fastjson.JSONObject;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.task.entity.enums.SourceTypeEnum;
import com.iflytek.rpa.task.entity.enums.TerminalTypeEnum;
import java.io.PrintWriter;
import java.util.Objects;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpSession;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * @Author: wyzhou3
 * @Date: 2021/12/31 15:03
 * @Description:
 */
public class HttpUtils extends com.iflytek.rpa.starter.utils.HttpUtils {
    private static final Logger LOGGER = LoggerFactory.getLogger(com.iflytek.rpa.starter.utils.HttpUtils.class);

    public HttpUtils() {}

    public static String getSsoSessionId() {
        return getHeader("ssoSessionId");
    }

    public static String getAccountId() {
        return getHeader("account_id");
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

    public static String getTenantId() {
        return TenantUtils.getTenantId();
    }

    public static String getTerminalType() {
        String terminalType = HttpUtils.getHeader("terminalType");
        return org.apache.commons.lang3.StringUtils.isEmpty(terminalType)
                ? TerminalTypeEnum.PRIVATE.getCode()
                : terminalType;
    }

    public static String getAppId() {
        return HttpUtils.getHeader("appId");
    }

    public static String getSourceType() {
        String userAgent = HttpUtils.getHeader("user-agent");
        if (!StringUtils.isEmpty(userAgent) && userAgent.contains("iFlyRPAStudio")) {
            return SourceTypeEnum.CLIENT.getCode();
        }
        return SourceTypeEnum.WEB.getCode();
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
