from obswebsocket import obsws, requests
import os
import time
import random


class OBSWebsocket:
    def __init__(self):
        self.ws = obsws(
            host=os.environ.get('WEBSOCKET_HOST'),
            port=os.environ.get('WEBSOCKET_PORT'),
            password=os.environ.get('WEBSOCKET_PASSWORD')
        )
        self.resolution_x = 1920
        self.resolution_y = 1080

        try:
            self.ws.connect()
        except Exception as e:
            print(e)
        else:
            print('--- Connected to Websocket ---')

    def disconnect(self):
        self.ws.disconnect()

    def change_source_visibility(self, scene_name, source_name, source_visibility=True):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        self.ws.call(requests.SetSceneItemEnabled(sceneName=scene_name, sceneItemId=myItemID, sceneItemEnabled=source_visibility))

    def move_source(self, scene_name, source_name, x_pos, y_pos, rot):
        new_transform = {'positionX': x_pos, 'positionY': y_pos, 'rotation': rot}
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        self.ws.call(requests.SetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID, sceneItemTransform=new_transform))

    def get_current_position(self, scene_name, source_name):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        response = self.ws.call(requests.GetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID))
        return response.datain["sceneItemTransform"]["positionX"], response.datain["sceneItemTransform"]["positionY"], response.datain["sceneItemTransform"]["rotation"]

    def get_source_dim(self, scene_name, source_name):
        response = self.ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source_name))
        myItemID = response.datain['sceneItemId']
        response = self.ws.call(requests.GetSceneItemTransform(sceneName=scene_name, sceneItemId=myItemID))
        return response.datain["sceneItemTransform"]['width'], response.datain['sceneItemTransform']['height']

    def move_offscreen(self, scene_name, source_name):
        """This is assuming a 1920x1080 resolution"""
        x_pos, y_pos, rot = self.get_current_position(scene_name=scene_name, source_name=source_name)
        width, height = self.get_source_dim(scene_name=scene_name, source_name=source_name)
        if rot == 0:  # Bottom
            for step in range(int(y_pos), self.resolution_y):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=x_pos, y_pos=step, rot=rot)
                time.sleep(0.001)
        elif rot == 90:  # Left side
            for step in range(int(x_pos), 0, -1):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=step, y_pos=y_pos, rot=rot)
                time.sleep(0.001)
        elif rot == 180:  # Top
            for step in range(int(y_pos), 0, -1):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=x_pos, y_pos=step, rot=rot)
                time.sleep(0.001)
        else:  # Right side
            for step in range(int(x_pos), self.resolution_x):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=step, y_pos=y_pos, rot=rot)
                time.sleep(0.001)

    def set_random_pos(self, scene_name, source_name):
        """This is assuming a 1920x1080 resolution"""
        x_pos, y_pos, rot = self.get_current_position(scene_name=scene_name, source_name=source_name)
        width, height = self.get_source_dim(scene_name=scene_name, source_name=source_name)

        rot = random.choice([0, 90, 180, 270])
        if rot == 0 or rot == 180:
            x_pos = random.randint(0, self.resolution_x - width)
        else:
            y_pos = random.randint(0, self.resolution_y - height)
        return x_pos, y_pos, rot

    def move_onscreen(self, scene_name, source_name, add=None):
        x_pos, y_pos, rot = self.set_random_pos(scene_name=scene_name, source_name=source_name)
        width, height = self.get_source_dim(scene_name=scene_name, source_name=source_name)
        if add:
            width += add[0]
            height += add[1]
            x_pos = add[2]
            y_pos = add[3]
            rot = add[4]

        if rot == 0:
            for step in range(self.resolution_y, self.resolution_y - int(height), -1):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=x_pos, y_pos=step, rot=rot)
                time.sleep(0.001)
        elif rot == 90:
            for step in range(0, int(width)):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=step, y_pos=y_pos, rot=rot)
                time.sleep(0.001)
        elif rot == 180:
            for step in range(0, int(height)):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=x_pos, y_pos=step, rot=rot)
                time.sleep(0.001)
        else:
            for step in range(self.resolution_x, self.resolution_x - int(width), -1):
                self.move_source(scene_name=scene_name, source_name=source_name, x_pos=step, y_pos=y_pos, rot=rot)
                time.sleep(0.001)

    def pipe_animation(self, scene_name, source_name1, source_name2):
        width, height = self.get_source_dim(scene_name=scene_name, source_name=source_name2)

        self.move_offscreen(scene_name=scene_name, source_name=source_name1)
        self.move_offscreen(scene_name=scene_name, source_name=source_name2)

        self.move_onscreen(scene_name=scene_name, source_name=source_name2)
        x_pos, y_pos, rot = self.get_current_position(scene_name=scene_name, source_name=source_name2)
        self.move_onscreen(scene_name=scene_name, source_name=source_name1, add=(width, height, x_pos, y_pos, rot))
