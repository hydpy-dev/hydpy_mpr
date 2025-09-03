# !python
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# cython: language_level=3
# cython: cpow=True
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision=True


from numpy cimport int64_t, npy_bool
from cython.operator cimport dereference, postincrement
from libc.math cimport NAN as nan
from libcpp.unordered_map cimport unordered_map


def arithmetic_mean_for_raster_element(
    *,
    int64_t[:, :] element_id,
    npy_bool[:, :] mask,
    double[:, :] output,
    dict[int64, float64] id2value,
) -> None:

    cdef int64_t id_, i, j, nmb
    cdef int64_t m = element_id.shape[0]
    cdef int64_t n = element_id.shape[1]
    cdef unordered_map[int64_t, double] id2value_
    cdef unordered_map[int64_t, double].iterator it
    cdef unordered_map[int64_t, int64_t] id2nmb

    id2value_ = unordered_map[int64_t, double]()
    for id_ in id2value:
        id2value_[id_] = 0.0
        id2nmb[id_] = 0

    with nogil:

        for i in range(m):
            for j in range(n):
                if mask[i, j]:
                    id_ = element_id[i, j]
                    id2value_[id_] += output[i, j]
                    id2nmb[id_] += 1

    it = id2value_.begin()
    while (it != id2value_.end()):
        i = dereference(it).first
        nmb = id2nmb[i]
        id2value[i] = nan if nmb == 0 else dereference(it).second / nmb
        postincrement(it)


def arithmetic_mean_for_raster_subunit(
    *,
    int64_t[:, :] element_id,
    int64_t[:, :] subunit_id,
    npy_bool[:, :] mask,
    double[:, :] output,
    dict[int64, dict[int64, float64]] id2idx2value,
) -> None:

    cdef int64_t id_, idx, i, j, nmb
    cdef int64_t m = element_id.shape[0]
    cdef int64_t n = element_id.shape[1]
    cdef unordered_map[int64_t, unordered_map[int64_t, double]] id2idx2value_
    cdef unordered_map[int64_t, unordered_map[int64_t, double]].iterator i1
    cdef unordered_map[int64_t, double] idx2value_
    cdef unordered_map[int64_t, double].iterator i2
    cdef unordered_map[int64_t, unordered_map[int64_t, int64_t]] id2idx2nmb
    cdef unordered_map[int64_t, int64_t] idx2nmb
    cdef dict[int64_t, double] idx2value

    for id_, idx2value in id2idx2value.items():
        id2idx2value[id_] = unordered_map[int64_t, double]()
        id2idx2nmb[id_] = unordered_map[int64_t, int64_t]()
        for idx in idx2value:
            id2idx2value_[id_][idx] = 0.0
            id2idx2nmb[id_][idx] = 0

    with nogil:

        for i in range(m):
            for j in range(n):
                if mask[i, j]:
                    id_ = element_id[i, j]
                    idx = subunit_id[i, j]
                    id2idx2value_[id_][idx] += output[i, j]
                    id2idx2nmb[id_][idx] += 1

    i1 = id2idx2value_.begin()
    while (i1 != id2idx2value_.end()):
        id_ = dereference(i1).first
        idx2value_ = dereference(i1).second
        idx2nmb = id2idx2nmb[id_]
        idx2value = id2idx2value[id_]
        i2 = idx2value_.begin()
        while (i2 != idx2value_.end()):
            i = dereference(i2).first
            nmb = idx2nmb[i]
            idx2value[i] = nan if nmb == 0 else dereference(i2).second / nmb
            postincrement(i2)
        postincrement(i1)
