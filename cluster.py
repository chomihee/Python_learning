from sklearn.cluster import estimate_bandwidth, MeanShift, AgglomerativeClustering, KMeans, AffinityPropagation
from sklearn.metrics import silhouette_samples, silhouette_score, davies_bouldin_score
import time
import numpy as np


def do_mean_shift(data_x, bandwidth=0):
    start = time.time()
    # 최적의 대역폭 찾기 (bandwidth 미입력시 베스트 대역폭 함수 동작, 입력하면 MeanShight에 대역폭 넣고 동작
    if bandwidth == 0:
        bandwidth = estimate_bandwidth(data_x)
    mean_shift = MeanShift(bandwidth=bandwidth)
    labels = mean_shift.fit_predict(data_x)
    print("best bandwidth : ", bandwidth)
    print("labels number : ", np.unique(labels))
    print("time : ", time.time() - start)

    return labels


def check_score(data_x, labels):
    return silhouette_score(data_x, labels), davies_bouldin_score(data_x, labels)


def do_agglomerative_clustering(n_clusters, data_x):
    for cluster in range(2, n_clusters + 1):
        start = time.time()
        # 최적의 대역폭 찾기 (이리찾아도되고,,,, 직접 대역폭 입력해도되고,,)
        agg = AgglomerativeClustering(n_clusters=cluster)
        labels = agg.fit_predict(data_x)
        print("cluster : ", cluster)
        print("time : ", time.time() - start)
        silhouette, davies_bouldin = check_score(data_x, labels)
        print("Silhouette Score : ", silhouette)
        print("Davies Bouldin Score : ", davies_bouldin)


def do_kmeans_clustering(n_clusters, data_x):
    for cluster in range(2, n_clusters + 1):
        start = time.time()
        kmeans = KMeans(n_clusters=cluster)
        labels = kmeans.fit_predict(data_x)
        print("cluster : ", cluster)
        print("time : ", time.time() - start)
        silhouette, davies_bouldin = check_score(data_x, labels)
        print("Silhouette Score : ", silhouette)
        print("Davies Bouldin Score : ", davies_bouldin)


def do_affinity_propagation(data_x):
    start = time.time()
    # 최적의 대역폭 찾기 (bandwidth 미입력시 베스트 대역폭 함수 동작, 입력하면 MeanShight에 대역폭 넣고 동작
    aff_prop = AffinityPropagation()
    labels = aff_prop.fit_predict(data_x)
    print("labels number : ", np.unique(labels))
    print("time : ", time.time() - start)

    return labels
