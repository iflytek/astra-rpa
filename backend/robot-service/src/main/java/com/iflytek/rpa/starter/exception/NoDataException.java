package com.iflytek.rpa.starter.exception;

public class NoDataException extends Exception {
    public NoDataException() {}

    public NoDataException(String message) {
        super(message);
    }

    public NoDataException(Exception e) {
        super(e);
    }
}
