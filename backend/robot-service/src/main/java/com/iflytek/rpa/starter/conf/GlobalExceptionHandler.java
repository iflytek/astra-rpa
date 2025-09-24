package com.iflytek.rpa.starter.conf;

import com.iflytek.rpa.starter.exception.NoDataException;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.LoggerUtils;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.sql.SQLException;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import javax.validation.ConstraintViolationException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.validation.BindException;
import org.springframework.validation.ObjectError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger LOGGER = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    public GlobalExceptionHandler() {}

    @ExceptionHandler({ServiceException.class})
    @ResponseBody
    public AppResponse serviceExceptionHandler(HttpServletRequest request, ServiceException e) {
        LOGGER.error("服务端代码报错，报错为：{}", e.getMessage());
        e.printStackTrace();
        return AppResponse.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler({ConstraintViolationException.class})
    @ResponseBody
    public AppResponse constraintViolationExceptionHandler(HttpServletRequest request, ConstraintViolationException e) {
        LOGGER.error("服务端代码报错，报错为：{}", e.getMessage());
        e.printStackTrace();
        return AppResponse.error(ErrorCodeEnum.E_SERVICE.getCode(), e.getMessage());
    }

    @ExceptionHandler({MethodArgumentNotValidException.class})
    public AppResponse<String> handlerValidException(MethodArgumentNotValidException e) {
        List<ObjectError> allErrors = e.getBindingResult().getAllErrors();
        LOGGER.error("方法参数无效异常", e);
        return this.validException(allErrors);
    }

    @ExceptionHandler({BindException.class})
    public AppResponse<String> handlerValidException(BindException e) {
        List<ObjectError> allErrors = e.getBindingResult().getAllErrors();
        LOGGER.error("BindException", e);
        return this.validException(allErrors);
    }

    private AppResponse<String> validException(List<ObjectError> allErrors) {
        StringBuilder errors = new StringBuilder();

        for (int i = 0; i < allErrors.size(); ++i) {
            if (i == allErrors.size() - 1) {
                errors.append(allErrors.get(i).getDefaultMessage());
            } else {
                errors.append(allErrors.get(i).getDefaultMessage()).append(" | ");
            }
        }

        LoggerUtils.error("参数校验失败：" + errors);
        return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK.getCode(), String.valueOf(errors));
    }

    @ExceptionHandler({NoLoginException.class})
    @ResponseBody
    public AppResponse noLoginExceptionHandler(NoLoginException e) {
        return AppResponse.error(ErrorCodeEnum.E_NOT_LOGIN, "用户登录信息失效");
    }

    @ExceptionHandler({IllegalArgumentException.class})
    @ResponseBody
    public AppResponse illegalArgumentExceptionHandler(IllegalArgumentException e) {
        LOGGER.error(LoggerUtils.getExceptionInfo(e));
        return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
    }

    @ExceptionHandler({NullPointerException.class})
    @ResponseBody
    public AppResponse<String> nullPointerExceptionHandler(NullPointerException e) {
        LOGGER.error(LoggerUtils.getExceptionInfo(e));
        return AppResponse.error(ErrorCodeEnum.E_PARAM);
    }

    @ExceptionHandler({DataIntegrityViolationException.class})
    @ResponseBody
    public AppResponse<String> dataIntegrityViolationExceptionHandler(DataIntegrityViolationException e) {
        LOGGER.error(LoggerUtils.getExceptionInfo(e));
        return AppResponse.error(ErrorCodeEnum.E_SQL);
    }

    @ExceptionHandler({Exception.class})
    public AppResponse<String> handleException(Exception ex) {
        LOGGER.error("===========全局统一异常处理============");
        LOGGER.error(LoggerUtils.getExceptionInfo(ex));
        return ex instanceof HttpRequestMethodNotSupportedException
                ? AppResponse.error("请求类型错误")
                : AppResponse.error(ErrorCodeEnum.E_EXCEPTION);
    }

    @ExceptionHandler({Throwable.class})
    public AppResponse<String> handleThrowable(Throwable t) {
        LOGGER.error("Application Throwable Exception: [" + t.getClass().getName() + "]", t);
        return AppResponse.error(ErrorCodeEnum.E_EXCEPTION);
    }

    @ExceptionHandler({SQLException.class})
    @ResponseBody
    public AppResponse<String> handlerSqlException(SQLException e) {
        LOGGER.error("Sql数据保存失败", e);
        return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
    }

    @ExceptionHandler({DataAccessException.class})
    @ResponseBody
    public AppResponse<String> handlerDataAccessException(DataAccessException e) {
        LOGGER.error("错误使用数据", e);
        return AppResponse.error(ErrorCodeEnum.E_SQL);
    }

    @ExceptionHandler({NoDataException.class})
    @ResponseBody
    public AppResponse<String> handlerDataAccessException(NoDataException e) {
        LOGGER.error("没有数据异常", e);
        return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY);
    }

    @ExceptionHandler({DuplicateKeyException.class})
    @ResponseBody
    public AppResponse<String> handlerDataAccessException(DuplicateKeyException e) {
        LOGGER.error("数据重复", e);
        return AppResponse.error(ErrorCodeEnum.E_SQL_REPEAT);
    }

    @ExceptionHandler({HttpRequestMethodNotSupportedException.class})
    @ResponseBody
    public AppResponse<String> handlerDataAccessException(HttpRequestMethodNotSupportedException e) {
        LOGGER.error("Http请求方法不支持", e);
        return AppResponse.error(ErrorCodeEnum.E_COMMON);
    }

    @ExceptionHandler({MethodArgumentTypeMismatchException.class})
    @ResponseBody
    public AppResponse<String> handlerDataAccessException(MethodArgumentTypeMismatchException e) {
        LOGGER.error("方法参数类型不匹配异常", e);
        return AppResponse.error(ErrorCodeEnum.E_PARAM);
    }

    @ExceptionHandler({MissingServletRequestParameterException.class})
    @ResponseBody
    public AppResponse<String> handlerDataAccessException(MissingServletRequestParameterException e) {
        LOGGER.error("缺少Servlet请求参数异常", e);
        return AppResponse.error(ErrorCodeEnum.E_PARAM);
    }
}
