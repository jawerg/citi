from download.collector import Collector
from learning.classification import generate_dataset_from_feature_file, \
    compute_scores_for_models
from learning.plotting import plot_model_scores
import os
import pickle

if __name__ == '__main__':
    # Use provided link to get all files needed for the task.
    # Collector().download_files().prep_base_files().upload_files()

    # Compute scores for different models.
    pq_path = os.path.join('data', '2_featured', 'tripfeatures.parquet')
    Xt, yt, Xtt, ytt = generate_dataset_from_feature_file(pq_path)
    models, scores = compute_scores_for_models(Xt, yt, Xtt, ytt)
    scores = scores.sort_values("F1-Score", ascending=False)
    scores.to_markdown('outputs/scores.md')

    # generate complementary visualistion of tables
    plot_model_scores(scores)

    # Store Training and Test dataasets for re-use in jupyter notebook.
    base_path = os.path.join('data', '3_train_and_test')

    pickle.dump(Xt, open(os.path.join(base_path, 'Xt.pickle'), 'wb'))
    pickle.dump(yt, open(os.path.join(base_path, 'yt.pickle'), 'wb'))
    pickle.dump(Xtt, open(os.path.join(base_path, 'Xtt.pickle'), 'wb'))
    pickle.dump(ytt, open(os.path.join(base_path, 'ytt.pickle'), 'wb'))
