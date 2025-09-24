package com.iflytek.rpa.triggerTask.entity.dto;

import java.util.Date;
import java.util.List;
import lombok.Data;

@Data
public class MailInfo {

    private List<String> fromAddresses;
    private List<String> toAddresses;
    private String title;
    private String content;
    private Boolean isAttachment;
    private String contentType;
    private Date time;
}
