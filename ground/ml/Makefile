SHELL :=/bin/bash

test : model_accuracy.txt

train : intermediary.pkl

model_accuracy.txt : intermediary.pkl clean_testing_tweets.pkl shared.py test_model.py
	python2.7 test_model.py && \
	cat model_accuracy.txt && echo

intermediary.pkl : clean_training_tweets.pkl shared.py train_model.py
	python2.7 train_model.py

clean_testing_tweets.pkl : testing_tweets.csv shared.py cleaner.py
	python2.7 cleaner.py te

clean_training_tweets.pkl : training_tweets.csv shared.py cleaner.py
	python2.7 cleaner.py tr

testing_tweets.csv : credentials.py crawler.py
	python2.7 crawler.py te 

training_tweets.csv : credentials.py crawler.py
	python2.7 crawler.py tr

clean :
	rm -f *.pkl *.txt *.csv *.pyc

.PHONY : clean train test
