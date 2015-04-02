all: interface resources

resources: dc/interface/resources.py

dc/interface/resources.py: resource-files/resources.qrc
	pyrcc5 -o $@ $<

interface: dc/interface/ui_main.py dc/interface/ui_editor.py

dc/interface/ui_main.py: resource-files/main.ui
	pyuic5 -o $@ -x --resource-suffix="" --from-imports $<

dc/interface/ui_editor.py: resource-files/editor.ui
	pyuic5 -o $@ -x --resource-suffix="" --from-imports $<

lint:
	@pylint dc || true
	@flake8 dc --exclude=ui_editor.py,ui_main.py,resources.py || true

test:
	@python3 -m dc.test

.PHONY: lint test
