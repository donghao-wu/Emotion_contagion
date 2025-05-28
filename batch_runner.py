from mesa.batchrunner import batch_run
from model import UrbanMoodModel
import pandas as pd

if __name__ == "__main__":

    parameters = {
        "width":        [20],         # fixed
        "height":       [20],         # fixed
        "density":      [0.5],        # fixed
        "seed":         [42],         # fixed
        # these two will be swept:
        "green_ratio":  [0.1, 0.2, 0.3],
        "stress_ratio": [0.1, 0.2, 0.3],
    }

    
    raw = batch_run(
        model_cls=UrbanMoodModel,
        parameters=parameters,
        iterations=5,
        max_steps=100,
        number_processes=None,
        data_collection_period=-1,   
        display_progress=True,
    )

    
    df = pd.DataFrame(raw)
    df.to_csv("batch_run_results.csv", index=False)
    print("Done. Sample of results:")
    print(df.head())
