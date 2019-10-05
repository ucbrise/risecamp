from typing import Any, Dict, Collection

from atlas.models.tensorflow.graphs.operators import SelectGGNN, SelectFixedGGNN, OrderedSubsetGGNN
from atlas.operators import OpInfo
from atlas.synthesis.pandas.encoders import PandasGraphEncoder
from atlas.tracing import OpTrace


class PivotSelectModel(SelectGGNN):
    def __init__(self, params: Dict[str, Any], debug: bool = False):
        self.encoder = PandasGraphEncoder()
        params.update({
            'num_node_features': self.encoder.get_num_node_features(),
            'num_edge_types': self.encoder.get_num_edge_types()
        })

        self.debug = debug
        super().__init__(params)

    def encode_context(self, context):
        return {'I': context[0], 'O': context[1]}

    def encode_op(self, op: OpTrace):
        c = self.encode_context(op.context)
        return self.encoder.Select(domain=op.domain,
                                   context=c,
                                   choice=op.choice,
                                   op_info=op.op_info)

    def train(self, training_data: Collection[OpTrace], validation_data: Collection[OpTrace], *args, **kwargs):
        encoded_train = [self.encode_op(op) for op in training_data]
        encoded_valid = [self.encode_op(op) for op in validation_data]
        super().train(encoded_train, encoded_valid, *args, **kwargs)

    def infer(self, domain, context: Any = None, op_info: OpInfo = None, **kwargs):
        encoding = self.encoder.Select(domain, self.encode_context(context), mode='inference', op_info=op_info)
        inference = super().infer([encoding])[0]
        if self.debug:
            print(f"Inference for operator {op_info.sid}")
            print(sorted(inference, key=lambda x: -x[1]))

        return [val for val, prob in sorted(inference, key=lambda x: -x[1])]


class PivotClassifyModel(SelectFixedGGNN):
    def __init__(self, params: Dict[str, Any], domain_size: int, debug: bool = False):
        self.encoder = PandasGraphEncoder()
        params.update({
            'num_node_features': self.encoder.get_num_node_features(),
            'num_edge_types': self.encoder.get_num_edge_types(),
            'domain_size': domain_size
        })

        self.debug = debug
        super().__init__(params)

    def encode_context(self, context):
        return {'I': context[0], 'O': context[1]}

    def encode_op(self, op: OpTrace):
        c = self.encode_context(op.context)
        return self.encoder.SelectFixed(domain=op.domain,
                                        context=c,
                                        choice=op.choice,
                                        op_info=op.op_info)

    def train(self, training_data: Collection[OpTrace], validation_data: Collection[OpTrace], *args, **kwargs):
        encoded_train = [self.encode_op(op) for op in training_data]
        encoded_valid = [self.encode_op(op) for op in validation_data]
        super().train(encoded_train, encoded_valid, *args, **kwargs)

    def infer(self, domain, context: Any = None, op_info: OpInfo = None, **kwargs):
        encoding = self.encoder.SelectFixed(domain, self.encode_context(context), mode='inference', op_info=op_info)
        inference = super().infer([encoding])[0]
        if self.debug:
            print(f"Inference for operator {op_info.sid}")
            print(sorted(inference, key=lambda x: -x[1]))

        return [val for val, prob in sorted(inference, key=lambda x: -x[1])]


class PivotOrderedSubsetModel(OrderedSubsetGGNN):
    def __init__(self, params: Dict[str, Any], debug: bool = False):
        self.encoder = PandasGraphEncoder()
        params.update({
            'num_node_features': self.encoder.get_num_node_features(),
            'num_edge_types': self.encoder.get_num_edge_types()
        })

        self.debug = debug
        super().__init__(params)

    def encode_context(self, context):
        return {'I': context[0], 'O': context[1]}

    def encode_op(self, op: OpTrace):
        c = self.encode_context(op.context)
        return self.encoder.OrderedSubset(domain=op.domain,
                                          context=c,
                                          choice=op.choice,
                                          op_info=op.op_info)

    def train(self, training_data: Collection[OpTrace], validation_data: Collection[OpTrace], *args, **kwargs):
        encoded_train = [self.encode_op(op) for op in training_data]
        encoded_valid = [self.encode_op(op) for op in validation_data]
        super().train(encoded_train, encoded_valid, *args, **kwargs)

    def infer(self, domain, context: Any = None, op_info: OpInfo = None, **kwargs):
        encoding = self.encoder.OrderedSubset(domain, self.encode_context(context), mode='inference', op_info=op_info)
        inference = super().infer([encoding], top_k=100)[0]
        if self.debug:
            print(f"Inference for operator {op_info.sid}")
            print(sorted(inference, key=lambda x: -x[1]))

        return [val for val, prob in sorted(inference, key=lambda x: -x[1])]
