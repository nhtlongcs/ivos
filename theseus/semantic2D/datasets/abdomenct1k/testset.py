import os.path as osp
import nibabel as nib # common way of importing nibabel
import torch
import numpy as np
import os
import os.path as osp
from theseus.semantic2D.datasets.abdomenct1k import AbdomenCT1KBaseDataset
from theseus.utilities.loggers.observer import LoggerObserver

LOGGER = LoggerObserver.getLogger('main')

class AbdomenCT1KTestDataset(AbdomenCT1KBaseDataset):
    def __init__(
        self, 
        root_dir: str,
        max_ref_frames: int = 15,
        transform=None,
        **kwargs):
        
        super().__init(root_dir, transform)
        self.max_ref_frames = max_ref_frames
        self.load_data()

    def load_data(self):
        volume_names = sorted(os.listdir(self.root_dir))
        self.fns = []
        for volume_name in volume_names:
            # train_0047_0000.nii.gz
            pid = volume_name.split('_')[1] 
            self.fns.append({
                'pid': pid,
                'vol': volume_name,
            })
        
    def sampling_frames(self, num_frames):
        if self.max_frames == -1:
            self.max_frames = num_frames
            
        frames_idx = np.random.choice(range(num_frames), size=self.max_frames, replace=False)
        return frames_idx

    def __getitem__(self, idx):
        patient_item = self.fns[idx]
        patient_id = patient_item['pid']
        item_dict = self._load_item(patient_item) 
        image = item_dict['image']              # torch.Size([H, W, T])
        affine = item_dict['affine']
        case_spacing = item_dict['spacing']
        width, height, num_slices = image.shape
        
        # Full volume
        stacked_vol = torch.stack([image, image, image], dim=0) # torch.Size([3, H, W, T])
        full_images = stacked_vol.permute(3, 0, 1, 2) # (C, H, W, T) --> (T, C, H, W)
        

        # Reference frames
        images = []
        frames_idx = self.sampling_frames(num_slices)
        for f_idx in frames_idx:
            this_im = image[:,:,f_idx] #(H, W)
            images.append(this_im)
        images = torch.stack(images, 0).unsqueeze(1)

        
        return {
            "ref_image": images, 
            'ref_indices': frames_idx,
            'full_image': full_images,
            'info': {
                'img_name': patient_id,
                'ori_size': [width, height],
                'affine': affine,
                'spacing': case_spacing
            }
        }

    def collate_fn(self, batch):
        imgs = torch.cat([i['ref_image'] for i in batch], dim=0)
        full_images = torch.stack([i['full_image'] for i in batch], dim=0)
        img_names = [i['img_name'] for i in batch]
        ori_sizes = [i['ori_size'] for i in batch]
        ref_indices = [i['ref_indices'] for i in batch]
        
        return {
            'ref_images': imgs,
            'full_images': full_images,
            'ref_indices': ref_indices,
            'img_names': img_names,
            'ori_sizes': ori_sizes
        }