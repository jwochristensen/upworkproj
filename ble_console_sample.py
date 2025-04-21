import time
from ble import FlaskBleMain

main = FlaskBleMain()

main.Start()
i = 0

print('BLE server started')
while True:
    time.sleep(1)
    value =  'tx: Test {}'.format(i)
    i += 1
    print(value)
    main.Send(value) 


print('Finish')


