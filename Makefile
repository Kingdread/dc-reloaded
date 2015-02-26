all: window resources

resources: resource-files/resources.qrc
	pyrcc4 -py3 -o dc/interface/resources.py resource-files/resources.qrc

window: resource-files/main.ui
	pyuic4 -o dc/interface/ui_main.py -x --resource-suffix="" --from-imports resource-files/main.ui
