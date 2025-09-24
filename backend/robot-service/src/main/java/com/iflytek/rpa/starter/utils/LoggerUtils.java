package com.iflytek.rpa.starter.utils;

import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggerUtils {
    public LoggerUtils() {}

    public static void error(Logger logger, String message, Exception ex) {
        logger.error(message);
        if (ex != null) {
            logger.error(getExceptionInfo(ex));
        }
    }

    public static void error(String message, Exception ex) {
        error(getLoggerBySelf(), message, ex);
    }

    public static void error(Logger logger, String message) {
        error(logger, message, null);
    }

    public static void error(String message) {
        error(getLoggerBySelf(), message);
    }

    public static void warn(Logger logger, String message, Exception ex) {
        logger.warn(message);
        if (ex != null) {
            logger.warn(getExceptionInfo(ex));
        }
    }

    public static void warn(String message, Exception ex) {
        warn(getLoggerBySelf(), message, ex);
    }

    public static void warn(Logger logger, String message) {
        warn(logger, message, null);
    }

    public static void warn(String message) {
        warn(getLoggerBySelf(), message);
    }

    public static void info(Logger logger, String message, Exception ex) {
        logger.info(message);
        if (ex != null) {
            logger.info(getExceptionInfo(ex));
        }
    }

    public static void info(String message, Exception ex) {
        info(getLoggerBySelf(), message, ex);
    }

    public static void info(Logger logger, String message) {
        info(logger, message, null);
    }

    public static void info(String message) {
        info(getLoggerBySelf(), message);
    }

    public static void debug(Logger logger, String message, Exception ex) {
        logger.debug(message);
        if (ex != null) {
            logger.debug(getExceptionInfo(ex));
        }
    }

    public static void debug(String message, Exception ex) {
        debug(getLoggerBySelf(), message, ex);
    }

    public static void debug(Logger logger, String message) {
        debug(logger, message, null);
    }

    public static void debug(String message) {
        debug(getLoggerBySelf(), message);
    }

    public static String getExceptionInfo(Exception ex) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        PrintStream printStream = new PrintStream(out);
        ex.printStackTrace(printStream);
        String rs = out.toString();

        try {
            printStream.close();
            out.close();
        } catch (Exception var5) {
            var5.printStackTrace();
        }

        return rs;
    }

    public static Logger getLoggerBySelf() {
        StackTraceElement[] stackTraceElements = Thread.currentThread().getStackTrace();
        return stackTraceElements.length >= 4
                ? LoggerFactory.getLogger(stackTraceElements[3].getClassName())
                : LoggerFactory.getLogger(LoggerUtils.class);
    }

    public static Logger getLogger() {
        StackTraceElement[] stackTraceElements = Thread.currentThread().getStackTrace();
        return stackTraceElements.length >= 3
                ? LoggerFactory.getLogger(stackTraceElements[2].getClassName())
                : LoggerFactory.getLogger(LoggerUtils.class);
    }
}
