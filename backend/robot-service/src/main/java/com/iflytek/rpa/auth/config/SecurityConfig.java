package com.iflytek.rpa.auth.config;

import com.iflytek.rpa.auth.constants.enums.AuthEnum;
import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.auth.filter.JwtTokenFilter;
import com.iflytek.rpa.auth.utils.ResponseUtils;
import com.iflytek.rpa.starter.redis.RedisUtils;
import java.util.Arrays;
import java.util.Collections;
import java.util.Objects;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.casbin.casdoor.entity.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.logout.LogoutHandler;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/**
 * @desc: 安全相关配置
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/15 15:23
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    private static final Logger logger = LoggerFactory.getLogger(SecurityConfig.class);

    private final JwtTokenFilter jwtTokenFilter;
    private final String frontendUrl;
    private final String casdoorUrl;

    public SecurityConfig(
            JwtTokenFilter jwtTokenFilter,
            @Value("${casdoor.redirect-url}") String redirectUrl,
            @Value("${casdoor.endpoint}") String casdoorUrl) {
        this.jwtTokenFilter = jwtTokenFilter;
        this.frontendUrl = parseOrigin(redirectUrl);
        this.casdoorUrl = parseOrigin(casdoorUrl);
    }

    private String parseOrigin(String url) {
        int protocol = url.startsWith("https://") ? 5 : 4;
        int slash = url.indexOf('/', protocol + 3);
        return slash == -1 ? url : url.substring(0, slash);
    }

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        // enable CORS and disable CSRF
        http = http.cors(corsConfig -> corsConfig.configurationSource(configurationSource()))
                .csrf()
                .disable();

        // set session management to stateless
        http = http.sessionManagement()
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and();

        // set permissions on endpoints
        http.authorizeRequests(authorize -> authorize
                // Our public endpoints
                .mvcMatchers("/api/redirect-url", "/api/signin")
                .permitAll()
                // Our private endpoints
                .mvcMatchers("/api/**")
                .authenticated());

        // set unauthorized requests exception handler
        http = http.exceptionHandling()
                .authenticationEntryPoint((request, response, ex) -> ResponseUtils.fail(response, "unauthorized"))
                .and();

        // set logout handler
        http.logout(logoutConfig -> logoutConfig
                .logoutUrl("/api/logout")
                .addLogoutHandler(new LogoutHandler() {
                    @Override
                    public void logout(
                            HttpServletRequest request, HttpServletResponse response, Authentication authentication) {
                        logger.info("Logout handler called - Authentication: {}", authentication);

                        // 拿到用户信息
                        User user = null;
                        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
                            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
                            user = userDetails.getUser();
                        }

                        // redis删token，key为CASDOOR_CURRENT_USER_TOKEN
                        if (Objects.nonNull(user)) {
                            String redisKey = AuthEnum.CASDOOR_CURRENT_USER_TOKEN.getCode() + "_" + user.name;
                            RedisUtils.redisTemplate.delete(redisKey);
                        }

                        // 清除Spring Security上下文
                        SecurityContextHolder.clearContext();

                        // 记录登出日志
                        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
                            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
                            logger.info("User {} logged out successfully", userDetails.getUsername());
                        }
                    }
                })
                .logoutSuccessHandler((request, response, authentication) -> {
                    // 登出成功后的处理
                    response.setStatus(HttpServletResponse.SC_OK);
                    response.setContentType("application/json;charset=UTF-8");
                    response.getWriter().write("{\"code\":200,\"message\":\"登出成功\",\"data\":null}");
                }));

        // add JWT token filter - 放在LogoutFilter之前
        http.addFilterBefore(jwtTokenFilter, org.springframework.security.web.authentication.logout.LogoutFilter.class);
    }

    @Bean
    CorsConfigurationSource configurationSource() {
        CorsConfiguration corsConfiguration = new CorsConfiguration();
        corsConfiguration.setAllowCredentials(true);
        corsConfiguration.setAllowedHeaders(Arrays.asList(
                HttpHeaders.AUTHORIZATION,
                HttpHeaders.CONTENT_TYPE,
                HttpHeaders.ACCEPT,
                HttpHeaders.ORIGIN,
                "X-Requested-With",
                "Cache-Control"));
        corsConfiguration.setAllowedMethods(Collections.singletonList("*"));
        corsConfiguration.setAllowedOrigins(Collections.singletonList("*"));
        corsConfiguration.setMaxAge(3600L);
        corsConfiguration.setExposedHeaders(Collections.singletonList("*"));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfiguration);

        return source;
    }
}
