INSTALL_DIR=/usr/lib/wdtvscraper
BINARY_DIR=/usr/bin
PIL_DIR=$(echo -e "import PIL,os\nprint os.path.dirname(PIL.__file__)" | python)

if [ ! -d "$INSTALL_DIR" ]; then
	mkdir "$INSTALL_DIR"
fi

cp -r ./src/*.py ./src/pytmdb3 ./src/pytvdb "$INSTALL_DIR"
cp "./src/ter28-16.pil" "./src/ter28-16.pbm" "$PIL_DIR"
ln -s "$INSTALL_DIR/scraper.py" "$BINARY_DIR/wdtvscraper"
