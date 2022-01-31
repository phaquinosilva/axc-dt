from C50.datasets.process import process_results
from C50.datasets.quantizer import DATASETS, preprocess
from C50.src.axc50 import runner

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
            
    print('Build approximate versions? [y/N]')
    if input() in YES:
        enable_build = True

    print('Train approximate C5.0 versions in all datasets? [Y/n]')
    if input() in NO:
        enable_train = False
    
    print('Save results? [Y/n]')
    if input() in NO:
        enable_save = False

    
    runner(build=enable_build, train=enable_train)
    process_results(save_files=enable_save)