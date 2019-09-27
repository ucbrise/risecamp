import collections
import itertools
from abc import ABC, abstractmethod

import torch
import torch_geometric
import torch.nn.functional as F
from atlas.models.pytorch.imitation import PyTorchGeneratorSharedStateModel, PyTorchOpModel
from atlas.operators import operator
from torch_geometric.data import DataLoader, Data, Batch
from torch_geometric.nn import GatedGraphConv, global_mean_pool, global_add_pool
from torch_geometric.utils.num_nodes import maybe_num_nodes
from torch_scatter import scatter_max, scatter_add, scatter_mul
from typing import List, Union


def softmax(src, index, num_nodes=None):
    r"""Computes a sparsely evaluated softmax along with its log in a numerically stable way.
    Given a value tensor :attr:`src`, this function first groups the values
    along the first dimension based on the indices specified in :attr:`index`,
    and then proceeds to compute the softmax individually for each group.

    Args:
        src (Tensor): The source tensor.
        index (LongTensor): The indices of elements for applying the softmax.
        num_nodes (int, optional): The number of nodes, *i.e.*
            :obj:`max_val + 1` of :attr:`index`. (default: :obj:`None`)

    :rtype: :class:`Tensor`
    """

    num_nodes = maybe_num_nodes(index, num_nodes)

    shifted = src - scatter_max(src, index, dim=0, dim_size=num_nodes)[0][index]
    exp_shifted = shifted.exp()
    exp_sum = scatter_add(exp_shifted, index, dim=0, dim_size=num_nodes)[index]
    scores = exp_shifted / (exp_sum + 1e-16)

    return scores, shifted - (exp_sum + 1e-16).log()


class GraphModel(torch.nn.Module):
    def __init__(self, node_dim: int, num_convs: int, num_layers: Union[int, List[int]], num_edge_types: int):
        super().__init__()
        self.convs = []
        if isinstance(num_layers, int):
            num_layers = [num_layers] * num_convs

        for i in range(num_convs):
            self.convs.append(GatedGraphConv(node_dim, num_layers=1))

        #  Weight given to each edge type
        self.edge_type_weights = torch.nn.Parameter(torch.FloatTensor((1.0,) * num_edge_types))

        #  Simple linear layer for the output of conv3
        self.lin1 = torch.nn.Linear(node_dim, node_dim)

        #  Slope for leaky relus
        self.neg_slope = 0.01

    def forward(self, data):
        #  x := Node embeddings (1-D flattened array with nodes of all graphs in batch)
        #  edge_index := adjacency list
        #  batch := 1-D array containing the graph-id of each node
        x, edge_index, batch, edge_attr = data.x, data.edge_index, data.batch, data.edge_attr
        edge_weights = self.edge_type_weights[edge_attr]

        #  Start message passing
        for conv in self.convs:
            x = F.leaky_relu(conv(x, edge_index, edge_weights), negative_slope=self.neg_slope)

        x = F.leaky_relu(self.lin1(x), negative_slope=self.neg_slope)
        return x


def encode_strings_as_graphs(strlist):
    nodes = []
    adjacency_edges = []
    equality_edges = []

    equality_maps = []
    for idx, s in enumerate(strlist):
        embedding = [0] * len(strlist)
        embedding[idx] = 1
        new_nodes = [embedding + [int(c.isalpha())] for c in s]
        for i in range(len(nodes), len(nodes) + len(s) - 1):
            adjacency_edges.append([i, i + 1])

        eq_map = collections.defaultdict(list)
        for n_idx, c in enumerate(s, len(nodes)):
            eq_map[c].append(n_idx)

        nodes.extend(new_nodes)
        equality_maps.append(eq_map)

    for m1 in equality_maps:
        for m2 in equality_maps:
            if m1 is m2:
                continue

            for k, v in m1.items():
                equality_edges.extend([[i, j] for i in v for j in m2[k]])

    return nodes, adjacency_edges, equality_edges


class SubstrModel(PyTorchOpModel):
    def __init__(self, node_dim: int):
        super().__init__()
        self.graph_model = GraphModel(node_dim, num_convs=3, num_layers=1, num_edge_types=2)
        #  Linear layer to account for state
        self.lin2 = torch.nn.Linear(2 * node_dim, node_dim)
        #  Attention score to find start index of the substr
        self.lin_start = torch.nn.Linear(2 * node_dim, 1)
        #  Attention score to find end index of the substr
        self.lin_end = torch.nn.Linear(2 * node_dim, 1)
        #  Linear layer for new state
        self.lin_state = torch.nn.Linear(2 * node_dim, node_dim)

        self.top_k = 10

        #  Slope for leaky relus
        self.neg_slope = 0.01

    def encode(self, data):
        return Batch.from_data_list([self.encode_point(p) for p in data])

    def infer(self, domain, context, state=None):
        batch = self.encode([(domain, context, None)])
        self.eval()
        with torch.no_grad():
            result = self(batch, state=state, mode="infer")

            cands = []
            start_cands = sorted([(i, idx) for idx, i in enumerate(result[0][:len(domain)])], key=lambda x: -x[0])[:self.top_k]
            for s_prob, s in start_cands:
                end_cands = sorted([(i, idx) for idx, i in enumerate(result[1][:len(domain)]) if idx >= s],
                                   key=lambda x: -x[0])[:self.top_k]
                cands.extend([(s_prob * e_prob, s, e) for e_prob, e in end_cands])

            cands = sorted(cands, key=lambda x: -x[0])[:self.top_k]
            return [domain[s: e + 1] for _, s, e in cands], result[2]

    def encode_point(self, point):
        domain, (inp, out), choice = point
        x, adjacency_edges, equality_edges = encode_strings_as_graphs([domain, inp, out])
        x = torch.tensor(x, dtype=torch.float)

        edges = torch.tensor(adjacency_edges + equality_edges, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor([0 for _ in adjacency_edges] + [1 for _ in equality_edges], dtype=torch.long)

        if choice is None:
            return Data(x=x, edge_index=edges, edge_attr=edge_attr)
        else:
            if choice not in domain:
                raise ValueError("Could not find label inside domain")

            y = [[0, 0] for _ in range(x.shape[0])]
            idx = domain.find(choice)
            y[idx][0] = 1
            y[idx + len(choice) - 1][1] = 1
            return Data(x=x, edge_index=edges, edge_attr=edge_attr, y=torch.tensor(y, dtype=torch.long))

    def forward(self, data, state=None, mode='train/test'):
        #  x := Node embeddings (1-D flattened array with nodes of all graphs in batch)
        #  edge_index := adjacency list
        #  batch := 1-D array containing the graph-id of each node
        x, edge_index, batch = data.x, data.edge_index, data.batch
        x = self.graph_model(data)

        graph_pooled = global_mean_pool(x, batch)
        processed = self.lin2(torch.cat([graph_pooled, state], dim=1))
        x_cat = torch.cat([x, processed[batch]], dim=1)
        scores_start = F.leaky_relu(self.lin_start(x_cat), negative_slope=self.neg_slope).view(-1)
        scores_end = F.leaky_relu(self.lin_end(x_cat), negative_slope=self.neg_slope).view(-1)

        attn_start, log_attn_start = softmax(scores_start, batch)
        attn_end, log_attn_end = softmax(scores_end, batch)
        state = F.leaky_relu(self.lin_state(torch.cat([processed, state], dim=1)), negative_slope=self.neg_slope)

        if mode == 'train/test':
            labels_start = data.y[:, 0]
            labels_end = data.y[:, 1]
            loss_start = -(log_attn_start * labels_start.type(torch.float)).mean()
            loss_end = -(log_attn_end * labels_end.type(torch.float)).mean()
            loss = loss_start + loss_end

            max_scores_start = scatter_max(scores_start, batch)[0][batch]
            max_scores_end = scatter_max(scores_end, batch)[0][batch]
            selected_start = max_scores_start.eq(scores_start).type(torch.long)
            selected_end = max_scores_end.eq(scores_end).type(torch.long)
            correct_start = scatter_mul(selected_start.eq(labels_start).type(torch.float), batch)
            correct_end = scatter_mul(selected_end.eq(labels_end).type(torch.float), batch)
            correct = (correct_start * correct_end)

            return loss, correct, state

        elif mode == 'infer':
            return attn_start, attn_end, state


class SelectFuncModel(PyTorchOpModel):
    def __init__(self, node_dim: int, num_classes: int):
        super().__init__()
        self.graph_model = GraphModel(node_dim, num_convs=3, num_layers=1, num_edge_types=2)

        #  Softmax linear layer
        self.lin2 = torch.nn.Linear(node_dim * 2, num_classes)

        #  Linear layer to compute next state
        self.lin_state = torch.nn.Linear(node_dim * 2, node_dim)

        #  Slope for leaky relus
        self.neg_slope = 0.01

    def encode(self, data):
        return Batch.from_data_list([self.encode_point(p) for p in data])

    def infer(self, domain, context, state=None):
        batch = self.encode([(domain, context, None)])
        self.eval()
        with torch.no_grad():
            result = self(batch, state=state, mode="infer")
            preds = result[0][0]
            cands = [(i, idx) for idx, i in enumerate(preds)]
            cands = sorted(cands, key=lambda x: -x[0])
            cands = [domain[i] for _, i in cands]
            return cands, result[1]

    def encode_point(self, point):
        domain, (inp, out), choice = point
        x, adjacency_edges, equality_edges = encode_strings_as_graphs([domain, inp, out])
        x = torch.tensor(x, dtype=torch.float)
        edges = torch.tensor(adjacency_edges + equality_edges, dtype=torch.long).t().contiguous()
        edge_attr = torch.tensor([0 for _ in adjacency_edges] + [1 for _ in equality_edges], dtype=torch.long)

        if choice is None:
            return Data(x=x, edge_index=edges, edge_attr=edge_attr)
        else:
            if choice not in domain:
                raise ValueError("Could not find label inside domain")

            y = [domain.index(choice)]
            return Data(x=x, edge_index=edges, edge_attr=edge_attr, y=torch.tensor(y, dtype=torch.long))

    def forward(self, data, state=None, mode='train/test'):
        #  x := Node embeddings (1-D flattened array with nodes of all graphs in batch)
        #  edge_index := adjacency list
        #  batch := 1-D array containing the graph-id of each node
        x, edge_index, batch = data.x, data.edge_index, data.batch
        x = self.graph_model(data)

        graph_pooled = global_mean_pool(x, batch)
        x_cat = torch.cat([graph_pooled, state], dim=1)
        x = F.leaky_relu(self.lin2(x_cat), negative_slope=self.neg_slope)
        state = F.leaky_relu(self.lin_state(x_cat), negative_slope=self.neg_slope)

        if mode == 'train/test':
            loss = F.nll_loss(F.log_softmax(x, dim=1), data.y)
            _, preds = F.softmax(x, dim=1).max(1)
            return loss, preds.eq(data.y).type(torch.float), state

        elif mode == 'infer':
            return F.softmax(x, dim=1), state
