import sys
import argparse
import torch
from pathlib import Path
from typing import Tuple

sys.path.append('..')

from utils.helpers import available_torch_device


def create_dataset_config() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Image dataset config parser',  add_help=False)

    train_data_path = Path('data/Mapillary_vistas_dataset/training/images')
    train_labels_path = Path('data/Mapillary_vistas_dataset/training/labels_mapped')
    val_data_path = Path('data/Mapillary_vistas_dataset/validation/images')
    val_labels_path = Path('data/Mapillary_vistas_dataset/validation/labels')
    test_data_path = Path('data/Mapillary_vistas_dataset/testing/images')
    json_class_names_file_path = Path('data/Mapillary_vistas_dataset/classes.json')

    # Paths
    parser.add_argument('--train_data_path', type=Path,
                        help='Path to directory containing the training data',
                        default=train_data_path)

    parser.add_argument('--train_labels_path', type=Path,
                        help='Path to directory containing the training labels',
                        default=train_labels_path)
    
    parser.add_argument('--val_data_path', type=Path,
                        help='Path to directory containing the validation data',
                        default=val_data_path)

    parser.add_argument('--val_labels_path', type=Path,
                        help='Path to directory containing the validation labels',
                        default=val_labels_path)

    parser.add_argument('--test_data_path', type=Path,
                        help='Path to directory containing the testing data',
                        default=test_data_path)

    parser.add_argument('--json_class_names_file_path', type=Path,
                        help='Path to a file containing class names',
                        default=json_class_names_file_path)

    # General
    parser.add_argument('--void_class_id', type=int, default=19, help='Label of the void class which should be skipped during training and evaluation')

    return parser


def create_pipeline_config():
    parser = argparse.ArgumentParser(description='Segmentation model pipeline config parser',  add_help=False)

    model_checkpoint = "nvidia/segformer-b0-finetuned-cityscapes-512-1024"
    # model_checkpoint = "nvidia/segformer-b5-finetuned-cityscapes-1024-1024"

    # Model
    parser.add_argument('--model_checkpoint', type=str,
                        help='Model checkpoint version',
                        default=model_checkpoint)
    
    # General
    parser.add_argument('--img_height', type=int, default=512, help='Desired height of the image')
    parser.add_argument('--img_width', type=int, default=1024, help='Desired width of the image')
    parser.add_argument('--batch_size', type=int, default=8, help='Batch size for training')
    parser.add_argument('--val_batch_size', type=int, default=1, help='Batch size for validation')
    parser.add_argument('--device',
                        choices=[torch.device('cpu'), torch.device('cuda'), torch.device('mps')],
                        type=available_torch_device,
                        default='cpu',
                        help='Device used for computation')

    # Transformations
    data_transformations = parser.add_argument_group()
    data_transformations.add_argument('--seed', type=int, default=50, help='Randomness seed')
    data_transformations.add_argument('--crop_size', type=tuple, default=(512, 1024), help='Size of the image after cropping (height, width)')
    data_transformations.add_argument('--horizontal_flip_probability', type=float, default=0.5, help='Probability of the horizontal flip image transformation')
    
    return parser


def parse_train_config() -> argparse.Namespace:
    dataset_config = create_dataset_config()
    pipeline_config = create_pipeline_config()

    output_dir_path = Path('src/models/model_checkpoints')
    output_log_dir_path = Path('src/models/model_logs')
    output_mlflow_log_dir_path = Path('src/models/mlflow_logs')

    parser = argparse.ArgumentParser(description='Training script config parser',
                                     parents=[dataset_config, pipeline_config])

    parser.add_argument('--output_dir', type=Path, default=output_dir_path, help='The output directory where the model predictions and checkpoints will be written')
    parser.add_argument('--output_log_dir', type=Path, default=output_log_dir_path, help='The output directory where the model logs will be written')
    parser.add_argument('--mlflow_log_dir', type=Path, default=output_mlflow_log_dir_path, help='The output directory where the mlflow logs will be written')
    parser.add_argument('--overwrite_output_dir', type=bool, default=False, help='Denotes if the contents of output_dir should be overwritten when training a new')
    parser.add_argument('--num_checkpoints_to_save', type=int, default=30, help='Number of model checkpoints to save in output_dir (If the number of checkpoints exceeds this value, the oldest checkpoints will be overwritten)')

    # Hyperparameters
    parser.add_argument('--num_epochs', type=int, default=3, help='Number of training epochs')
    parser.add_argument('--learning_rate', '--lr', type=float, default=2e-06, help='Initial Learning rate')
    parser.add_argument('--weight_decay', type=float, default=0.01, help='Weight decay (reguralization coef) applied to training loss')
    parser.add_argument('--optimizer_betas', type=Tuple[float, float], default=(0.9, 0.999), help='Adam optimizer beta parameters (b1, b2)')

    return parser.parse_args()


def parse_evaluation_config() -> argparse.Namespace:
    dataset_config = create_dataset_config()
    pipeline_config = create_pipeline_config()

    parser = argparse.ArgumentParser(description='Evaluation script config parser',
                                     parents=[dataset_config, pipeline_config])

    args = parser.parse_args()
    args.img_width = 1024
    args.img_height = 512

    return args


def parse_test_config() -> argparse.Namespace:
    dataset_config = create_dataset_config()
    pipeline_config = create_pipeline_config()
    parser = argparse.ArgumentParser(description='Test script config parser',
                                     parents=[dataset_config, pipeline_config])

    args = parser.parse_args()
    args.img_width = 1024
    args.img_height = 512
    args.batch_size = 1

    return args
