import argparse
import asyncio
import json
import sys
import time

import pyautogui
import websockets
from cv_picker.core import PickType, Status
from cv_picker.core.core import IPickCore
from cv_picker.core.message import (
    PickerInputData,
    PickerResponse,
    PickerResponseItem,
    PickerSign,
)
from cv_picker.core.picker import CVPicker, Socket, logger


async def handler(websocket):
    try:
        picker = CVPicker(status=Status.INIT, picktype=PickType.TARGET)
        # 处理前端 Websocket 发送过来的消息
        async for message in websocket:
            data = json.loads(message)
            input_data = PickerInputData(**data)
            logger.info(
                f"remote_addr:{Config.REMOTE_ADDR}, port:{Config.CV_PICKER_PORT}, input_data.sign:{input_data.pick_type}"
            )

            # 判断是否收到开始拾取信号
            if input_data.pick_sign == PickerSign.START:
                logger.info(f"START CV PICKER")
                # 初始化拾取
                picker.set(status=Status.INIT, picktype=PickType.TARGET)
                status, msg = picker.run()

                # 根据拾取返回的不同状态返回响应的响应
                if status == Status.OVER:
                    if msg is not None:
                        await websocket.send(PickerResponse(err_msg="", data=msg).json())
                    else:
                        await websocket.send(
                            PickerResponse(
                                err_msg="拾取失败，未拾取到元素",
                                data="",
                                key=PickerResponseItem.ERROR,
                            ).json()
                        )
                    continue
                elif status == Status.TIMEOUT:
                    await websocket.send(
                        PickerResponse(err_msg="拾取超时", data="", key=PickerResponseItem.ERROR).json()
                    )
                    continue
                elif status == Status.CANCEL:
                    await websocket.send(
                        PickerResponse(err_msg="拾取取消", data="", key=PickerResponseItem.CANCEL).json()
                    )
                    continue
                else:
                    raise NotImplementedError()
            # 判断是否收到校验信号
            elif input_data.pick_sign == PickerSign.VALIDATE:
                with Socket() as hl:
                    data = json.loads(input_data.data)
                    logger.info("校验data ", data)
                    print("进入校验")
                    # 执行校验程序，获取目标元素位置
                    match_rect = IPickCore.match_imgs(data=data, remote_addr=Config.REMOTE_ADDR)
                    print(f"匹配目标：{match_rect}")
                    if match_rect:
                        # 向高亮发送坐标信息，进行高亮显示
                        logger.info(f"目标元素校验成功，元素坐标：{match_rect}")
                        hl.send_rect(operation="validate", rect=match_rect)
                        time.sleep(3)
                        await websocket.send(PickerResponse(err_msg="", data="校验成功").json())
                    else:
                        # 发送未校验到目标元素
                        logger.info(f"目标元素校验失败")
                        await websocket.send(
                            PickerResponse(
                                err_msg="未校验到目标元素，请检查页面元素或降低校验相似度重试",
                                data="",
                                key=PickerResponseItem.ERROR,
                            ).json()
                        )

                    continue

            # 判断是否收到锚点重拾的信号
            elif input_data.pick_sign == PickerSign.DESIGNATE:
                with Socket() as hl:
                    data = json.loads(input_data.data)
                    # 首先进行目标元素校验，判断当前界面是否存在目标元素
                    match_rect = IPickCore.match_imgs(data=data, remote_addr=Config.REMOTE_ADDR)
                    desktop_img = pyautogui.screenshot()
                    if match_rect:
                        # 向高亮发送designate信号及目标元素坐标，进行标识
                        hl.send_rect(operation="start", status="designate", rect=match_rect)
                        # 开始拾取锚点图像
                        logger.info(f"元素校验成功，开始拾取锚点")
                        picker.set(
                            status=Status.INIT,
                            picktype=PickType.ANCHOR,
                            anchor_pick_img=desktop_img,
                        )
                        status, anchor_msg = picker.run()
                    else:
                        # 未检测到目标元素，报错返回
                        logger.info(f"元素校验失败，当前界面无目标元素")
                        await websocket.send(
                            PickerResponse(
                                err_msg="当前界面未检测到目标元素，无法拾取锚点",
                                data="",
                                key=PickerResponseItem.ERROR,
                            ).json()
                        )
                        continue

                    # 根据拾取返回的不同状态返回响应的响应
                    if status == Status.OVER:
                        if anchor_msg is not None:
                            await websocket.send(PickerResponse(err_msg="", data=anchor_msg).json())
                        else:
                            await websocket.send(
                                PickerResponse(
                                    err_msg="拾取失败，未拾取到锚点元素",
                                    data="",
                                    key=PickerResponseItem.ERROR,
                                ).json()
                            )
                    elif status == Status.TIMEOUT:
                        logger.info("拾取超时")
                        await websocket.send(
                            PickerResponse(
                                err_msg="拾取超时",
                                data="",
                                key=PickerResponseItem.ERROR,
                            ).json()
                        )
                        continue
                    elif status == Status.CANCEL:
                        logger.info("拾取取消")
                        await websocket.send(
                            PickerResponse(
                                err_msg="拾取取消",
                                data="",
                                key=PickerResponseItem.CANCEL,
                            ).json()
                        )
                    else:
                        raise NotImplementedError()
                    continue

    except websockets.ConnectionClosed as e:
        logger.info(f"Connection closed: {e}")
    except Exception as e:
        logger.info(f"程序执行报错：{e}")
    finally:
        logger.info("Client disconnected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", type=str, default="cv_picker")
    parser.add_argument("--cv_picker_port", type=int, default=8008)
    parser.add_argument("--highlight_socket_port", type=int, default=11001)
    parser.add_argument("--remote_addr", type=str, default="http://localhost:31680")
    try:
        args = parser.parse_args()
        # 正常的业务逻辑
        logger.info(
            f"Starting application with schema: {args.schema}, "
            f"cv_picker_port: {args.cv_picker_port}, highlight_socket_port: {args.highlight_socket_port}"
        )
    except SystemExit as e:
        # argparse 通过调用 sys.exit() 来处理不正确的参数，这会抛出 SystemExit 异常
        logger.error("Error parsing arguments", exc_info=True)
        sys.exit(e.code)

    schema = args.schema
    cv_picker_port = args.cv_picker_port
    highlight_socket_port = args.highlight_socket_port
    remote_addr = args.remote_addr

    from cv_picker.config import Config

    Config.CV_PICKER_PORT = cv_picker_port
    Config.HL_SOCKET_PORT = highlight_socket_port
    Config.REMOTE_ADDR = remote_addr

    if schema == "cv_picker":
        try:
            # 设置和运行websocket服务器的主函数
            async def main():
                # 在指定的主机和端口上启动Websocket服务器
                start_serve = websockets.serve(handler, "localhost", Config.CV_PICKER_PORT)
                # 等待服务器启动完成
                await start_serve
                try:
                    await asyncio.Future()  # run forever
                except asyncio.CancelledError:
                    print("Server stopped")

            asyncio.run(main())
        except Exception as e:
            logger.exception(e)
            sys.exit(-1)
