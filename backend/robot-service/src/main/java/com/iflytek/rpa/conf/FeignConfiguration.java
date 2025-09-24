package com.iflytek.rpa.conf;

import static com.iflytek.rpa.conf.ApiContext.*;

import feign.RequestInterceptor;
import feign.RequestTemplate;
import javax.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

@Configuration
public class FeignConfiguration implements RequestInterceptor {

    private final Logger logger = LoggerFactory.getLogger(getClass());

    @Override
    public void apply(RequestTemplate template) {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attributes != null) {
            HttpServletRequest request = attributes.getRequest();
            template.header(CURRENT_USER_ID_KEY, request.getHeader(CURRENT_USER_ID_KEY));
            template.header(CURRENT_TENANT_ID_KEY, request.getHeader(CURRENT_TENANT_ID_KEY));
            template.header(CURRENT_TERMINAL_MAC_KEY, request.getHeader(CURRENT_TERMINAL_MAC_KEY));
            template.header(CURRENT_TERMINAL_NAME_KEY, request.getHeader(CURRENT_TERMINAL_NAME_KEY));
        }
    }
}
