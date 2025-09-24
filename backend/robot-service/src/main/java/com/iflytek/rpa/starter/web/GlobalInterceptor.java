// package com.iflytek.rpa.starter.web;
//
// import com.iflytek.rpa.starter.constant.CommonConstants;
// import com.iflytek.rpa.starter.utils.HttpUtils;
// import com.iflytek.rpa.starter.utils.StringUtils;
// import org.springframework.web.servlet.HandlerInterceptor;
//
// import javax.servlet.http.HttpServletRequest;
// import javax.servlet.http.HttpServletResponse;
// import java.io.PrintWriter;
//
/// **
// * 访问是否由 gateway 发起
// * @author keler
// * @date 2020/5/6
// */
// public class GlobalInterceptor implements HandlerInterceptor {
//    @Override
//    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object obj) throws Exception {
//        String tgToken = HttpUtils.getGlobalToken();
//
//        if(StringUtils.isEmpty(tgToken) || !tgToken.equals(StringUtils.getGlobalToken())) {
//            response.setContentType(CommonConstants.CONTENT_TYPE);
//            PrintWriter writer = response.getWriter();
//            writer.write("Dead End ！");
//            return false;
//        }
//
//        return true;
//    }
// }
