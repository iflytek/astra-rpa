package com.iflytek.rpa.starter.exception;

/**
 * 项目名称： com.iflytek.projectmanage.common.exception
 * 类 名 称： NoFileException
 * 类 描 述： 文件找不到异常
 * 创建时间： 2020/4/26 4:00 下午
 * 创 建 人： keler
 **/
public class NoFileException extends Exception {

    public NoFileException() {
        super();
    }

    public NoFileException(String message) {
        super(message);
    }

    public NoFileException(Exception e) {
        super(e);
    }
}
