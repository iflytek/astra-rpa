package com.iflytek.rpa.auth.service;

import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import org.casbin.casdoor.config.Config;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.springframework.stereotype.Service;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/20 19:04
 */
@Service
public class AuthExtendService extends AuthService {
    public AuthExtendService(Config config) {
        super(config);
    }

    public String getCustomSigninUrl(String redirectUrl) {
        return this.getCustomSigninUrl(redirectUrl, config.applicationName);
    }

    public String getCustomSigninUrl(String redirectUrl, String state) {
        String scope = "read";
        try {
            return String.format(
                    "/login/oauth/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=%s&state=%s",
                    config.clientId, URLEncoder.encode(redirectUrl, StandardCharsets.UTF_8.toString()), scope, state);
        } catch (UnsupportedEncodingException e) {
            throw new AuthException(e);
        }
    }
}
