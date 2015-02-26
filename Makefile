all: window resources

resources: resource-files/resources.qrc
	pyrcc5 -o dc/interface/resources.py resource-files/resources.qrc

window: resource-files/main.ui
	pyuic5 -o dc/interface/ui_main.py -x --resource-suffix="" --from-imports resource-files/main.ui
