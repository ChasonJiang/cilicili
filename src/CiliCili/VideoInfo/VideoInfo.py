from qasync import asyncSlot
import aiohttp


class VideoInfo():
    def __init__(self,context:dict):
        self.data:dict = context


    @asyncSlot()
    async def requestData(self):
        pass
        
    def createMediaInfo(self):
        pass