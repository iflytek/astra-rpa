package com.iflytek.rpa.starter.exception;

public class NoLoginException extends Exception {
    public NoLoginException() {}

    public NoLoginException(String message) {
        super(message);
    }

    public NoLoginException(Exception e) {
        super(e);
    }
}
