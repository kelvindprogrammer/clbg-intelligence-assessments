def patch_dictionary(images, n_atoms, patch=5, seed=0):
    raise NotImplementedError("R3: k-means atoms (n_atoms, patch*patch*3) over contrast-normalised patches; see the README for the normalisation")


def encode(images, dictionary, patch=5):
    raise NotImplementedError("R4: (n, 4 * n_atoms) triangle-activation features pooled over the four image quadrants")
