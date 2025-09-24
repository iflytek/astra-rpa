package com.iflytek.rpa.starter.utils;

import java.net.InetAddress;
import java.util.Objects;
import javax.servlet.http.HttpServletRequest;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.server.reactive.ServerHttpRequest;

public class IpUtil {
    public static final Logger LOGGER = LoggerFactory.getLogger(IpUtil.class);
    static final String[] PROXYS =
            new String[] {"X-Real-IP", "X-Forwarded-For", "Proxy-Client-IP", "WL-Proxy-Client-IP", "HTTP_CLIENT_IP"};
    static final String LOCALHOST_IP_V4 = "127.0.0.1";
    static final String LOCALHOST_IP_V6 = "0:0:0:0:0:0:0:1";

    public IpUtil() {}

    public static String getIpAddr(ServerHttpRequest request) {
        HttpHeaders headers = request.getHeaders();
        String ipAddress = null;
        String[] var3 = PROXYS;
        int var4 = var3.length;

        for (int var5 = 0; var5 < var4; ++var5) {
            String proxy = var3[var5];
            ipAddress = headers.getFirst(proxy);
            if (!StringUtils.isEmpty(ipAddress) && !"unknown".equalsIgnoreCase(ipAddress)) {
                break;
            }
        }

        if (StringUtils.isEmpty(ipAddress) || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = Objects.requireNonNull(request.getRemoteAddress())
                    .getAddress()
                    .getHostAddress();
        }

        String ipSeparator = ",";
        if (!StringUtils.isEmpty(ipAddress) && ipAddress.indexOf(ipSeparator) > 0) {
            ipAddress = ipAddress.substring(0, ipAddress.indexOf(ipSeparator));
        }

        return ipAddress;
    }

    public static String getIpAddr(HttpServletRequest request) {
        String ipAddress = null;
        String[] inet = PROXYS;
        int var3 = inet.length;

        for (int var4 = 0; var4 < var3; ++var4) {
            String proxy = inet[var4];
            ipAddress = request.getHeader(proxy);
            if (!StringUtils.isEmpty(ipAddress) && !"unknown".equalsIgnoreCase(ipAddress)) {
                break;
            }
        }

        if (StringUtils.isEmpty(ipAddress) || "unknown".equalsIgnoreCase(ipAddress)) {
            ipAddress = request.getRemoteAddr();
            if ("127.0.0.1".equals(ipAddress) || "0:0:0:0:0:0:0:1".equals(ipAddress)) {
                inet = null;

                try {
                    InetAddress inet1 = InetAddress.getLocalHost();
                    ipAddress = inet1.getHostAddress();
                } catch (Exception var6) {
                }
            }
        }

        String ipSeparator = ",";
        if (!StringUtils.isEmpty(ipAddress) && ipAddress.indexOf(ipSeparator) > 0) {
            ipAddress = ipAddress.substring(0, ipAddress.indexOf(ipSeparator));
        }

        return ipAddress;
    }
}
