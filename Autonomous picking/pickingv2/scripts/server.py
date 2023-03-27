#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/25 下午6:53
"""
import asyncio

import uvicorn
import cv2
import socketio
import numpy as np
import rospy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
import aiorospy

import pickingv2.msg

sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode="asgi")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_app = socketio.ASGIApp(sio, socketio_path="socket.io")
app.mount("/ws", _app)

img: np.ndarray = cv2.imread("/home/msi/Documents/data/div-rgb-png/0B_c.png")
_, blank_img = cv2.imencode('.png', np.zeros((1080, 1920, 3), dtype=np.uint8))


def failure_resp(msg):
    return {'success': False, 'msg': msg}


def success_resp():
    return {'success': False, 'msg': ''}


class SystemView:
    def __init__(self):
        self._view = {
            "image": None,
            "targets": None,
            "runningTask": None,
        }
        self._lock = asyncio.Lock()
        self.remote_ac = aiorospy.AsyncActionClient("PickingCmd", pickingv2.msg.PickingCmdAction, feedback_queue_size=20)
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.remote_ac.start)

    async def get_current_view(self) -> dict:
        async with self._lock:
            return self._view

    async def exec(self, cmd_data):
        name = cmd_data['name']
        if name not in ['go_home', 'auto', 'stop', 'move_forward', "move_backward"]:
            return failure_resp(f"no such command: {name}")
        print("exec", cmd_data)
        goal = pickingv2.msg.PickingCmdGoal()
        goal.name = name
        print("sss")
        goal_handle = await self.remote_ac.ensure_goal(goal, resend_timeout=1)
        print("sssccc")
        for f in goal_handle.feedback():
            print(f)
        print(goal_handle.result)
        # if not resp.success:
        #     return failure_resp(f"exec {name} failed: {resp.desc}")
        return success_resp()


s = SystemView()


@app.get("/")
async def index():
    return FileResponse("./template/index.html", )


@sio.event
async def connect(sid, environ):
    print('connect ', sid)


@sio.event
async def view_init(sid, data):
    return await s.get_current_view()


@sio.event
async def cmd(sid, data):
    return await s.exec(data)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    rospy.init_node("app_server")
    uvicorn.run(app, host='0.0.0.0', port=8123)
