package com.iflytek.rpa.auth.filter;

import com.iflytek.rpa.auth.constants.enums.AuthEnum;
import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.starter.redis.RedisUtils;
import java.io.IOException;
import java.util.Objects;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.exception.AuthException;
import org.casbin.casdoor.service.AuthService;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.AuthorityUtils;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/16 17:16
 */
@Component
public class JwtTokenFilter extends OncePerRequestFilter {

    private final AuthService authService;

    public JwtTokenFilter(AuthService casdoorAuthService) {
        this.authService = casdoorAuthService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        // get authorization header and validate
        final String header = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (!StringUtils.hasText(header) || !header.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        // get jwt token and validate
        final String token = header.split(" ")[1].trim();

        // get user identity and set it on the spring security context
        UserDetails userDetails = null;
        User user = null;
        try {
            user = authService.parseJwtToken(token);
            userDetails = new CustomUserDetails(user);
        } catch (AuthException exception) {
            logger.error("casdoor auth exception", exception);
            chain.doFilter(request, response);
            return;
        }

        UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                userDetails, null, AuthorityUtils.createAuthorityList("ROLE_casdoor"));

        authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
        // 将token存到redis中，key为CASDOOR_CURRENT_USER_TOKEN，value为token
        if (Objects.nonNull(user)) {
            String redisKey = AuthEnum.CASDOOR_CURRENT_USER_TOKEN.getCode() + "_" + user.name;
            RedisUtils.redisTemplate.opsForValue().set(redisKey, token);
        }

        SecurityContextHolder.getContext().setAuthentication(authentication);
        chain.doFilter(request, response);
    }
}
