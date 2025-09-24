// package com.iflytek.rpa.starter.web;
//
// import org.springframework.beans.factory.annotation.Autowired;
// import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
// import org.springframework.boot.context.properties.EnableConfigurationProperties;
// import org.springframework.context.annotation.Configuration;
// import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
// import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
//
/// **
// * @angelor keler
// * @date 2020/5/6
// */
// @Configuration
// @EnableConfigurationProperties(GlobalInterceptorProperties.class)
// @ConditionalOnProperty(
//        name = "web.global.interceptor.open",
//        havingValue = "true"
// )
// public class WebMvcAutoConfiguration implements WebMvcConfigurer {
//
//    @Autowired
//    GlobalInterceptorProperties interceptorProperties;
//
//    @Override
//    public void addInterceptors(InterceptorRegistry registry) {
//        registry.addInterceptor(new GlobalInterceptor())
//                .addPathPatterns(interceptorProperties.getAddPathPatterns())
//                .excludePathPatterns(interceptorProperties.getExcludePathPatterns());
//    }
// }
