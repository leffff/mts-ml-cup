import pandas as pd
import numpy as np
from tests import torch
from tqdm import tqdm


class Preprocessor:
    def __init__(self, agg_column: str, time_column: str, max_len: int):
        self.agg_column = agg_column
        self.time_column = time_column
        self.max_len = max_len

    def get_sequences(self, dataset: pd.DataFrame) -> list:
        dataset = dataset.sort_values(
            by=[self.agg_column, self.time_column], ascending=[True, True]
        )

        sequences = []
        agg_col = dataset[self.agg_column].to_numpy()
        dataset = dataset.to_numpy()

        curr_ind = 0
        curr_val = agg_col[0]
        for i in tqdm(range(curr_val.shape[0])):
            if agg_col[i] != curr_val:
                sequences.append(dataset[curr_ind:i])

                curr_ind = i
                curr_val = agg_col[i]

        return sequences

    def to_tensor(self, sequences: list) -> list:
        return [torch.tensor(sequence) for sequence in tqdm(sequences)]

    def pad_and_truncate(self, sequences: list) -> list:
        attention_masks = []

        for i in tqdm(range(len(sequences))):
            if sequences[i].shape[0] < self.max_len:
                sequences[i] = np.concatenate(
                    [
                        np.zeros(
                            (
                                self.max_len - sequences[i].shape[0],
                                sequences[i].shape[1],
                            )
                        ),
                        sequences[i],
                    ],
                    axis=0,
                )
                attention_masks.append(
                    np.concatenate(
                        [
                            np.zeros((self.max_len - sequences[i].shape[0])),
                            np.ones((sequences[i].shape[0])),
                        ],
                        axis=0,
                    )
                )
            elif sequences[i].shape[0] > self.max_len:
                sequences[i] = sequences[i][-(self.max_len - 1) :]
                attention_masks.append(np.ones((sequences[i].shape[0])))

        return sequences

    def transform(self, dataset: pd.DataFrame) -> list:
        sequences = self.get_sequences(dataset)
        sequences = self.pad_and_truncate(sequences)
        sequences = self.to_tensor(sequences)

        return sequences