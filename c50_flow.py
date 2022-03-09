from C50.datasets.process import process_results
from C50.datasets.quantizer import DATASETS, preprocess
from C50.src.axc50 import build, train

YES = ['y', 'yes', 'Y']
NO = ['n', 'no', 'N']

if __name__ == "__main__":
    enable_build = False
    enable_train = True
    enable_save = True

    print('Quantize datasets? [Y/n]')
    if input() not in NO:
        for dataset in DATASETS:
            preprocess(dataset)
            
    print('Build approximate C5.0 versions? [y/N]')
    if input() in YES:
        build(n_bits=8)

    print('Train approximate C5.0 versions in all datasets? [Y/n]')
    if input() not in NO:
        train(n_bits=8)

    print('Process and save results? [Y/n]')
    if input() not in NO:
        process_results(save_files=True)