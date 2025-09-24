package com.iflytek.rpa.base.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.METHOD) // 表示这个注解只能用于方法上
@Retention(RetentionPolicy.RUNTIME) // 表示这个注解在运行时可用
public @interface LogExecutionTime {}
