from typing import List, Dict
from theseus.base.callbacks.base_callbacks import Callbacks
from theseus.utilities.loggers.observer import LoggerObserver

LOGGER = LoggerObserver.getLogger("main")

class STCNCallbacks(Callbacks):
    """
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.skip_values = [10, 15, 20, 25, 5]
        self.increase_skip_fraction = [0.1, 0.2, 0.3, 0.4, 0.9, 1.0]

    def on_start(self, logs:Dict = None):
        
        train_dataloader = self.params['trainer'].trainloader
        self.num_iterations = self.params['trainer'].num_iterations
        self.total_epoch = self.num_iterations // len(train_dataloader)
        self.increase_skip_epoch = [
            round(self.num_iterations*f) for f in self.increase_skip_fraction]

    def on_epoch_start(self, logs:Dict = None):

        iters = logs['iters']
        train_dataloader = self.params['trainer'].trainloader
        current_epoch = iters // len(train_dataloader)

        if current_epoch!=self.total_epoch and current_epoch>=self.increase_skip_epoch[0]:
            while current_epoch >= self.increase_skip_epoch[0]:
                cur_skip = self.skip_values[0]
                self.skip_values = self.skip_values[1:]
                self.increase_skip_epoch = self.increase_skip_epoch[1:]
            print('Increasing skip to: ', cur_skip)
            self.renew_loader(cur_skip)

    def renew_loader(self, max_skip: int):
        # //5 because we only have annotation for every five frames
        self.params['trainer'].trainloader.dataset.max_jump = max_skip
        self.params['trainer'].valloader.dataset.max_jump = max_skip
        LOGGER.text(f'Renewed with skip: {max_skip}', level=LoggerObserver.INFO)