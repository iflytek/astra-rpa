package com.iflytek.rpa.starter.exception;

public class DictionaryException extends Exception {
    public DictionaryException() {
        super();
    }

    public DictionaryException(String message) {
        super(message);
    }

    public DictionaryException(Exception e) {
        super(e);
    }
}
