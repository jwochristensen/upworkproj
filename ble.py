from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import (
    characteristic,
    CharacteristicFlags as CharFlags,
)
from bluez_peripheral.gatt.descriptor import descriptor, DescriptorFlags as DescFlags
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.util import get_message_bus, Adapter
from bluez_peripheral.agent import NoIoAgent, TestAgent, AgentCapability
import asyncio
import threading
import time

from uuids import flask_ble_uuids

class FlaskBleService(Service):
    def __init__(self):
        self.tx_characteristic_value = ''
        super().__init__(flask_ble_uuids["Service"], True)

    @characteristic(flask_ble_uuids["TX_chr"], CharFlags.NOTIFY | CharFlags.READ)
    def tx_characteristic(self, _):
        return self.tx_characteristic_value
    

    @characteristic(flask_ble_uuids["RX_chr"], CharFlags.WRITE_WITHOUT_RESPONSE)
    def rx_characteristic(self, _):
        pass 

    @rx_characteristic.setter
    def rx_characteristic_setter(self, value, options):
        s = value.decode("utf-8")
        print('rx: ' + s)

    def Send(self, s):
        self.tx_characteristic_value = s.encode()
        self.tx_characteristic.changed(self.tx_characteristic_value)


class FlaskBleMain:
    def __init__(self) -> None:
       self.is_running = False
       self.is_stop_requested = False
       self.service = FlaskBleService()
       #self.agent = NoIoAgent()
       self.agent = TestAgent(AgentCapability.NO_INPUT_NO_OUTPUT)

    def _loop_(self) -> None:
        loop = asyncio.new_event_loop()
        task = loop.create_task(self._loop_async_())
        loop.run_until_complete(task)
        loop.close()

    async def _loop_async_(self) -> None:
        self.bus = await get_message_bus() 
        await self.agent.register(self.bus)
        await self.service.register(self.bus)
        self.service_ids = [flask_ble_uuids["Service"]]
        self.adapter = await Adapter.get_first(self.bus)
        self.advert = Advertisement("rpi-flask-gatt-server", self.service_ids, 0, 0)
        await self.advert.register(self.bus, self.adapter)
        await self.bus.wait_for_disconnect()
        while not self.is_stop_requested:
            time.sleep(0.1) 

        self.advert.Release()
        await self.service.unregister()
        self.bus.disconnect()
        self.is_running = False

    def Start(self) -> None:
        if self.is_running:
            return

        self.is_running = True        
        self.runner = threading.Thread(target=self._loop_)
        self.runner.start()

    def Stop(self) -> None:
        if not self.is_running:
            return
        
        self.is_stop_requested = True
        self.bus.disconnect()
        while self.is_running:
            time.sleep(0.1)
        

    def Send(self, s):
        if not self.is_running:
            return
        
        self.service.Send(s)




