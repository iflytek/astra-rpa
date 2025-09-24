package com.iflytek.rpa.auth.controller;

import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.auth.entity.Result;
import com.iflytek.rpa.auth.service.AuthExtendService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.utils.UserUtils;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

/**
 * @desc: 认证用户控制器
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/11 15:10
 */
@RestController
@RequestMapping("/user")
public class UserController {
    private static final Logger logger = LoggerFactory.getLogger(UserController.class);

    private final AuthService authService;
    private final AuthExtendService authExtendService;
    private final String redirectUrl;

    public UserController(
            AuthService authService,
            AuthExtendService authExtendService,
            @Value("${casdoor.redirect-url}") String redirectUrl) {
        this.authService = authService;
        this.authExtendService = authExtendService;
        this.redirectUrl = redirectUrl;
    }

    @GetMapping("/api/redirect-url")
    public Result getRedirectUrl() {
        try {
            String signinUrl = authExtendService.getCustomSigninUrl(redirectUrl);
            return Result.success(signinUrl);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            return Result.failure(exception.getMessage());
        }
    }

    @PostMapping("/api/signin")
    public Result signin(@RequestParam("code") String code, @RequestParam("state") String state) {
        try {
            String token = authService.getOAuthToken(code, state);
            return Result.success(token);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            return Result.failure(exception.getMessage());
        }
    }

    @GetMapping("/api/userinfo")
    public Result userinfo(Authentication authentication) {
        CustomUserDetails customUserDetails = (CustomUserDetails) authentication.getPrincipal();
        User user = customUserDetails.getUser();
        return Result.success(user);
    }

    @GetMapping("/api/now/userinfo")
    public Result nowUserinfo() throws NoLoginException {
        try {
            User casdoorUser = UserUtils.nowLoginUser();
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("登录出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }

    @GetMapping("/api/userinfobyid")
    public Result userinfo(@RequestParam("id") String id) {
        try {
            User casdoorUser = UserUtils.getUserInfoById(id);
            return Result.success(casdoorUser);
        } catch (Exception e) {
            logger.error("查找出错 exception", e);
            return Result.failure(e.getMessage());
        }
    }
}
