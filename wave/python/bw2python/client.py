import datetime
import msgpack
import os
import base64
import socket
import sys
import threading
import Queue

from bwtypes import *

ENTITY_PO_NUM = (0, 0, 0, 50)

class Client(object):
    # This is run in a separate thread to listen for incoming frames
    def _readFrame(self):
        while True:
            frame = Frame.readFromSocket(self.socket)
            finished = frame.getFirstValue("finished")

            seq_num = frame.seq_num
            if frame.command == "resp":
                with self.response_handlers_lock:
                    handler = self.response_handlers.pop(seq_num, None)
                if handler is not None:
                    status = frame.getFirstValue("status")
                    reason = frame.getFirstValue("reason")
                    response = BosswaveResponse(status, reason, frame.kv_pairs,
                                                frame.routing_objects,
                                                frame.payload_objects)


                # If the operation failed, we need to clean up result handlers
                if status != "okay" or finished == "true":
                    with self.result_handlers_lock:
                        self.result_handlers.pop(seq_num, None)
                    with self.list_result_handlers_lock:
                        self.list_result_handlers.pop(seq_num, None)

                handler(response)

            elif frame.command == "rslt":
                with self.result_handlers_lock:
                    message_handler = self.result_handlers.get(seq_num)
                    if message_handler is not None and finished == "true":
                        del self.result_handlers[seq_num]
                with self.list_result_handlers_lock:
                    list_result_handler = self.list_result_handlers.get(seq_num)
                    if list_result_handler is not None and finished == "true":
                        del self.list_result_handlers[seq_num]

                if message_handler is not None:
                    from_ = frame.getFirstValue("from")
                    uri = frame.getFirstValue("uri")

                    unpack = frame.getFirstValue("unpack")
                    if unpack is not None and unpack.lower() == "false":
                        result = BosswaveResult(from_, uri, frame.kv_pairs, None, None)
                    else:
                        result = BosswaveResult(from_, uri, frame.kv_pairs,
                                                frame.routing_objects,
                                                frame.payload_objects)
                    # Place message handler and result in message queue.
                    # This allows callbacks to do bosswave actions (i.e. publish/subscribe)
                    # because they now take place from another thread.
                    self.msgq.put((message_handler, result))
                elif list_result_handler is not None:
                    child = frame.getFirstValue("child")
                    if child is not None:
                        list_result_handler(child)
                    if finished == "true":
                        list_result_handler(None)


    # thread for executing callbacks
    def _msgq_handler(self):
        while True:
            handler, item = self.msgq.get()
            handler(item)
            self.msgq.task_done()

    def __init__(self, host_name=None, port=None):
        default_host = "localhost"
        default_port = 28589
        if host_name is None and port is None:
            default_agent = os.getenv('BW2_AGENT')
            if default_agent is not None:
                tokens = default_agent.split(':')
                if len(tokens) != 2:
                    raise RuntimeError("Invalid BW2_AGENT env var: " + default_agent)
                default_host = tokens[0]
                try:
                    default_port = int(tokens[1])
                except ValueError as e:
                    raise RuntimeError("BW2_AGENT env var " + default_agent + " contains invalid port", e)
        if host_name is None:
            host_name = default_host
        if port is None:
            port = default_port

        self.host_name = host_name
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # setup message queue for handling callbacks
        self.msgq = Queue.Queue()
        msgq_worker = threading.Thread(target=self._msgq_handler)
        msgq_worker.daemon = True
        msgq_worker.start()

        self.response_handlers = {}
        self.response_handlers_lock = threading.Lock()
        self.result_handlers = {}
        self.result_handlers_lock = threading.Lock()
        self.list_result_handlers_lock = threading.Lock()
        self.list_result_handlers = {}

        self.synchronous_results = {}
        self.synchronous_results_lock = threading.Lock()
        self.synchronous_cond_vars = {}

        self.socket.connect((self.host_name, self.port))
        frame = Frame.readFromSocket(self.socket)
        if frame.command != "helo":
            self.close()
            raise RuntimeError("Received invalid Bosswave ACK")

        self.default_auto_chain = None

        self.listener_thread = threading.Thread(target=self._readFrame)
        self.listener_thread.daemon = True
        self.listener_thread.start()


    def close(self):
        self.socket.close()


    def overrideAutoChainTo(self, auto_chain):
        self.default_auto_chain = auto_chain


    @staticmethod
    def _utcToRfc3339(dt):
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


    def asyncSetEntity(self, key, response_handler):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("sete", seq_num)
        po = PayloadObject(ENTITY_PO_NUM, None, key)
        frame.addPayloadObject(po)

        def wrappedResponseHandler(response):
            self.vk = response.getFirstValue("vk")
            response_handler(response)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = wrappedResponseHandler
        frame.writeToSocket(self.socket)

    def setEntity(self, key):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("sete", seq_num)
        po = PayloadObject(ENTITY_PO_NUM, None, key)
        frame.addPayloadObject(po)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = response
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            response = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        if response.status != "okay":
            with self.result_handlers_lock:
                del self.result_handlers[seq_num]
            raise RuntimeError("Failed to set entity: " + result.reason)
        else:
            self.vk = response.getFirstValue("vk")
            return self.vk

    def asyncSetEntityFromFile(self, key_file_name, response_handler):
        with open(key_file_name,'rb') as f:
            f.read(1) # Strip leading byte
            key = f.read()
        self.asyncSetEntity(key, response_handler)

    def setEntityFromFile(self, key_file_name):
        with open(key_file_name,'rb') as f:
            f.read(1) # Strip leading byte
            key = f.read()
        return self.setEntity(key)

    def setEntityFromEnviron(self):
        return self.setEntityFromFile(os.environ['BW2_DEFAULT_ENTITY'])


    @staticmethod
    def _createSubscribeFrame(uri, primary_access_chain, expiry, expiry_delta,
                              elaborate_pac, unpack, auto_chain, routing_objects):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("subs", seq_num)
        frame.addKVPair("uri", uri)

        if primary_access_chain is not None:
            frame.addKVPair("primary_access_chain", primary_access_chain)
        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", Client._utcToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if elaborate_pac is not None:
            if elaborate_pac.lower() == "full":
                frame.addKVPair("elaborate_pac", "full")
            else:
                frame.addKVPair("elaborate_pac", "partial")
        if unpack:
            frame.addKVPair("unpack", "true")
        else:
            frame.addKVPair("unpack", "false")

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            frame.addRoutingObjects(routing_objects)

        return frame

    def asyncSubscribe(self, uri, response_handler, result_handler, primary_access_chain=None,
                       expiry=None, expiry_delta=None, elaborate_pac=None, unpack=True,
                       auto_chain=False, routing_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createSubscribeFrame(uri, primary_access_chain, expiry,
                                             expiry_delta, elaborate_pac, unpack,
                                             auto_chain, routing_objects)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def subscribe(self, uri, result_handler, primary_access_chain=None, expiry=None,
                  expiry_delta=None, elaborate_pac=None, unpack=True,
                  auto_chain=False, routing_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createSubscribeFrame(uri, primary_access_chain, expiry,
                                             expiry_delta, elaborate_pac, unpack,
                                             auto_chain, routing_objects)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = response
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = result_handler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        if result.status != "okay":
            raise RuntimeError("Failed to subscribe: " + result.reason)


    @staticmethod
    def _createPublishFrame(uri, persist, primary_access_chain, expiry, expiry_delta,
                            elaborate_pac, auto_chain, routing_objects, payload_objects):
        seq_num = Frame.generateSequenceNumber()
        if persist:
            frame = Frame("pers", seq_num)
        else:
            frame = Frame("publ", seq_num)
        frame.addKVPair("uri", uri)

        if primary_access_chain is not None:
            frame.addKVPair("primary_access_chain", primary_access_chain)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utcToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if elaborate_pac is not None:
            if elaborate_pac.lower() == "full":
                frame.addKVPair("elaborate_pac", "full")
            else:
                frame.addKVPair("elaborate_pac", "partial")

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            frame.addRoutingObjects(routing_objects)
        if payload_objects is not None:
            frame.addPayloadObjects(payload_objects)

        return frame

    def asyncPublish(self, uri, response_handler, persist=False, primary_access_chain=None,
                     expiry=None, expiry_delta=None, elaborate_pac=None, auto_chain=False,
                     routing_objects=None, payload_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createPublishFrame(uri, persist, primary_access_chain, expiry,
                                           expiry_delta, elaborate_pac, auto_chain,
                                           routing_objects, payload_objects)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        frame.writeToSocket(self.socket)

    def publish(self, uri, persist=False, primary_access_chain=None, expiry=None,
                expiry_delta=None, elaborate_pac=None, auto_chain=False,
                routing_objects=None, payload_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createPublishFrame(uri, persist, primary_access_chain, expiry,
                                           expiry_delta, elaborate_pac, auto_chain,
                                           routing_objects, payload_objects)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = response
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            response = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        if response.status != "okay":
            raise RuntimeError("Failed to publish: " + response.reason)


    @staticmethod
    def _createListFrame(uri, primary_access_chain, expiry, expiry_delta,
                         elaborate_pac, auto_chain, routing_objects):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("list", seq_num)
        frame.addKVPair("uri", uri)

        if primary_access_chain is not None:
            frame.addKVPair("primary_access_chain", primary_access_chain)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utcToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if elaborate_pac is not None:
            if elaborate_pac.lower() == "full":
                frame.addKVPair("elaborate_pac", "full")
            else:
                frame.addKVPair("elaborate_pac", "partial")

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            for ro in routing_objects:
                frame.addRoutingObject(ro)

        return frame

    def asyncList(self, uri, response_handler, list_result_handler, primary_access_chain=None,
                  expiry=None, expiry_delta=None, elaborate_pac=None, auto_chain=False,
                  routing_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createListFrame(uri, primary_access_chain, expiry, expiry_delta,
                                        elaborate_pac, auto_chain, routing_objects)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.list_result_handlers_lock:
            self.list_result_handlers[frame.seq_num] = list_result_handler
        frame.writeToSocket(self.socket)

    def list(self, uri, primary_access_chain=None, expiry=None, expiry_delta=None,
             elaborate_pac=None, auto_chain=False, routing_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createListFrame(uri, primary_access_chain, expiry, expiry_delta,
                                        elaborate_pac, auto_chain, routing_objects)

        def responseHandler(response):
            if response.status != "okay":
                with self.synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = response.reason
                    self.synchronous_cond_vars[frame.seq_num].notify()

        children = []
        def listResultHandler(child):
            if child is None:
                with self.synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = children
                    self.synchronous_cond_vars[frame.seq_num].notify()
            else:
                children.append(child)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.list_result_handlers_lock:
            self.list_result_handlers[frame.seq_num] = listResultHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        # The result will be a string if an error has occurred
        if type(result) is str:
            raise RuntimeError("List operation failed: " + result)
        else:
            return result


    @staticmethod
    def _createQueryFrame(uri, primary_access_chain, expiry, expiry_delta,
                         elaborate_pac, unpack, auto_chain, routing_objects):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("quer", seq_num)
        frame.addKVPair("uri", uri)

        if primary_access_chain is not None:
            frame.addKVPair("primary_access_chain", primary_access_chain)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utcToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if elaborate_pac is not None:
            if elaborate_pac.lower() == "full":
                frame.addKVPair("elaborate_pac", "full")
            else:
                frame.addKVPair("elaborate_pac", "partial")

        if unpack:
            frame.addKVPair("unpack", "true")
        else:
            frame.addKVPair("unpack", "false")

        if auto_chain:
            frame.addKVPair("autochain", "true")

        if routing_objects is not None:
            frame.addRoutingObjects(routing_objects)

        return frame

    def asyncQuery(self, uri, response_handler, result_handler, primary_access_chain=None,
                   expiry=None, expiry_delta=None, elaborate_pac=None, unpack=True,
                   auto_chain=False, routing_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createQueryFrame(uri, primary_access_chain, expiry,
                                         expiry_delta, elaborate_pac, unpack,
                                         auto_chain, routing_objects)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def query(self, uri, primary_access_chain=None, expiry=None, expiry_delta=None,
              elaborate_pac=None, unpack=True, auto_chain=False, routing_objects=None):
        if self.default_auto_chain is not None:
            auto_chain = self.default_auto_chain
        frame = Client._createQueryFrame(uri, primary_access_chain, expiry,
                                         expiry_delta, elaborate_pac, unpack,
                                         auto_chain, routing_objects)

        def responseHandler(response):
            if response.status != "okay":
                with self.synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = response.reason
                    self.synchronous_cond_vars[frame.seq_num].notify()

        results = []
        def resultHandler(result):
            finished = result.getFirstValue("finished")
            if finished == "true":
                with self.synchronous_results_lock:
                    self.synchronous_results[frame.seq_num] = results
                    self.synchronous_cond_vars[frame.seq_num].notify()
            else:
                results.append(result)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = resultHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        if type(result) is str:
            raise RuntimeError("Failed to query: " + result)
        else:
            return result


    @staticmethod
    def _createMakeEntityFrame(contact, comment, expiry, expiry_delta, revokers,
                               omit_creation_date):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("make", seq_num)

        if contact is not None:
            frame.addKVPair("contact", contact)
        if comment is not None:
            frame.addKVPair("comment", comment)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utfToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if revokers is not None:
            for revoker in reovkers:
                frame.addKVPair("revoker", revoker)
        if omit_creation_date:
            frame.addKVPair("omitcreationdate", "true")
        else:
            frame.addKVPair("omitcreationdate", "false")

        return frame

    def asyncMakeEntity(self, response_handler, contact=None, comment=None,
                        expiry=None, expiry_delta=None, revokers=None,
                        omit_creation_date=False):
        frame = Client._createMakeEntityFrame(contact, comment, expiry, expiry_delta,
                                              revokers, omit_creation_date)
        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        frame.writeToSocket(self.socket)

    def makeEntity(self, contact=None, comment=None, expiry=None, expiry_delta=None,
                   revokers=None, omit_creation_date=False):
        frame = Client._createMakeEntityFrame(contact, comment, expiry, expiry_delta,
                                              revokers, omit_creation_date)

        def responseHandler(response):
            if response.status == "okay":
                if len(response.payload_objects) != 1:
                    result = "Too few payload objects in response"
                else:
                    vk = response.getFirstValue("vk")
                    raw_entity = response.payload_objects[0].content
                    result = (vk, raw_entity)
            else:
                result = response.reason
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = result
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        # The result will be a string if an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result


    @staticmethod
    def _createMakeDotFrame(to, uri, ttl, is_permission, contact, comment, expiry,
                            expiry_delta, revokers, omit_creation_date,
                            access_permissions):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("makd", seq_num)
        frame.addKVPair("to", to)
        frame.addKVPair("uri", uri)

        if ttl is not None:
            frame.addKVPair("ttl", str(ttl))

        if is_permission:
            frame.addKVPair("ispermission", "true")

        if contact is not None:
            frame.addKVPair("contact", contact)
        if comment is not None:
            frame.addKVPair("comment", comment)

        if expiry is not None:
            expiry_time = datetime.utcfromtimestamp(expiry)
            frame.addKVPair("expiry", _utfToRfc3339(expiry_time))
        if expiry_delta is not None:
            frame.addKVPair("expirydelta", "{0}ms".format(expiry_delta))

        if revokers is not None:
            for revoker in reovkers:
                frame.addKVPair("revoker", revoker)

        if omit_creation_date:
            frame.addKVPair("omitcreationdate", "true")
        else:
            frame.addKVPair("omitcreationdate", "false")

        if access_permissions is not None:
            frame.addKVPair("accesspermissions", access_permissions)

        return frame

    def asyncMakeDot(self, response_handler, to, uri, ttl=None, is_permission=False,
                     contact=None, comment=None, expiry=None, expiry_delta=None,
                     revokers=None, omit_creation_date=False, access_permissions=None):
        frame = Client._createMakeDotFrame(to, ttl, is_permission, contact, comment,
                                           expiry, expiry_delta, revokers,
                                           omit_creation_date, access_permissions, uri)

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        frame.writeToSocket(self.socket)

    def makeDot(self, to, uri, ttl=None, is_permission=False, contact=None,
                comment=None, expiry=None, expiry_delta=None, revokers=None,
                omit_creation_date=False, access_permissions=None):
        frame = Client._createMakeDotFrame(to, uri, ttl, is_permission, contact, comment,
                                           expiry, expiry_delta, revokers,
                                           omit_creation_date, access_permissions)

        def responseHandler(response):
            if response.status == "okay":
                if len(response.payload_objects) != 1:
                    result = "Too few payload objects in response"
                else:
                    hash_ = response.getFirstValue("hash")
                    raw_dot = response.payload_objects[0].content
                    result = (hash_, raw_dot)
            else:
                result = response.reason
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = result
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = responseHandler
        with self.result_handlers_lock:
            self.result_handlers[frame.seq_num] = resultHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
            threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[frame.seq_num].wait()
            result = self.synchronous_results.pop(frame.seq_num)
            del self.synchronous_cond_vars[frame.seq_num]

        # Result will be a BosswaveResponse object unless an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result


    def asyncMakeChain(self, response_handler, is_permission=False,
                       unelaborate=False, dots=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("makc", seq_num)

        if is_permission:
            frame.addKVPair("ispermission", "true")

        if unelaborate:
            frame.addKVPair("unelaborate", "true")

        if dots is not None:
            for d in dots:
                frame.addKVPair("dot", d)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        frame.writeToSocket(self.socket)

    def makeChain(self, is_permission=False, unelaborate=False, dots=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("makc", seq_num)

        if is_permission:
            frame.addKVPair("ispermission", "true")

        if unelaborate:
            frame.addKVPair("unelaborate", "true")

        if dots is not None:
            for d in dots:
                frame.addKVPair("dot", d)

        def responseHandler(response):
            if response.status == "okay":
                if len(response.routing_objects) != 1:
                    result = "Too few routing objects in response"
                else:
                    hash_ = response.getFirstValue("hash")
                    result = (hash, response.routing_objects[0])
            else:
                result = response.reason
            with self.synchronous_results_lock:
                self.synchronous_results[frame.seq_num] = result
                self.synchronous_cond_vars[frame.seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[frame.seq_num] = response_handler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[frame.seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while frame.seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            result = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        # Result is a BosswaveResultObject unless an error has occurred
        if type(result) is str:
            raise RuntimeError(result)
        else:
            return result


    def asnycMakeView(self, view, response_handler, view_change_handler=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("mkvw", seq_num)

        view_mp = msgpack.packb(view)
        frame.addKVPair("msgpack", view_mp)

        # Bit of a hack: Call view_change_handler upon result
        def resultHandler(result):
            view_change_handler()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        frame.writeToSocket(self.socket)

        if view_change_handler is not None:
            with self.result_handlers_lock:
                self.result_handlers[seq_num] = resultHandler

    def makeView(self, view, view_change_handler=None):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("mkvw", seq_num)

        view_mp = msgpack.packb(view)
        frame.addKVPair("msgpack", view_mp)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = response
                self.synchronous_cond_vars[seq_num].notify()

        # Bit of a hack: Call view_change_handler upon result
        def resultHandler(result):
            view_change_handler()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        if view_change_handler is not None:
            with self.result_handlers_lock:
                self.result_handlers[seq_num] = resultHandler

        with self.synchronous_results_lock:
            while seq_num not in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            response = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        if response.status != "okay":
            raise RuntimeError("Failed to make view: " + response.reason)
        else:
            return int(response.getFirstValue("id"))


    def asyncViewSubscribe(self, interface_name, response_handler, result_handler,
                           signal=None, slot=None):
        if signal is None and slot is None:
            raise ValueError("View subscription must specify a signal or slot")

        seq_num = Frame.generateSequenceNumber()
        frame = Frame("vsub", seq_num)
        frame.addKVPair("interface", interface_name)
        if signal is not None:
            frame.addKVPair("signal", signal)
        else:
            frame.addKVPair("slot", slot)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        frame.writeToSocket(self.socket)

    def viewSubscribe(self, interface_name, result_handler, signal=None, slot=None):
        if signal is None and slot is None:
            raise ValueError("View subscription must specify a signal or slot")

        seq_num = Frame.generateSequenceNumber()
        frame = Frame("vsub", seq_num)
        frame.addKVPair("interface", interface_name)
        if signal is not None:
            frame.addKVPair("signal", signal)
        else:
            frame.addKVPair("slot", slot)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = response
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.result_handlers_lock:
            self.result_handlers[seq_num] = result_handler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while not seq_num in self.symchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            response = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        if response.status != "okay":
            raise RuntimeError("View subscribe failed: " + response.reason)


    def asyncViewPublish(self, interface_name, response_handler, payload_objects,
                         signal=None, slot=None):
        if signal is None and slot is None:
            raise ValueError("View publish must specify a signal or slot")

        seq_num = Frame.generateSequenceNumber()
        frame = Frame("vpub", seq_num)
        frame.addKVPair("interface", interface_name)
        if signal is not None:
            frame.addKVPair("signal", signal)
        else:
            frame.addKVPair("slot", slot)
        frame.addPayloadObjects(payload_objects)

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = response_handler
        frame.writeToSocket(self.socket)

    def viewPublish(self, interface_name, payload_objects, signal=None, slot=None):
        if signal is None and slot is NOne:
            raise ValueError("View publish must specify a signal or slot")

        seq_num = Frame.generateSequenceNumber()
        frame = Frame("vpub", seq_num)
        frame.addKVPair("interface", interface_name)
        if signal is not None:
            frame.addKVPair("signal", signal)
        else:
            frame.addKVPair("slot", slot)
        frame.addPayloadObjects(payload_objects)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = response
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while not seq_num in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            result = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        if result.status != "okay":
            raise RuntimeError("View publish failed: " + result.reason)

    def resolveAlias(self, alias):
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("resa", seq_num)
        frame.addKVPair("longkey", alias)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = response
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while not seq_num in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            result = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        if result.status != "okay":
            raise RuntimeError("Resolve failed: " + result.reason)
        val = result.getFirstValue("value")
        if val is not None:
            return base64.urlsafe_b64encode(str(val))
        else:
            return None

    def unresolveAlias(self, b64_blob):
        blob = base64.urlsafe_b64decode(b64_blob)
        seq_num = Frame.generateSequenceNumber()
        frame = Frame("resa", seq_num)
        frame.addKVPair("unresolve", blob)

        def responseHandler(response):
            with self.synchronous_results_lock:
                self.synchronous_results[seq_num] = response
                self.synchronous_cond_vars[seq_num].notify()

        with self.response_handlers_lock:
            self.response_handlers[seq_num] = responseHandler
        with self.synchronous_results_lock:
            self.synchronous_cond_vars[seq_num] = \
                    threading.Condition(self.synchronous_results_lock)
        frame.writeToSocket(self.socket)

        with self.synchronous_results_lock:
            while not seq_num in self.synchronous_results:
                self.synchronous_cond_vars[seq_num].wait()
            result = self.synchronous_results.pop(seq_num)
            del self.synchronous_cond_vars[seq_num]

        if result.status != "okay":
            raise RuntimeError("Unresolve failed: " + result.reason)
        return result.getFirstValue("value")
