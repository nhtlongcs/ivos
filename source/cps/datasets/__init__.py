from .twosampler import TwoStreamBatchSampler
from .twostreamloader import TwoStreamDataLoader
from source.semantic2D.datasets import DATASET_REGISTRY, DATALOADER_REGISTRY

DATALOADER_REGISTRY.register(TwoStreamBatchSampler)
DATALOADER_REGISTRY.register(TwoStreamDataLoader)