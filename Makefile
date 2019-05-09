all:
	make -C tgrocery/learner

clean:
	rm -rf *.svm *.converter *.model *.config *.out *.pyc build *.egg-info
	make -C tgrocery/learner  clean