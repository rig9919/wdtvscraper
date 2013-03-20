INSTALL_DIR=/usr/lib/wdtvscraper
BINARY_DIR=/usr/bin
MAN_DIR=/usr/share/man

if [ ! -d "$INSTALL_DIR" ]; then
	mkdir "$INSTALL_DIR"
fi

cp -r ./src/*.py ./src/pytmdb3 ./src/pytvdb "$INSTALL_DIR"
cp "./src/ter28-16.pil" "./src/ter28-16.pbm" "$INSTALL_DIR"
cp "./doc/wdtvscraper.1.gz" "$MAN_DIR/man1/wdtvscraper.1.gz"
ln -s "$INSTALL_DIR/scraper.py" "$BINARY_DIR/wdtvscraper"
