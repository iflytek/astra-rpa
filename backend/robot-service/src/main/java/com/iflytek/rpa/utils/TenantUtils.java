package com.iflytek.rpa.utils;

import com.iflytek.rpa.auth.entity.CustomUserDetails;
import java.util.Objects;
import lombok.extern.slf4j.Slf4j;
import org.casbin.casdoor.entity.User;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

/**
 * @desc: 租户工具类
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/11 14:10
 */
@Component
@Slf4j
public class TenantUtils {
    /**
     * 获取当前登录租户ID
     *
     * @return 租户ID
     */
    public static String getTenantId() {
        // 从Spring Security上下文获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
            User user = userDetails.getUser();
            if (Objects.nonNull(user)) {
                return user.owner;
            }
            return null;
        }
        return null;
    }
}
