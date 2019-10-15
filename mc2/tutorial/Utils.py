from pymongo import MongoClient
from os.path import expanduser
import subprocess
import sys
import xgboost as xgb
from numpy import genfromtxt
import logging
import pickle
import pandas as pd

db_username = "xgboost"
db_password = "risecampmc2"


class PKI:
    def __init__(self):
        self.client = MongoClient(
            'mongodb://%s:%s@54.202.14.46:27017/PKI' % (db_username, db_password))
        self.db = self.client['PKI']


    def upload(self, username, IP, pubkey):
        try:
            collection = self.db.posts
            query = \
                {
                    'user': username
                }
            doc = \
                {
                    'user': username,
                    'IP': IP,
                    'key': pubkey
                }
            result = collection.find_one_and_replace(query, doc, upsert=True)
            print('Uploaded information:')
            print('\tUsername: %s' % username)
            print('\tIP: %s' % IP)
            print('\tPublic key: %s...' % pubkey[8:18])
        except Exception as e:
            print(str(e))


    def lookup(self, username):
        try:
            posts = self.db.posts
            query = {
                'user': username
            }
            result = posts.find_one(query)
            if result == None:
                print("No information found for user %s" % username)
                return None, None
            else:
                print('Retrieved information for user %s:' % username)
                print('\tIP: %s' % result['IP'])
                print('\tPublic key: %s...' % result['key'][8:18])
                return result['IP'], result['key']
        except Exception as e:
            print(str(e))


    def save_key(self, username):
        try:
            IP, key = self.lookup(username)
            if key == None:
                return False
            home = expanduser("~")
            with open(home + "/.ssh/authorized_keys", "a") as authorized_keys:
                authorized_keys.write("%s\n" % key)
                print("Saved key for user %s" % username)
            return True
        except Exception as e:
            print(str(e))


class Federation:
    def __init__(self):
        self.client = MongoClient(
            'mongodb://%s:%s@54.202.14.46:27017/Federations' % (db_username, db_password))
        self.db = self.client['Federations']
        self.username = None
        self.aggregator = None


    def check_federation(self):
        if self.aggregator is None:
            print("No federation to check. Please create or join a federation first.")
            return False

        try:
            collection = self.db.federations
            query = \
                {
                    'master': self.aggregator,
                }
            result = collection.find_one(query)
            if result == None:
                print("No such federation exists")
                return False

            members_list = result['members']
            members = []
            for member in members_list:
                members.append(member['member'])

            print("Federation members: %s" % members)

            collection = self.db.members
            for member in members:
                query = \
                    {
                        'member': member,
                        'federation': self.aggregator
                    }
                if collection.count_documents(query, limit=1) == 0:
                    print("User %s has not joined the federation" % member)
                    return False
            print("All users have joined the federation")
            return True
        except Exception as e:
            print(str(e))
            return False


    def get_federation_members(self, aggregator_name):
        try:
            collection = self.db.federations
            query = \
                {
                    'master': aggregator_name
                }
            result = collection.find_one(query)
            if (result == None):
                print("No federation found")
                return None

            members_list = result['members']
            members = []
            for member in members_list:
                members.append(member['member'])

            return members

        except Exception as e:
            print(str(e))
            return None


    def get_federation_member_id(self, aggregator_name, member_name):
        try:
            collection = self.db.federations
            query = \
                {
                    'master': aggregator_name
                }
            result = collection.find_one(query)
            if (result == None):
                print("No federation found")
                return None

            members_list = result['members']
            print(members_list)
            for member in members_list:
                if member['member'] == member_name:
                    return member['m_id']

            return None

        except Exception as e:
            print(str(e))
            return None


class FederationAggregator(Federation):
    def __init__(self, username):
        Federation.__init__(self)
        self.username = username
        self.aggregator = username


    def create_federation(self, members):
        try:
            if self.username not in members:
                members.append(self.username)

            members_list = []
            id_ctr = 2;
            for member in members:
                if member == self.username:
                    m_id = 1
                    members_list.append({'member': member, 'm_id': m_id})
                else:
                    m_id = id_ctr
                    members_list.append({'member': member, 'm_id': m_id})
                    id_ctr = id_ctr + 1

            collection = self.db.federations
            query = \
                {
                    'master': self.username
                }
            doc = \
                {
                    'master': self.username,
                    'members': members_list
                }
            result = collection.find_one_and_replace(query, doc, upsert=True)

            collection = self.db.members
            query = \
                {
                    'member': self.username
                }
            doc = \
                {
                    'member': self.username,
                    'federation': self.username,
                    'role': 'master'
                }
            result = collection.find_one_and_replace(query, doc, upsert=True)

            print('Successfully created federation:')
            print('\tAggregator: %s' % self.username)
            print('\tMembers: %s' % members)
        except Exception as e:
            print(str(e))


    def save_members_info(self):
        if self.aggregator is None:
            print("No federation to save. Please create or join a federation first.")
            return
        try:
            pki = PKI()

            collection = self.db.federations
            query = \
                {
                    'master': self.aggregator,
                }
            result = collection.find_one(query)
            if result == None:
                print("No such federation exists")
                return

            members_list = result['members']
            members = []
            for member in members_list:
                members.append(member['member'])
            print("Federation members: %s" % members)

            collection = self.db.members
            for member in members:
                # if (member == self.username):
                #    continue
                result = pki.save_key(member)
                if (result == False):
                    print("ERROR saving information")
                    return
            print("Members' information saved")
            return
        except Exception as e:
            print(str(e))



class FederationMember(Federation):
    def __init__(self, username):
        Federation.__init__(self)
        self.username = username

    def join_federation(self, master_username):
        try:

            collection = self.db.federations
            query = \
                {
                    'master': master_username,
                }
            result = collection.find_one(query)
            if result == None:
                print("No such federation exists.")
                return

            members_list = result['members']
            members = []
            for member in members_list:
                members.append(member['member'])
            if self.username not in members:
                print("The central aggregator hasn't added you as a member to the federation.")

            self.aggregator = master_username

            collection = self.db.members
            query = \
                {
                    'member': self.username
                }
            doc = \
                {
                    'member': self.username,
                    'federation': master_username,
                    'role': 'worker'
                }
            result = collection.find_one_and_replace(query, doc, upsert=True)

            print('Successfully joined federation created by %s' % master_username)

        except Exception as e:
            print(str(e))


    def save_aggregator_info(self):
        if self.aggregator is None:
            print("No federation to save. Please create or join a federation first.")
            return
        try:
            pki = PKI()

            collection = self.db.members
            result = pki.save_key(self.aggregator)
            if (result == True):
                print("Aggregator information saved")
            else:
                print("ERROR saving information")
            return
        except Exception as e:
            print(str(e))

class FederatedXGBoost:
    def __init__(self):
        xgb.rabit.init()
        self.dtrain = None
        self.dtest = None
        self.model = None

    def load_training_data(self, training_data_path):
        training_data_path = training_data_path[:-4] + \
            "_" + str(xgb.rabit.get_rank() + 1) + ".csv"
        training_data = genfromtxt(training_data_path, delimiter=',')
        self.dtrain = xgb.DMatrix(
            training_data[:, 1:], label=training_data[:, 0])

    def load_test_data(self, test_data_path):
        test_data_path = test_data_path[:-4] + \
            "_" + str(xgb.rabit.get_rank() + 1) + ".csv"
        test_data = genfromtxt(test_data_path, delimiter=',')
        self.dtest = xgb.DMatrix(test_data[:, 1:], label=test_data[:, 0])

    def train(self, params, num_rounds):
        if self.dtrain == None:
            print("Training data not yet loaded")
        self.model = xgb.train(params, self.dtrain, num_rounds)

    def predict(self):
        if self.dtest == None:
            print("Test data not yet loaded")
        return self.model.predict(self.dtest)

    def eval(self):
        if self.dtest == None:
            print("Test data not yet loaded")
        return self.model.eval(self.dtest)

    def get_num_parties(self):
        return xgb.rabit.get_world_size()

    def load_model(self, model_path):
        self.model = xgb.Booster()
        self.model.load_model(model_path)

    def save_model(self, model_name):
        self.model.save_model(model_name)
        print("Saved model to {}".format(model_name))

    def shutdown(self):
        print("Shutting down tracker")
        xgb.rabit.finalize()


def start_job(num_parties):
    # Check if training_job is already running on each machine; if so kill it
    with open("hosts.config") as f:
        tmp = f.readlines()
    for h in tmp:
        if len(h.strip()) > 0:
            # parse addresses of the form ip:port
            h = h.strip()
            i = h.find(":")
            p = "22"
            if i != -1:
                p = h[i+1:]
                h = h[:i]
           
            kill_cmd = "kill -9 $(ps aux | awk '$12 $28 ~ \"train_model.py\" {print $2}')"
            ssh_kill_cmd = ["ssh", "-o", "StrictHostKeyChecking=no", str(h), "-p", str(p), kill_cmd]
           
            process = subprocess.Popen(
                ssh_kill_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    cmd = ["../dmlc-core/tracker/dmlc-submit", "--cluster", "ssh", "--num-workers",
           str(num_parties), "--host-file", "hosts.config", "--worker-memory", "4g", "/opt/conda/bin/python3", "/home/$USER/train_model.py"]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in iter(process.stdout.readline, b''):
        line = line.decode("utf-8")
        if line[:4] == "2019":
            sys.stdout.write(line)



