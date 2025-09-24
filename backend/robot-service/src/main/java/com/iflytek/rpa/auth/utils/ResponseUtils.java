package com.iflytek.rpa.auth.utils;

/**
 * @desc: TODO
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/16 19:27
 */
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.auth.entity.Result;
import java.io.PrintWriter;
import javax.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;

public class ResponseUtils {

    private static final Logger logger = LoggerFactory.getLogger(ResponseUtils.class);

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static void success(HttpServletResponse response, Object data) {
        Result result = new Result(200, "ok", data);
        writeResultToResponse(response, result);
    }

    public static void fail(HttpServletResponse response, String message) {
        Result result = new Result(500, message, null);
        writeResultToResponse(response, result);
    }

    private static void writeResultToResponse(HttpServletResponse response, Result result) {
        try {
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.setCharacterEncoding("UTF-8");
            PrintWriter writer = response.getWriter();
            String json = objectMapper.writeValueAsString(result);
            writer.write(json);
            writer.flush();
        } catch (Exception e) {
            logger.error("failed to write to the response stream", e);
        }
    }
}
