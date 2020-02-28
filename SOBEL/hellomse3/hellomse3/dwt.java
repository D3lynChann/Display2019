package com.test.hellomse3;
/*
 *  Discrete (Haar) Wavelet Transform using Paillier Encryption
 *  Author : Jian Chen 
 *  Latest Modified : 2017.12.6
 */
import java.math.BigDecimal;
import java.math.BigInteger;
import java.io.IOException;

public class dwt
{
    public static BigInteger[] data;
    public static BigInteger[] EnData = new BigInteger[6400000];
    public static BigInteger tmp;
    public static BigInteger[] cA = new BigInteger[6400000];
    public static BigInteger[] cD = new BigInteger[6400000];

    public static BigInteger modn = new BigInteger("1");
    public static BigInteger zeroBase = new BigInteger("0");

    /*
     *  DWT Initialization
     *  BigInteger zeroInput - encrypted '0'
     */
    public dwt(BigInteger zeroInput)
    {
        zeroBase = zeroInput;
    }

    /*
     *  DWT Decomposition
     *  BigInteger[] cA - approximate coefficient
     *  BigInteger[] cD - detail coefficient 
     *  BigInteger[] x  - encrypted data
     *  BigInteger N    - modular of Paillier cryptosystem
     *  int leg         - length of data to be processed
     */
    public static void mallatDe(BigInteger[] cA, BigInteger[] cD, BigInteger[] x, BigInteger N, int leg)
    {
        int i, T1, T2;
        int LEG = 2 * leg;
        BigInteger invX;
        BigInteger minus1 = new BigInteger("-1");

        for(i=0; i<leg; i++)
        {
            T1 = (2*i) % LEG;
            T2 = (1+2*i) % LEG;
            cA[i] = x[T1].multiply(x[T2]).mod(N);
            invX = new BigInteger(x[T2].modPow(minus1,N).toString());
            cD[i] = x[T1].multiply(invX).mod(N);
        }
    }

    /*
     *  Multi-level DWT Decomposition
     *  BigInteger[] datain  - input data
     *  BigInteger modnin    - modular of Paillier cryptosystem
     *  int Level            - levels of wavelet decomposition 
     */
    public BigInteger[] haarDe(int Level, BigInteger[] datain, BigInteger modnin)
    {
        int Dim = datain.length;
        int middle = Dim / 2;
        data = datain;
        modn = modnin;

        for (int k=0; k<Level; k++)
        {
            for(int i=0; i<Dim; i++)
                EnData[i] = data[i];

            mallatDe(cA, cD, EnData, modn, middle);

            for(int i=0; i<middle; i++)
            {
                data[i] = cA[i];
                data[i+middle] = cD[i];
            }
            Dim = Dim / 2;
            middle = middle / 2;
        }

        return data;
    }

    /*
     *  DWT Reconstruction
     *  BigInteger[] cA - approximate coefficient
     *  BigInteger[] cD - detail coefficient 
     *  BigInteger[] x  - encrypted data
     *  BigInteger N    - modular of Paillier cryptosystem
     *  int LEG         - length of data to be processed  
     */
    public static void mallatRe(BigInteger[] cA, BigInteger[] cD, BigInteger[] x, BigInteger N, int LEG)
    {
        int i, T1;
        BigInteger invX;
        BigInteger minus1 = new BigInteger("-1");

        for (i=0; i<LEG; i++)
        {
            T1 = i / 2;
            if (i % 2 == 1)
            {
                invX = new BigInteger(cD[T1].modPow(minus1,N).toString());
                x[i] = cA[T1].multiply(invX).mod(N);
            }
            else
                x[i] = cA[T1].multiply(cD[T1]).mod(N);
        }
    }

    /*
     *  Multi-level DWT Reconstruction
     *  BigInteger[] datain  - input data
     *  BigInteger modnin    - modular of Paillier cryptosystem
     *  int Level            - levels of wavelet decomposition 
     */
    public BigInteger[] haarRe(int Level, BigInteger[] datain, BigInteger modnin)
    {
        int Dim = datain.length;
        int Length = datain.length;
        for (int i=Level; i>0; i--)
            Dim = Dim / 2;
        data = datain;
        modn = modnin;

        /* For Haar wavelet, quantizing factor Q=1 */
        BigInteger quantization_factor_wavelet = new BigInteger("1");
        BigInteger QSquare = quantization_factor_wavelet.multiply(quantization_factor_wavelet);
        BigInteger twoQSquare = QSquare.add(QSquare);

        for (int k=Level; k>0; k--)
        {
            /* Coefficient allocation */
            Dim = Dim * 2;
            for (int i = 0; i < Dim / 2; i++) {
                cA[i] = data[i];
                cD[i] = data[i + Dim / 2];
            }
            mallatRe(cA, cD, EnData, modn, Dim); 

            for (int i = 0; i < Dim; i++) {
                data[i] = EnData[i];
            }

            for(int i=Dim; i<Length; i++)  /* Data after position 'Dim' need to multiply quantizing factor */
            {
                tmp = data[i];
                tmp = tmp.modPow(twoQSquare, modn);  /* multiply 2Q^2 */
                data[i] = tmp;
            }
        }
        return data;
    }
}

