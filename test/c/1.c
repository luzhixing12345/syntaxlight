if (M == 32) {

}
else if (M == 64) {
    int i, j, k, l;
    int t0, t1, t2, t3;
    for (i = 0; i < N; i += 4) {
        for (j = 0; j < M; j += 4) {
            if (i != j) {
                for (k = i; k < i + 4; k++) {
                    for (l = j; l < j + 4; l++) {
                        B[l][k] = A[k][l];
                    }
                }
            } else {
                for (k = i; k < i + 4; k++) {
                    t0 = A[k][j];
                    t1 = A[k][j + 1];
                    t2 = A[k][j + 2];
                    t3 = A[k][j + 3];

                    B[k][j] = t0;
                    B[k][j + 1] = t1;
                    B[k][j + 2] = t2;
                    B[k][j + 3] = t3;
                }

                for (k = i; k < i + 4; k++) {
                    for (l = j + (k - i + 1); l < j + 4; l++) {
                        if (k != l) {
                            t0 = B[k][l];
                            B[k][l] = B[l][k];
                            B[l][k] = t0;
                        }
                    }
                }
            }
        }
    }
}