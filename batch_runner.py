from mesa.batchrunner import batch_run
from model import UrbanMoodModel
import pandas as pd

if __name__ == "__main__":
    # ----------------------------------------------------------------
    # 1) Define the full grid of parameters (including any fixed ones).
    #    You can repeat fixed parameters as singleton lists.
    # ----------------------------------------------------------------
    parameters = {
        "width":        [20],         # fixed
        "height":       [20],         # fixed
        "density":      [0.5],        # fixed
        "seed":         [42],         # fixed
        # these two will be swept:
        "green_ratio":  [0.1, 0.2, 0.3],
        "stress_ratio": [0.1, 0.2, 0.3],
    }

    # ----------------------------------------------------------------
    # 2) Run the batch:
    #    - iterations: number of stochastic repeats per combo
    #    - max_steps:  max steps per run
    #    - data_collection_period:
    #        * -1 means collect only at end (since your model.collect is in step())
    #        *  1 would collect every tick
    # ----------------------------------------------------------------
    raw = batch_run(
        model_cls=UrbanMoodModel,
        parameters=parameters,
        iterations=5,
        max_steps=100,
        number_processes=None,
        data_collection_period=-1,   # collect only at the end of each run
        display_progress=True,
    )

    # ----------------------------------------------------------------
    # 3) Turn it into a DataFrame & save:
    # ----------------------------------------------------------------
    df = pd.DataFrame(raw)
    df.to_csv("batch_run_results.csv", index=False)
    print("Done. Sample of results:")
    print(df.head())
