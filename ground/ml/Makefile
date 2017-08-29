SHELL :=/bin/bash

test : model_accuracy.txt

train : intermediary.pkl

model_accuracy.txt : intermediary.pkl clean_testing_tweets.pkl shared.py test_model.py
	python test_model.py && \
	cat model_accuracy.txt && echo

intermediary.pkl : clean_training_tweets.pkl shared.py train_model.py
	python train_model.py

clean_testing_tweets.pkl : testing_tweets.csv shared.py cleaner.py
	python cleaner.py te

clean_training_tweets.pkl : training_tweets.csv shared.py cleaner.py
	python cleaner.py tr

testing_tweets.csv : credentials.py crawler.py
	python crawler.py te 

training_tweets.csv : credentials.py crawler.py
	python crawler.py tr

clean :
	rm -f *.pkl *.txt *.csv *.pyc

.PHONY : clean train test
