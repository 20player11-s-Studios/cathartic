VERSION ?= 0.1.0
IMAGE ?= build/dist/Cathartic-x86_64.AppImage
APPIMAGETOOL ?= /tmp/appimagetool

.PHONY: all clean appimage install uninstall

all: appimage

build/AppDir/usr/bin/cathartic: $(shell find cathartic -name '*.py')
	pyinstaller build/cathartic.spec --distpath build/dist --workpath build/work

appimage: build/AppDir/usr/bin/cathartic
	VERSION=$(VERSION) $(APPIMAGETOOL) --no-appstream build/AppDir $(IMAGE)

clean:
	rm -rf build/dist build/work build/AppDir/usr/bin

install:
	./install.sh

uninstall:
	./uninstall.sh
