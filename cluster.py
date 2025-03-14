import json

from gensim.models import FastText
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter


def build_model():
    with open('text/text8', 'r', encoding='utf-8') as file:
        text = file.read()

    words = text.split()
    sentences = [words[i:i + 10] for i in range(0, len(words), 10)]

    model = FastText(sentences, sg=1, vector_size=1, window=5, min_count=5, negative=3, sample=0.001, hs=1,
                     workers=4, epochs=1)
    model.save('text/text8_fasttext.model')


def cluster(responses):
    model = FastText.load('text/text8_fasttext.model')
    response_texts = []
    attributes = []
    for response in responses:
        try:
            response_text = json.loads(response.text)
            for key in response_text.keys():
                if key not in attributes:
                    attributes.append(key)
        except Exception as e:
            response_text = {}
            print(e)
        if 'status_code' not in response_text:
            response_text['status_code'] = response.status_code
        response_texts.append(response_text)

    for response_text in response_texts:
        if len(response_text) < len(attributes) + 1:
            for attribute in attributes:
                if attribute not in response_text:
                    response_text[attribute] = attribute

    response_vectors = []
    status_codes = {}
    for response_text in response_texts:
        status_code = str([response_text['status_code']])
        if status_code not in status_codes:
            status_codes[status_code] = 1
        else:
            status_codes[status_code] = status_codes.get(status_code) + 1
    for response_text in response_texts:
        response_vector = []
        status_code = str([response_text['status_code']])
        response_vector.append(status_codes[status_code] / len(responses))
        for attr in attributes:
            words = str(response_text[attr]).split()
            temp_vector = [0.0] * 3
            for word in words:
                temp_vector2 = model.wv[word]
                temp_vector = [a + b for a, b in zip(temp_vector, temp_vector2)]
            temp_vector = [temp_vec / len(words) for temp_vec in temp_vector]
            response_vector.extend(temp_vector)
        response_vectors.append(response_vector)

    data = np.array(response_vectors)

    kmeans = KMeans(n_clusters=len(status_codes), random_state=0).fit(data)
    labels = kmeans.labels_

    counter = Counter(labels)

    min_count = min(counter.values())

    least_common_elements = [element for element, count in counter.items() if count == min_count]

    indices = []
    text_unique = []
    for index, value in enumerate(labels):
        if value in least_common_elements:
            if response_texts[index] not in text_unique:
                indices.append(index)
                text_unique.append(response_texts[index])
    return indices


build_model()
