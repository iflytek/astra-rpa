//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package com.iflytek.rpa.starter.conf;

import com.alibaba.fastjson.JSON;
import java.util.*;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.AfterThrowing;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.multipart.MultipartFile;

@Aspect
public class RequestLogAspect {
    private static final Logger LOGGER = LoggerFactory.getLogger(RequestLogAspect.class);

    public RequestLogAspect() {}

    public static <T> List<T> castList(Object obj, Class<T> clazz) {
        List<T> result = new ArrayList();
        if (!(obj instanceof List)) {
            return null;
        } else {
            Iterator var3 = ((List) obj).iterator();

            while (var3.hasNext()) {
                Object o = var3.next();
                result.add(clazz.cast(o));
            }

            return result;
        }
    }

    @Pointcut("execution(* com.iflytek.rpa.monitor..controller..*(..))")
    public void requestServer() {}

    @Around("requestServer() && !@annotation(SkipAop)")
    public Object doAround(ProceedingJoinPoint proceedingJoinPoint) throws Throwable {
        long start = System.currentTimeMillis();
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();
        Object result = proceedingJoinPoint.proceed();
        RequestInfo requestInfo = new RequestInfo();
        requestInfo.setIp(request.getRemoteAddr());
        requestInfo.setUrl(request.getRequestURL().toString());
        requestInfo.setHttpMethod(request.getMethod());
        requestInfo.setClassMethod(String.format(
                "%s.%s",
                proceedingJoinPoint.getSignature().getDeclaringTypeName(),
                proceedingJoinPoint.getSignature().getName()));
        requestInfo.setRequestParams(this.getRequestParamsByProceedingJoinPoint(proceedingJoinPoint));
        requestInfo.setTimeCost(System.currentTimeMillis() - start);
        LOGGER.info("Request Info      : {}", JSON.toJSONString(requestInfo));
        return result;
    }

    @AfterThrowing(pointcut = "requestServer() && !@annotation(SkipAop)", throwing = "e")
    public void doAfterThrow(JoinPoint joinPoint, RuntimeException e) {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        HttpServletRequest request = attributes.getRequest();
        RequestErrorInfo requestErrorInfo = new RequestErrorInfo();
        requestErrorInfo.setIp(request.getRemoteAddr());
        requestErrorInfo.setUrl(request.getRequestURL().toString());
        requestErrorInfo.setHttpMethod(request.getMethod());
        requestErrorInfo.setClassMethod(String.format(
                "%s.%s",
                joinPoint.getSignature().getDeclaringTypeName(),
                joinPoint.getSignature().getName()));
        requestErrorInfo.setRequestParams(this.getRequestParamsByJoinPoint(joinPoint));
        requestErrorInfo.setException(e);
        LOGGER.info("Error Request Info      : {}", JSON.toJSONString(requestErrorInfo));
    }

    private Map<String, Object> getRequestParamsByProceedingJoinPoint(ProceedingJoinPoint proceedingJoinPoint) {
        String[] paramNames = ((MethodSignature) proceedingJoinPoint.getSignature()).getParameterNames();
        Object[] paramValues = proceedingJoinPoint.getArgs();
        return this.buildRequestParam(paramNames, paramValues);
    }

    private Map<String, Object> getRequestParamsByJoinPoint(JoinPoint joinPoint) {
        String[] paramNames = ((MethodSignature) joinPoint.getSignature()).getParameterNames();
        Object[] paramValues = joinPoint.getArgs();
        return this.buildRequestParam(paramNames, paramValues);
    }

    private Map<String, Object> buildRequestParam(String[] paramNames, Object[] paramValues) {
        Map<String, Object> requestParams = new HashMap();

        for (int i = 0; i < paramNames.length; ++i) {
            Object value = paramValues[i];
            if (value instanceof MultipartFile) {
                MultipartFile file = (MultipartFile) value;
                value = file.getOriginalFilename();
            }

            if (value instanceof MultipartFile[]) {
                MultipartFile[] files = (MultipartFile[]) value;
                value = Arrays.stream(files)
                        .map(MultipartFile::getOriginalFilename)
                        .collect(Collectors.joining(","));
            }

            if (value instanceof List) {
                try {
                    List<MultipartFile> multipartFiles = castList(value, MultipartFile.class);
                    if (multipartFiles != null) {
                        List<String> fileNames = new ArrayList();
                        Iterator var8 = multipartFiles.iterator();

                        while (var8.hasNext()) {
                            MultipartFile file = (MultipartFile) var8.next();
                            fileNames.add(file.getOriginalFilename());
                        }

                        requestParams.put(paramNames[i], fileNames);
                        break;
                    }
                } catch (ClassCastException var10) {
                }
            }

            requestParams.put(paramNames[i], value);
        }

        return requestParams;
    }

    public class RequestErrorInfo {
        private String ip;
        private String url;
        private String httpMethod;
        private String classMethod;
        private Object requestParams;
        private RuntimeException exception;

        public RequestErrorInfo() {}

        public String getIp() {
            return this.ip;
        }

        public void setIp(final String ip) {
            this.ip = ip;
        }

        public String getUrl() {
            return this.url;
        }

        public void setUrl(final String url) {
            this.url = url;
        }

        public String getHttpMethod() {
            return this.httpMethod;
        }

        public void setHttpMethod(final String httpMethod) {
            this.httpMethod = httpMethod;
        }

        public String getClassMethod() {
            return this.classMethod;
        }

        public void setClassMethod(final String classMethod) {
            this.classMethod = classMethod;
        }

        public Object getRequestParams() {
            return this.requestParams;
        }

        public void setRequestParams(final Object requestParams) {
            this.requestParams = requestParams;
        }

        public RuntimeException getException() {
            return this.exception;
        }

        public void setException(final RuntimeException exception) {
            this.exception = exception;
        }

        public boolean equals(final Object o) {
            if (o == this) {
                return true;
            } else if (!(o instanceof RequestErrorInfo)) {
                return false;
            } else {
                RequestErrorInfo other = (RequestErrorInfo) o;
                if (!other.canEqual(this)) {
                    return false;
                } else {
                    Object this$ip = this.getIp();
                    Object other$ip = other.getIp();
                    if (this$ip == null) {
                        if (other$ip != null) {
                            return false;
                        }
                    } else if (!this$ip.equals(other$ip)) {
                        return false;
                    }

                    Object this$url = this.getUrl();
                    Object other$url = other.getUrl();
                    if (this$url == null) {
                        if (other$url != null) {
                            return false;
                        }
                    } else if (!this$url.equals(other$url)) {
                        return false;
                    }

                    Object this$httpMethod = this.getHttpMethod();
                    Object other$httpMethod = other.getHttpMethod();
                    if (this$httpMethod == null) {
                        if (other$httpMethod != null) {
                            return false;
                        }
                    } else if (!this$httpMethod.equals(other$httpMethod)) {
                        return false;
                    }

                    label62:
                    {
                        Object this$classMethod = this.getClassMethod();
                        Object other$classMethod = other.getClassMethod();
                        if (this$classMethod == null) {
                            if (other$classMethod == null) {
                                break label62;
                            }
                        } else if (this$classMethod.equals(other$classMethod)) {
                            break label62;
                        }

                        return false;
                    }

                    label55:
                    {
                        Object this$requestParams = this.getRequestParams();
                        Object other$requestParams = other.getRequestParams();
                        if (this$requestParams == null) {
                            if (other$requestParams == null) {
                                break label55;
                            }
                        } else if (this$requestParams.equals(other$requestParams)) {
                            break label55;
                        }

                        return false;
                    }

                    Object this$exception = this.getException();
                    Object other$exception = other.getException();
                    if (this$exception == null) {
                        return other$exception == null;
                    } else return this$exception.equals(other$exception);
                }
            }
        }

        protected boolean canEqual(final Object other) {
            return other instanceof RequestErrorInfo;
        }

        public int hashCode() {
            boolean PRIME = true;
            int result = 1;
            Object $ip = this.getIp();
            result = result * 59 + ($ip == null ? 43 : $ip.hashCode());
            Object $url = this.getUrl();
            result = result * 59 + ($url == null ? 43 : $url.hashCode());
            Object $httpMethod = this.getHttpMethod();
            result = result * 59 + ($httpMethod == null ? 43 : $httpMethod.hashCode());
            Object $classMethod = this.getClassMethod();
            result = result * 59 + ($classMethod == null ? 43 : $classMethod.hashCode());
            Object $requestParams = this.getRequestParams();
            result = result * 59 + ($requestParams == null ? 43 : $requestParams.hashCode());
            Object $exception = this.getException();
            result = result * 59 + ($exception == null ? 43 : $exception.hashCode());
            return result;
        }

        public String toString() {
            return "RequestLogAspect.RequestErrorInfo(ip=" + this.getIp() + ", url=" + this.getUrl() + ", httpMethod="
                    + this.getHttpMethod() + ", classMethod=" + this.getClassMethod() + ", requestParams="
                    + this.getRequestParams() + ", exception=" + this.getException() + ")";
        }
    }

    public class RequestInfo {
        private String ip;
        private String url;
        private String httpMethod;
        private String classMethod;
        private Object requestParams;
        private Object result;
        private Long timeCost;

        public RequestInfo() {}

        public String getIp() {
            return this.ip;
        }

        public void setIp(final String ip) {
            this.ip = ip;
        }

        public String getUrl() {
            return this.url;
        }

        public void setUrl(final String url) {
            this.url = url;
        }

        public String getHttpMethod() {
            return this.httpMethod;
        }

        public void setHttpMethod(final String httpMethod) {
            this.httpMethod = httpMethod;
        }

        public String getClassMethod() {
            return this.classMethod;
        }

        public void setClassMethod(final String classMethod) {
            this.classMethod = classMethod;
        }

        public Object getRequestParams() {
            return this.requestParams;
        }

        public void setRequestParams(final Object requestParams) {
            this.requestParams = requestParams;
        }

        public Object getResult() {
            return this.result;
        }

        public void setResult(final Object result) {
            this.result = result;
        }

        public Long getTimeCost() {
            return this.timeCost;
        }

        public void setTimeCost(final Long timeCost) {
            this.timeCost = timeCost;
        }

        public boolean equals(final Object o) {
            if (o == this) {
                return true;
            } else if (!(o instanceof RequestInfo)) {
                return false;
            } else {
                RequestInfo other = (RequestInfo) o;
                if (!other.canEqual(this)) {
                    return false;
                } else {
                    label95:
                    {
                        Object this$timeCost = this.getTimeCost();
                        Object other$timeCost = other.getTimeCost();
                        if (this$timeCost == null) {
                            if (other$timeCost == null) {
                                break label95;
                            }
                        } else if (this$timeCost.equals(other$timeCost)) {
                            break label95;
                        }

                        return false;
                    }

                    Object this$ip = this.getIp();
                    Object other$ip = other.getIp();
                    if (this$ip == null) {
                        if (other$ip != null) {
                            return false;
                        }
                    } else if (!this$ip.equals(other$ip)) {
                        return false;
                    }

                    Object this$url = this.getUrl();
                    Object other$url = other.getUrl();
                    if (this$url == null) {
                        if (other$url != null) {
                            return false;
                        }
                    } else if (!this$url.equals(other$url)) {
                        return false;
                    }

                    label74:
                    {
                        Object this$httpMethod = this.getHttpMethod();
                        Object other$httpMethod = other.getHttpMethod();
                        if (this$httpMethod == null) {
                            if (other$httpMethod == null) {
                                break label74;
                            }
                        } else if (this$httpMethod.equals(other$httpMethod)) {
                            break label74;
                        }

                        return false;
                    }

                    label67:
                    {
                        Object this$classMethod = this.getClassMethod();
                        Object other$classMethod = other.getClassMethod();
                        if (this$classMethod == null) {
                            if (other$classMethod == null) {
                                break label67;
                            }
                        } else if (this$classMethod.equals(other$classMethod)) {
                            break label67;
                        }

                        return false;
                    }

                    Object this$requestParams = this.getRequestParams();
                    Object other$requestParams = other.getRequestParams();
                    if (this$requestParams == null) {
                        if (other$requestParams != null) {
                            return false;
                        }
                    } else if (!this$requestParams.equals(other$requestParams)) {
                        return false;
                    }

                    Object this$result = this.getResult();
                    Object other$result = other.getResult();
                    if (this$result == null) {
                        return other$result == null;
                    } else return this$result.equals(other$result);
                }
            }
        }

        protected boolean canEqual(final Object other) {
            return other instanceof RequestInfo;
        }

        public int hashCode() {
            boolean PRIME = true;
            int result = 1;
            Object $timeCost = this.getTimeCost();
            result = result * 59 + ($timeCost == null ? 43 : $timeCost.hashCode());
            Object $ip = this.getIp();
            result = result * 59 + ($ip == null ? 43 : $ip.hashCode());
            Object $url = this.getUrl();
            result = result * 59 + ($url == null ? 43 : $url.hashCode());
            Object $httpMethod = this.getHttpMethod();
            result = result * 59 + ($httpMethod == null ? 43 : $httpMethod.hashCode());
            Object $classMethod = this.getClassMethod();
            result = result * 59 + ($classMethod == null ? 43 : $classMethod.hashCode());
            Object $requestParams = this.getRequestParams();
            result = result * 59 + ($requestParams == null ? 43 : $requestParams.hashCode());
            Object $result = this.getResult();
            result = result * 59 + ($result == null ? 43 : $result.hashCode());
            return result;
        }

        public String toString() {
            return "RequestLogAspect.RequestInfo(ip=" + this.getIp() + ", url=" + this.getUrl() + ", httpMethod="
                    + this.getHttpMethod() + ", classMethod=" + this.getClassMethod() + ", requestParams="
                    + this.getRequestParams() + ", result=" + this.getResult() + ", timeCost=" + this.getTimeCost()
                    + ")";
        }
    }
}
