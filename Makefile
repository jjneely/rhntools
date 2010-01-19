VERSION=0.0.2
NAME=rhntools
SPEC=rhntools.spec

ifndef PYTHON
PYTHON=/usr/bin/python
endif
SITELIB=`$(PYTHON) -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`

.PHONY: archive clean

all:
	@echo "$(NAME) Makefile"
	@echo
	@echo "make clean 		-- Clean the source directory"
	@echo "make archive		-- Build a tar.bz2 ball for release"
	@echo "make srpm		-- Build a src.rpm for release"
	@echo "make tag         -- Tag for a git release"
	@echo "make release     -- Tag and make an archive for release"
	@echo "make install     -- Do useful things - define a DESTDIR"
	@echo

install:
	install -d -m 755 $(DESTDIR)/usr/share/$(NAME)
	install -d -m 755 $(DESTDIR)/usr/bin
	
	install -m 644 *.py $(DESTDIR)/usr/share/$(NAME)
	install -m 755 *.sh $(DESTDIR)/usr/bin
	install -m 755 send_nsca.pl $(DESTDIR)/usr/bin
	
srpm: archive
	rpmbuild --define "_srcrpmdir ." -ts $(NAME)-$(VERSION).tar.bz2

clean:
	rm -f `find . -name \*.pyc -o -name \*~`
	rm -f $(NAME)-*.tar.bz2

release: tag archive

tag:
	git tag -f -a -m "Tag $(VERSION)" $(VERSION)

archive:
	if ! grep "Version: $(VERSION)" $(SPEC) > /dev/null ; then \
		sed -i '/^Version: $(VERSION)/q; s/^Version:.*$$/Version: $(VERSION)/' $(SPEC) ; \
		git add $(SPEC) ; git commit -m "Bumb version tag to $(VERSION)" ; \
	fi
	git archive --prefix=$(NAME)-$(VERSION)/ \
		--format=tar HEAD | bzip2 > $(NAME)-$(VERSION).tar.bz2
	@echo "The archive is in $(NAME)-$(VERSION).tar.bz2"

