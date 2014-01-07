INSTALL=/usr/bin/install

INSTALLDIR=/usr/local/lib/wdtvscraper
BINDIR=/usr/local/bin
MANDIR=/usr/local/share/man/man1

install:
		mkdir -p $(INSTALLDIR)
		$(INSTALL) ./src/*.py $(INSTALLDIR)
		cp -r ./src/pytmdb3 $(INSTALLDIR)
		cp -r ./src/pytvdb $(INSTALLDIR)
		$(INSTALL) ./src/ter28-16.* $(INSTALLDIR)
		$(INSTALL) ./doc/wdtvscraper.1.gz $(MANDIR)
		ln -s $(INSTALLDIR)/scraper.py $(BINDIR)/wdtvscraper

uninstall:
		rm -rf $(BINDIR)/wdtvscraper
		rm -rf $(INSTALLDIR)
		rm -rf $(MANDIR)/wdtvscraper.1.gz
