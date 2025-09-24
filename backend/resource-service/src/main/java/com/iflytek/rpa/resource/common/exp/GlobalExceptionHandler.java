package com.iflytek.rpa.resource.common.exp;

import com.iflytek.rpa.resource.common.response.AppResponse;
import com.iflytek.rpa.resource.common.response.ErrorCodeEnum;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.servlet.NoHandlerFoundException;

/**
 * 全局异常处理器
 * 统一处理应用程序中的各种异常，并返回标准化的错误响应
 *
 * @author system
 * @date 2024
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理业务异常
     *
     * @param e 业务异常
     * @return 错误响应
     */
    @ExceptionHandler(ServiceException.class)
    public ResponseEntity<AppResponse<String>> handleServiceException(ServiceException e) {
        log.warn("业务异常: {}", e.getMessage(), e);
        AppResponse<String> response = AppResponse.error(e.getCode(), e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理参数校验异常 - @Valid 注解校验失败
     *
     * @param e 参数校验异常
     * @return 错误响应
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<AppResponse<String>> handleMethodArgumentNotValidException(
            MethodArgumentNotValidException e) {
        log.warn("参数校验异常: {}", e.getMessage());

        StringBuilder errorMsg = new StringBuilder();
        for (FieldError fieldError : e.getBindingResult().getFieldErrors()) {
            errorMsg.append(fieldError.getField())
                    .append(": ")
                    .append(fieldError.getDefaultMessage())
                    .append("; ");
        }

        AppResponse<String> response =
                AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数校验失败: " + errorMsg.toString());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理参数绑定异常 - @Validated 注解校验失败
     *
     * @param e 参数绑定异常
     * @return 错误响应
     */
    @ExceptionHandler(BindException.class)
    public ResponseEntity<AppResponse<String>> handleBindException(BindException e) {
        log.warn("参数绑定异常: {}", e.getMessage());

        StringBuilder errorMsg = new StringBuilder();
        for (FieldError fieldError : e.getBindingResult().getFieldErrors()) {
            errorMsg.append(fieldError.getField())
                    .append(": ")
                    .append(fieldError.getDefaultMessage())
                    .append("; ");
        }

        AppResponse<String> response =
                AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数绑定失败: " + errorMsg.toString());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理约束违反异常 - @Validated 注解校验失败
     *
     * @param e 约束违反异常
     * @return 错误响应
     */
    @ExceptionHandler(ConstraintViolationException.class)
    public ResponseEntity<AppResponse<String>> handleConstraintViolationException(ConstraintViolationException e) {
        log.warn("约束违反异常: {}", e.getMessage());

        StringBuilder errorMsg = new StringBuilder();
        Set<ConstraintViolation<?>> violations = e.getConstraintViolations();
        for (ConstraintViolation<?> violation : violations) {
            errorMsg.append(violation.getPropertyPath())
                    .append(": ")
                    .append(violation.getMessage())
                    .append("; ");
        }

        AppResponse<String> response =
                AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数约束违反: " + errorMsg.toString());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理缺少请求参数异常
     *
     * @param e 缺少请求参数异常
     * @return 错误响应
     */
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<AppResponse<String>> handleMissingServletRequestParameterException(
            MissingServletRequestParameterException e) {
        log.warn("缺少请求参数异常: {}", e.getMessage());
        String message = String.format("缺少必需的请求参数: %s", e.getParameterName());
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE.getCode(), message);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理方法参数类型不匹配异常
     *
     * @param e 方法参数类型不匹配异常
     * @return 错误响应
     */
    @ExceptionHandler(MethodArgumentTypeMismatchException.class)
    public ResponseEntity<AppResponse<String>> handleMethodArgumentTypeMismatchException(
            MethodArgumentTypeMismatchException e) {
        log.warn("方法参数类型不匹配异常: {}", e.getMessage());
        String message = String.format(
                "参数 '%s' 的值 '%s' 无法转换为类型 '%s'",
                e.getName(), e.getValue(), e.getRequiredType().getSimpleName());
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_PARAM_PARSE.getCode(), message);
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理请求方法不支持异常
     *
     * @param e 请求方法不支持异常
     * @return 错误响应
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<AppResponse<String>> handleHttpRequestMethodNotSupportedException(
            HttpRequestMethodNotSupportedException e) {
        log.warn("请求方法不支持异常: {}", e.getMessage());
        String message =
                String.format("请求方法 '%s' 不支持，支持的方法: %s", e.getMethod(), String.join(", ", e.getSupportedMethods()));
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT.getCode(), message);
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(response);
    }

    /**
     * 处理404异常 - 找不到处理器
     *
     * @param e 找不到处理器异常
     * @return 错误响应
     */
    @ExceptionHandler(NoHandlerFoundException.class)
    public ResponseEntity<AppResponse<String>> handleNoHandlerFoundException(NoHandlerFoundException e) {
        log.warn("找不到处理器异常: {}", e.getMessage());
        String message = String.format("请求路径 '%s' 不存在", e.getRequestURL());
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT.getCode(), message);
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
    }

    /**
     * 处理文件上传大小超限异常
     *
     * @param e 文件上传大小超限异常
     * @return 错误响应
     */
    @ExceptionHandler(MaxUploadSizeExceededException.class)
    public ResponseEntity<AppResponse<String>> handleMaxUploadSizeExceededException(MaxUploadSizeExceededException e) {
        log.warn("文件上传大小超限异常: {}", e.getMessage());
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_PARAM.getCode(), "上传文件大小超出限制");
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理非法参数异常
     *
     * @param e 非法参数异常
     * @return 错误响应
     */
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<AppResponse<String>> handleIllegalArgumentException(IllegalArgumentException e) {
        log.warn("非法参数异常: {}", e.getMessage(), e);
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_PARAM.getCode(), e.getMessage());
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
    }

    /**
     * 处理空指针异常
     *
     * @param e 空指针异常
     * @return 错误响应
     */
    @ExceptionHandler(NullPointerException.class)
    public ResponseEntity<AppResponse<String>> handleNullPointerException(NullPointerException e) {
        log.error("空指针异常: {}", e.getMessage(), e);
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_EXCEPTION.getCode(), "系统内部错误");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }

    /**
     * 处理运行时异常
     *
     * @param e 运行时异常
     * @return 错误响应
     */
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<AppResponse<String>> handleRuntimeException(RuntimeException e) {
        log.error("运行时异常: {}", e.getMessage(), e);
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_EXCEPTION.getCode(), "系统运行异常");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }

    /**
     * 处理所有其他异常
     *
     * @param e 异常
     * @return 错误响应
     */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<AppResponse<String>> handleException(Exception e) {
        log.error("系统异常: {}", e.getMessage(), e);
        AppResponse<String> response = AppResponse.error(ErrorCodeEnum.E_EXCEPTION.getCode(), "系统内部错误");
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
    }
}
