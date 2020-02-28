import paillier

if __name__ == '__main__':
    pk, sk, p, q, n, n_len = paillier.generate_paillier_keypair(n_length = 16)
    g, nsquare, max_int = pk.getPara()
    
    print('p:', p, '\nq:', q, '\nn:', n, '\nn_len:', n_len)
    print('g:', g, '\nnsquare:', nsquare, '\nmax_int:', max_int)
    