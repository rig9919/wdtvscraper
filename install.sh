INSTALL_DIR=/usr/lib/wdtvscraper
BINARY_DIR=/usr/bin

if [ ! -d "$INSTALL_DIR" ]; then
	mkdir "$INSTALL_DIR"
fi

cp -r ./src/*.py ./src/pytmdb3 ./src/pytvdb "$INSTALL_DIR"
ln -s "$INSTALL_DIR/scraper.py" "$BINARY_DIR/wdtvscraper"
