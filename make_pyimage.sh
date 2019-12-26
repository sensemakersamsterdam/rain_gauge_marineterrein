rm -r ./pyimage
mkdir ./pyimage
cp -r lib ./pyimage
cp *.py ./pyimage
cp micropython-wifimanager/wifi_manager/wifi_manager.py ./pyimage/lib
cp networks.json ./pyimage
