package com.iflytek.rpa.base.annotation;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

// @Documented
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
public @interface RobotVersionAnnotation {

    Class<?> clazz() default BaseDto.class;

    boolean printLog() default true;
}
