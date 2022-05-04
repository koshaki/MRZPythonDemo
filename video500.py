import midv500
# set directory for dataset to be downloaded
dataset_dir = 'midv500_data/'

# download and unzip the base midv500 dataset
dataset_name = "midv500"
midv500.download_dataset(dataset_dir, dataset_name)

# or download and unzip the midv2019 dataset that includes low light images
dataset_name = "midv2019"
midv500.download_dataset(dataset_dir, dataset_name)

# or download and unzip both midv500 and midv2019 datasets
dataset_name = "all"
midv500.download_dataset(dataset_dir, dataset_name)
