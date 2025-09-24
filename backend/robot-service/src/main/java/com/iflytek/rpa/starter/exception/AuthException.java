package com.iflytek.rpa.starter.exception;

public class AuthException extends Exception {
    public AuthException() {
        super();
    }

    public AuthException(String message) {
        super(message);
    }

    public AuthException(Exception e) {
        super(e);
    }
}
