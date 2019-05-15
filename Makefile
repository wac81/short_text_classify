all:
	make -C stclassify/svc_impl

clean:
	rm -rf *.svm *.converter *.model *.config *.out *.pyc build *.egg-info
	make -C stclassify/svc_impl  clean