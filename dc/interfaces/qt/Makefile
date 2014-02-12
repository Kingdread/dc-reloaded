all: window resources

resources: resource-files/resources.qrc
	pyrcc4 -py3 -o resources.py resource-files/resources.qrc

window: main.ui
	pyuic4 -o ui_main.py -x --resource-suffix="" --from-imports main.ui
