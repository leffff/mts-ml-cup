import torch
from torch import nn

from seq2seq_modules.layers import TrainablePositionalEncoding, PositionalEncoding, EventEncoder, AttentionPooling
from utils import generate_square_subsequent_mask


class LSTMModel(nn.Module):
    def __init__(
            self,
            cat_feature_indexes: list,
            vocab_sizes: list,
            cont_feature_indexes: list,
            encoder_hidden_dim: int,
            hidden_dim: int,
            output_dim: int,
            num_layers: int = 3,
            bias: bool = True,
            batch_first: bool = True,
            bidirectional: bool = False,
            dropout: float = 0.1,
    ):
        super().__init__()

        self.cat_feature_indexes = cat_feature_indexes
        self.vocab_sizes = vocab_sizes
        self.cont_feature_indexes = cont_feature_indexes
        self.encoder_hidden_dim = encoder_hidden_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.bias = bias
        self.batch_first = batch_first
        self.bidirectional = bidirectional
        self.dropout = dropout

        self.event_embedding = EventEncoder(
            cat_feature_indexes=self.cat_feature_indexes,
            vocab_sizes=self.vocab_sizes,
            cont_feature_indexes=self.cont_feature_indexes,
            hidden_dim=self.encoder_hidden_dim,
            output_dim=self.hidden_dim,
        )

        self.seq2seq = nn.LSTM(
            input_size=self.hidden_dim,
            hidden_size=self.hidden_dim,
            num_layers=self.num_layers,
            bias=self.bias,
            batch_first=self.batch_first,
            bidirectional=self.bidirectional,
            dropout=self.dropout,
        )

        self.out = nn.Linear(self.hidden_dim, self.output_dim)

    def forward(self, input_features: torch.Tensor, attention_mask: torch.LongTensor) -> torch.Tensor:
        event_embeddings = self.event_embedding(input_features)
        event_embeddings = event_embeddings * attention_mask.unsqueeze(2)
        x, (h, c) = self.seq2seq(event_embeddings)
        out = self.out(h[-1])

        return out


class GRUModel(nn.Module):
    def __init__(
            self,
            cat_feature_indexes: list,
            vocab_sizes: list,
            cont_feature_indexes: list,
            encoder_hidden_dim: int,
            hidden_dim: int,
            output_dim: int,
            num_layers: int = 3,
            bias: bool = True,
            batch_first: bool = True,
            bidirectional: bool = False,
            dropout: float = 0.1,
    ):
        super().__init__()

        self.cat_feature_indexes = cat_feature_indexes
        self.vocab_sizes = vocab_sizes
        self.cont_feature_indexes = cont_feature_indexes
        self.encoder_hidden_dim = encoder_hidden_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.bias = bias
        self.batch_first = batch_first
        self.bidirectional = bidirectional
        self.dropout = dropout

        self.event_embedding = EventEncoder(
            cat_feature_indexes=self.cat_feature_indexes,
            vocab_sizes=self.vocab_sizes,
            cont_feature_indexes=self.cont_feature_indexes,
            hidden_dim=self.encoder_hidden_dim,
            output_dim=self.hidden_dim,
        )

        self.seq2seq = nn.GRU(
            input_size=self.hidden_dim,
            hidden_size=self.hidden_dim,
            num_layers=self.num_layers,
            bias=self.bias,
            batch_first=self.batch_first,
            bidirectional=self.bidirectional,
            dropout=self.dropout,
        )

        self.out = nn.Linear(self.hidden_dim, self.output_dim)

    def forward(self, input_features: torch.Tensor, attention_mask: torch.LongTensor) -> torch.Tensor:
        event_embeddings = self.event_embedding(input_features)
        event_embeddings = event_embeddings * attention_mask.unsqueeze(2)
        x, h = self.seq2seq(event_embeddings)
        out = self.out(h[-1])

        return out


# class MeanBERTModel(nn.Module):
#     def __init__(
#             self,
#             cat_feature_indexes: list,
#             vocab_sizes: list,
#             cont_fe00ature_indexes: list,
#             encoder_hidden_dim: int,
#             hidden_dim: int,
#             dim_feedforward: int,
#             output_dim: int,
#             num_layers: int = 3,
#             nhead: int = 4,
#             batch_first: bool = True,
#             pe_type: str = "sinusoid",
#             max_len: int = None,
#             use_mask: bool = True,
#             use_key_padding_mask: bool = True,
#             dropout: float = 0.1,
#     ):
#         super().__init__()

#         self.cat_feature_indexes = cat_feature_indexes
#         self.vocab_sizes = vocab_sizes
#         self.cont_feature_indexes = cont_feature_indexes
#         self.encoder_hidden_dim = encoder_hidden_dim
#         self.hidden_dim = hidden_dim
#         self.dim_feedforward = dim_feedforward
#         self.output_dim = output_dim
#         self.num_layers = num_layers
#         self.nhead = nhead
#         self.pe_type = pe_type
#         self.max_len = max_len
#         self.use_mask = use_mask
#         self.use_key_padding_mask = use_key_padding_mask
#         self.batch_first = batch_first
#         self.dropout = dropout

#         self.event_embedding = EventEncoder(
#             cat_feature_indexes=self.cat_feature_indexes,
#             vocab_sizes=self.vocab_sizes,
#             cont_feature_indexes=self.cont_feature_indexes,
#             hidden_dim=self.encoder_hidden_dim,
#             output_dim=self.hidden_dim,
#         )

#         if self.pe_type == "sinusoid":
#             self.pe = PositionalEncoding(
#                 d_model=self.hidden_dim,
#                 max_len=self.max_len
#             )

#         elif self.pe_type == "trainable":
#             self.pe = TrainablePositionalEncoding(
#                 d_model=self.hidden_dim,
#                 max_len=self.max_len
#             )

#         self.seq2seq = nn.TransformerEncoder(
#             encoder_layer=nn.TransformerEncoderLayer(
#                 d_model=self.hidden_dim,
#                 nhead=self.nhead,
#                 dim_feedforward=self.dim_feedforward,
#                 batch_first=self.batch_first,
#                 dropout=self.dropout,
#                 norm_first=True,
#             ),
#             num_layers=self.num_layers
#         )

#         self.out = nn.Linear(self.hidden_dim, self.output_dim)

#     def forward(self, input_features: torch.Tensor, attention_mask: torch.LongTensor) -> torch.Tensor:
#         B, T, H = input_features.size()

#         event_embeddings = self.event_embedding(input_features)
#         event_embeddings = event_embeddings * attention_mask.unsqueeze(2)

#         if self.use_mask:
#             mask = generate_square_subsequent_mask(T).to(input_features.device)
#         else:
#             mask = None

#         if self.use_key_padding_mask:
#             key_padding_mask = attention_mask.bool()
#         else:
#             key_padding_mask = None

#         x = self.pe(event_embeddings)

#         x = self.seq2seq(
#             x,
#             mask=mask,
#             src_key_padding_mask=key_padding_mask
#         )

#         out = self.out((x * attention_mask.unsqueeze(2)).mean(dim=1))

#         return out


class StarterBERTModel(nn.Module):
    def __init__(
            self,
            cat_feature_indexes: list,
            vocab_sizes: list,
            cont_feature_indexes: list,
            encoder_hidden_dim: int,
            hidden_dim: int,
            dim_feedforward: int,
            output_dim: int,
            num_layers: int = 3,
            nhead: int = 4,
            batch_first: bool = True,
            pe_type: str = "trainable",
            use_mask: bool = False,
            max_len: int = 1024,
            use_key_padding_mask: bool = False,
            dropout: float = 0.1,
            starter: str = "rand",
    ):
        super().__init__()

        self.cat_feature_indexes = cat_feature_indexes
        self.vocab_sizes = vocab_sizes
        self.cont_feature_indexes = cont_feature_indexes
        self.encoder_hidden_dim = encoder_hidden_dim
        self.hidden_dim = hidden_dim
        self.dim_feedforward = dim_feedforward
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.nhead = nhead
        self.pe_type = pe_type
        self.use_mask = use_mask
        self.max_len = max_len
        self.use_key_padding_mask = use_key_padding_mask
        self.batch_first = batch_first
        self.dropout = dropout
        self.starter = starter

        if self.starter.lower() == 'randn':
            self.starter = torch.nn.Parameter(torch.randn(1, 1, self.hidden_dim), requires_grad=True)
        elif self.starter.lower() == 'zeros':
            self.starter = torch.nn.Parameter(torch.zeros(1, 1, self.hidden_dim), requires_grad=True)
        elif self.starter.lower() == 'ones':
            self.starter = torch.nn.Parameter(torch.ones(1, 1, self.hidden_dim), requires_grad=True)
        else:
            raise AttributeError(f'Unknown train_starter: "{self.starter}". Expected one of [randn, zeros, ones]')

        self.event_embedding = EventEncoder(
            cat_feature_indexes=self.cat_feature_indexes,
            vocab_sizes=self.vocab_sizes,
            cont_feature_indexes=self.cont_feature_indexes,
            hidden_dim=self.encoder_hidden_dim,
            output_dim=self.hidden_dim,
        )

        if self.pe_type == "sinusoid":
            self.pe = PositionalEncoding(
                d_model=self.hidden_dim,
                max_len=self.max_len
            )

        elif self.pe_type == "trainable":
            self.pe = TrainablePositionalEncoding(
                d_model=self.hidden_dim,
                max_len=self.max_len + 1
            )

        self.seq2seq = nn.TransformerEncoder(
            encoder_layer=nn.TransformerEncoderLayer(
                d_model=self.hidden_dim,
                nhead=self.nhead,
                dim_feedforward=self.dim_feedforward,
                batch_first=self.batch_first,
                dropout=self.dropout,
                norm_first=True,
            ),
            num_layers=self.num_layers
        )

        self.out = nn.Linear(self.hidden_dim, self.output_dim)

    def forward(self, input_features: torch.Tensor, attention_mask: torch.LongTensor) -> torch.Tensor:
        B, T, H = input_features.size()

        event_embeddings = self.event_embedding(input_features)
        event_embeddings = event_embeddings * attention_mask.unsqueeze(2)

        if self.use_mask:
            mask = generate_square_subsequent_mask(T + 1).to(input_features.device)
        else:
            mask = None

        if self.use_key_padding_mask:
            key_padding_mask = torch.cat([
                torch.zeros(B, 1, dtype=torch.long, device=input_features.device),
                attention_mask,
            ], dim=1).bool()
        else:
            key_padding_mask = None

        x = torch.cat([self.starter.expand(B, 1, self.hidden_dim), event_embeddings], dim=1)

        x = self.pe(x)

        x = self.seq2seq(
            x,
            mask=mask,
            src_key_padding_mask=key_padding_mask
        )

        out = self.out(x[:, 0])

        return out
    
    
class AttentionPoolingBERTModel(nn.Module):
    def __init__(
            self,
            cat_feature_indexes: list,
            vocab_sizes: list,
            cont_feature_indexes: list,
            encoder_hidden_dim: int,
            hidden_dim: int,
            dim_feedforward: int,
            output_dim: int,
            num_layers: int = 3,
            nhead: int = 4,
            batch_first: bool = True,
            pe_type: str = "trainable",
            use_mask: bool = False,
            max_len: int = 1024,
            use_key_padding_mask: bool = False,
            dropout: float = 0.1,
    ):
        super().__init__()

        self.cat_feature_indexes = cat_feature_indexes
        self.vocab_sizes = vocab_sizes
        self.cont_feature_indexes = cont_feature_indexes
        self.encoder_hidden_dim = encoder_hidden_dim
        self.hidden_dim = hidden_dim
        self.dim_feedforward = dim_feedforward
        self.output_dim = output_dim
        self.num_layers = num_layers
        self.nhead = nhead
        self.pe_type = pe_type
        self.use_mask = use_mask
        self.max_len = max_len
        self.use_key_padding_mask = use_key_padding_mask
        self.batch_first = batch_first
        self.dropout = dropout

        self.event_embedding = EventEncoder(
            cat_feature_indexes=self.cat_feature_indexes,
            vocab_sizes=self.vocab_sizes,
            cont_feature_indexes=self.cont_feature_indexes,
            hidden_dim=self.encoder_hidden_dim,
            output_dim=self.hidden_dim,
        )

        if self.pe_type == "sinusoid":
            self.pe = PositionalEncoding(
                d_model=self.hidden_dim,
                max_len=self.max_len
            )

        elif self.pe_type == "trainable":
            self.pe = TrainablePositionalEncoding(
                d_model=self.hidden_dim,
                max_len=self.max_len
            )

        self.seq2seq = nn.TransformerEncoder(
            encoder_layer=nn.TransformerEncoderLayer(
                d_model=self.hidden_dim,
                nhead=self.nhead,
                dim_feedforward=self.dim_feedforward,
                batch_first=self.batch_first,
                dropout=self.dropout,
                norm_first=True,
            ),
            num_layers=self.num_layers
        )
        
        self.attention_pooling = AttentionPooling(
            d_model=self.hidden_dim
        )

        self.out = nn.Linear(self.hidden_dim, self.output_dim)

    def forward(self, input_features: torch.Tensor, attention_mask: torch.LongTensor) -> torch.Tensor:
        B, T, H = input_features.size()

        event_embeddings = self.event_embedding(input_features)
        event_embeddings = event_embeddings * attention_mask.unsqueeze(2)

        if self.use_mask:
            mask = generate_square_subsequent_mask(T).to(input_features.device)
        else:
            mask = None

        if self.use_key_padding_mask:
            key_padding_mask = attention_mask
        else:
            key_padding_mask = None

        x = event_embeddings

        x = self.pe(x)

        x = self.seq2seq(
            x,
            mask=mask,
            src_key_padding_mask=key_padding_mask
        )
        
        pooled_x = self.attention_pooling(x, attention_mask)
        
        out = self.out(pooled_x)

        return out

# ADD: Attention LSTM
