package com.test.hellomse3;

/**
* �����ǱȽϿ����������TXT�����������
* This program is free software: you can redistribute it and/or modify it
* under the terms of the GNU General Public License as published by the Free
* Software Foundation, either version 3 of the License, or (at your option)
* any later version.
*
* This program is distributed in the hope that it will be useful, but WITHOUT
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
* more details.
*
* You should have received a copy of the GNU General Public License along with
* this program. If not, see <http://www.gnu.org/licenses/>.
*/

import java.math.*;
import java.util.*;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OptionalDataException;
import java.io.OutputStream;
import java.io.StreamCorruptedException;
import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.math.*;
import java.sql.*;
import java.io.PrintStream;
import java.util.Scanner; //�����һ��
import java.util.Arrays;
import java.util.Comparator;
/**
1��ͨ����վ����ͼƬ��ͨ��matlab����ÿ��ͼƬ�ֽ��������
2��ͨ��matlab����java����ͼƬ�����������ɾ���A�������PCA��
3����PCA���õ�W���㣬�������BOB��W��ALICE��W��
4�������BOB��W��ALICE�����ģ���W֮���ŷ����þ��루���ܣ���
5���Ƚϼ��ܾ��룬�ó��Ƚ�С�ľ����Ӧ��BOB��������
6��ReRandomize��ģ��s��bob�������������������

 */
/**
 * Paillier Cryptosystem <br>
 * <br>
 * References: <br>
 * [1] Pascal Paillier,
 * "Public-Key Cryptosystems Based on Composite Degree Residuosity Classes,"
 * EUROCRYPT'99. URL:
 * <a href="http://www.gemplus.com/smart/rd/publications/pdf/Pai99pai.pdf">http:
 * //www.gemplus.com/smart/rd/publications/pdf/Pai99pai.pdf</a><br>
 *
 * [2] Paillier cryptosystem from Wikipedia. URL:
 * <a href="http://en.wikipedia.org/wiki/Paillier_cryptosystem">http://en.
 * wikipedia.org/wiki/Paillier_cryptosystem</a>
 * 
 * @author Kun Liu (kunliu1@cs.umbc.edu)
 * @version 1.0
 */
public class Paillier {
 
	/**
	 * p and q are two large primes. lambda = lcm(p-1, q-1) =
	 * (p-1)*(q-1)/gcd(p-1, q-1).
	 */
	private BigInteger p, q, lambda;
	/**
	 * n = p*q, where p and q are two large primes.
	 */
	public BigInteger n;
	/**
	 * nsquare = n*n
	 */
	public BigInteger nsquare;
	/**
	 * a random integer in Z*_{n^2} where gcd (L(g^lambda mod n^2), n) = 1.
	 */
	private BigInteger g;
	/**
	 * number of bits of modulus
	 */
	private int bitLength;
 
	/**
	 * Constructs an instance of the Paillier cryptosystem.
	 * 
	 * @param bitLengthVal
	 *            number of bits of modulus
	 * @param certainty
	 *            The probability that the new BigInteger represents a prime
	 *            number will exceed (1 - 2^(-certainty)). The execution time of
	 *            this constructor is proportional to the value of this
	 *            parameter.
	 */
	
	public static long timeForAlice = 0;
	public static long timeForBob = 0;
	public static long timeForAlice2 = 0;
	public static long timeForBob2 = 0;
	public static final BigInteger minusOne = BigInteger.ONE.negate();
	public static final BigInteger zero = BigInteger.ZERO;
	public static final BigInteger one = BigInteger.ONE;
	public static final BigInteger two = one.add(one);
	public static final BigInteger three = two.add(one);
	
	public Paillier(int bitLengthVal, int certainty) {
		KeyGeneration(bitLengthVal, certainty);
	}
 
	/**
	 * Constructs an instance of the Paillier cryptosystem with 512 bits of
	 * modulus and at least 1-2^(-64) certainty of primes generation.
	 */
	public Paillier() {
		KeyGeneration(512, 64);
	}
 
	/**
	 * Sets up the public key and private key.
	 * 
	 * @param bitLengthVal
	 *            number of bits of modulus.
	 * @param certainty
	 *            The probability that the new BigInteger represents a prime
	 *            number will exceed (1 - 2^(-certainty)). The execution time of
	 *            this constructor is proportional to the value of this
	 *            parameter.
	 */
	public void KeyGeneration(int bitLengthVal, int certainty) {
		bitLength = bitLengthVal;
		/*
		 * Constructs two randomly generated positive BigIntegers that are
		 * probably prime, with the specified bitLength and certainty.
		 */
		p = new BigInteger(bitLength / 2, certainty, new Random());
		q = new BigInteger(bitLength / 2, certainty, new Random());
 
		n = p.multiply(q);
		nsquare = n.multiply(n);
 
		g = new BigInteger("2");
		lambda = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE))
				.divide(p.subtract(BigInteger.ONE).gcd(q.subtract(BigInteger.ONE)));
		/* check whether g is good. */
		if (g.modPow(lambda, nsquare).subtract(BigInteger.ONE).divide(n).gcd(n).intValue() != 1) {
	//		System.out.println("g is not good. Choose g again.");
			System.exit(1);
		}
	}
 
	/**
	 * Encrypts plaintext m. ciphertext c = g^m * r^n mod n^2. This function
	 * explicitly requires random input r to help with encryption.
	 * 
	 * @param m
	 *            plaintext as a BigInteger
	 * @param r
	 *            random plaintext to help with encryption
	 * @return ciphertext as a BigInteger
	 */
	public BigInteger Encryption(BigInteger m, BigInteger r) {
		return g.modPow(m, nsquare).multiply(r.modPow(n, nsquare)).mod(nsquare);
	}
 
	/**
	 * Encrypts plaintext m. ciphertext c = g^m * r^n mod n^2. This function
	 * automatically generates random input r (to help with encryption).
	 * 
	 * @param m
	 *            plaintext as a BigInteger
	 * @return ciphertext as a BigInteger
	 */
	public BigInteger Encryption(BigInteger m) {
		BigInteger r = new BigInteger(bitLength, new Random());
		return g.modPow(m, nsquare).multiply(r.modPow(n, nsquare)).mod(nsquare);
 
	}
 
	/**
	 * Decrypts ciphertext c. plaintext m = L(c^lambda mod n^2) * u mod n, where
	 * u = (L(g^lambda mod n^2))^(-1) mod n.
	 * 
	 * @param c
	 *            ciphertext as a BigInteger
	 * @return plaintext as a BigInteger
	 */
	public BigInteger Decryption(BigInteger c) {
		BigInteger u = g.modPow(lambda, nsquare).subtract(BigInteger.ONE).divide(n).modInverse(n);
		return c.modPow(lambda, nsquare).subtract(BigInteger.ONE).divide(n).multiply(u).mod(n);
	}
 
	/**
	 * sum of (cipher) em1 and em2
	 * 
	 * @param em1
	 * @param em2
	 * @return
	 */
	public BigInteger cipher_add(BigInteger em1, BigInteger em2) {
		return em1.multiply(em2).mod(nsquare);
	}
 
	/**
	 * main function
	 * 
	 * @param str
	 *            intput string
	 */
	public static void main(String[] str) throws Exception{

	
		File f=new File("E:\\result\\PCA\\testalice-junzhi2.txt");
        f.createNewFile();
        FileOutputStream fileOutputStream = new FileOutputStream(f);
        PrintStream printStream = new PrintStream(fileOutputStream);
        System.setOut(printStream);
   
  		/* --------------------------------------------����ͳһ����------------------------------------------------------------- */
		int NumBobMsg6=400;
		int NumBoblength=1288;
		int uvectornumber=300;
		int NumALICElength=10304;
		int Nummindintance=10;
		//int Numofface=6;  //�ڼ���alice����
		BigInteger m3= new BigInteger("40");//��ֵ�ĳ��Ȳ���������ֵ��̫�࣬��˵�ʱ�򣬸������
		double SS= 0.07;//����ģ�����1000000���仯��ʱ��UҪ��  ;PCA��ʱ��double SS= 0.07;
		/* --------------------------------------------����ͳһ����------------------------------------------------------------- */
      
		/* -------------------------------------------��ʼ��ȡ�ʹ���BOB------------------------------------------------------------ */	
		
		/* ����BOb���е�����BobMsg-BobMsg6����AliceMsg	*/	
		double [][] BobMsgdouble=new double[NumBobMsg6][NumBoblength];  //����Ϊ9*6����6��1*9��һά������ÿ��Ϊһ��ͼƬ��һ��6��ͼƬ��
		double [][] udouble=new double[uvectornumber][NumBoblength]; 
		double [][] AliceMsgdoubleall= new double[40][NumALICElength];
		double [] AliceMsgdouble= new double[NumALICElength];
		double [][] Cmatricdouble=  new double[uvectornumber][uvectornumber];
		/*��ʼ����txt���ݣ�*/
		
		BobMsgdouble=FileTobobAry(NumBobMsg6,NumBoblength);
		udouble=FileTouAry(uvectornumber,NumBoblength);
		AliceMsgdoubleall=FileToaliceAry(NumALICElength);
		
		 //����ͨ��SS��double�͵����󣬷������paillier����	
		int [][] BobMsg= new int[NumBobMsg6][NumBoblength];
		int [][] u= new int[uvectornumber][NumBoblength];
		int [][] Cmatric= new int[uvectornumber][uvectornumber];
		
		
		/*--------------------------------------------------------- ����ͨ��SS��ʼ�������е���	----------------------------------------*/
		for(int i=0; i<BobMsg.length;i++)
		{
			for(int j=0;j<BobMsg[1].length;j++)
			{
				//System.out.println("BobMsg " + i+"��" +j+ ": " + BobMsgdouble[i][j]);
				BobMsg[i][j]=(int)(BobMsgdouble[i][j]*SS*2.828);//��ÿһ��ֵ��������
		//		System.out.println("BobMsg " + i +j+ ": " + BobMsg[i][j]);
			}
		}
		
		for(int i=0; i<u.length;i++)
		{
			for(int j=0;j<u[0].length;j++)
			{
				
			//	System.out.println("udouble " + i+"  " +j+ ": " + udouble[i][j]);
					
				u[i][j]=(int)(udouble[i][j])/16; // PCA��ʱ����* 80;
			//	u[i][j]=(int)(udouble[i][j]);// LFDA����	
			//	System.out.println("u " + i+"  " +j+ ": " + u[i][j]);
			}
		}
		
		
		/* -------------------------------------------������ȡ�ʹ���BOB------------------------------------------------------------ */	
		/* -------------------------------------------��ʼѭ����ȡ�ʹ���ALICE------------------------------------------------------------ */	
		int sumaccuracy=0;//��ʼ�������еĸ���Ϊ0
		double accuracysumrate=0.00;//��ʼ����׼ȷ��Ϊ0
		double recallsumrate=0.00;//��ʼ�����ٻ���Ϊ0
		for(int Numofface=1;Numofface<=40;Numofface++)
        {
		
			Paillier paillier = new Paillier();
			BigInteger m4 = new BigInteger("1");	
			
			AliceMsgdouble=AliceMsgdoubleall[Numofface-1];
			
			int [] AliceMsg= new int [NumALICElength];
			for(int j=0;j<AliceMsg.length;j++)
			{
			//	System.out.println("AliceMsgdouble " +j+ ": " + AliceMsgdouble[j]);
				AliceMsg[j]=(int)(AliceMsgdouble[j]*SS);//��ÿһ��ֵ��������
				
			}
			/*--------------------------------------------------------- ������ϣ�ͨ��PCA����ŷʽ����	----------------------------------------------------------------------------------------------*/
			//Alice����Ԫͼ���ÿһλe_AliceMsg
			
			BigInteger [] e_AliceMsg = new BigInteger[AliceMsg.length]; //biginteger array that contains x
			BigInteger [] we_AliceMsg = new BigInteger[uvectornumber]; //biginteger array that contains x
			int a;
			int temps=0;
			BigInteger tempss;
			
			/*����B0b�����ƽ��ֵ�����ŵ�AverageBOb����������ܵ�AverageBOb*/
			int []AverageBOb= new int[NumBoblength]; 
			BigInteger[] e_AverageBOb = new BigInteger[AverageBOb.length];

			for(int i=0; i<AverageBOb.length;i++)
			{
				double sumBOb=0;
				for(int j=0;j<NumBobMsg6;j++)
				{
					sumBOb=sumBOb+BobMsg[j][i];//��Bob����������ۼ�����
				}
				
					sumBOb= sumBOb/NumBobMsg6;
					AverageBOb[i] =(int)sumBOb;
					e_AverageBOb[i] = paillier.Encryption(BigInteger.valueOf(AverageBOb[i]));//ʱ�临�Ӷ�--1288��Encryption
			}
			
			/*���ݼ���BOB���������W*/
			int [][]WBobMsg= new int[NumBobMsg6][uvectornumber]; //ÿά����u�ĸ���

			for(int k=0;k<NumBobMsg6;k++)
			{
				for(int i=0; i<u.length;i++)
				{
				
					WBobMsg[k][i]=0;
					for(int j=0; j<AverageBOb.length;j++)
					{
						temps=BobMsg[k][j]-AverageBOb[j];
						temps=u[i][j]*(BobMsg[k][j]-AverageBOb[j]); //U��ת�ó��Բ�ֵ
						WBobMsg[k][i]=WBobMsg[k][i]+temps;
					}
				}
			}
			
			
			for(int i=0; i<AliceMsg.length;i++)
			{
				temps = AliceMsg[i]; 
				e_AliceMsg[i] = paillier.Encryption(BigInteger.valueOf(temps)); //ʱ�临�Ӷ�--10304��Encryption
				a=sizeof(e_AliceMsg[i]);
			//	System.out.println("a*** " + i + ": " + a);
			}
			
			/*����ͨ��AliceMsg��AliceMsg�����ģ�����С���ֽ⣬��ü��ܵ�С�����ĸ�bob*/
			e_AliceMsg=DWT_ALICE(AliceMsg,e_AliceMsg,paillier);
			
			/*Aliceͨ�����ܵ�ֵ��������ܵ�����W���õ�we_AliceMsg*/
			for(int i=0; i<u.length;i++)
			{
	
				BigInteger sumtempss= BigInteger.ONE;
	
				for(int j=0; j<e_AliceMsg.length;j++)
				{

					tempss=e_AliceMsg[j].multiply((e_AverageBOb[j]).modInverse(paillier.nsquare));  //[I] �� [?��1] ʱ�临�Ӷ�

					tempss =tempss.modPow(BigInteger.valueOf(u[i][j]),paillier.nsquare); 	// [��1]^u  ʱ�临�Ӷ�

					sumtempss=sumtempss.multiply(tempss).mod(paillier.nsquare);//�۳� [��1]^u��ΪAlice�ĵ�i��Wֵ  ʱ�临�Ӷ�
			
				}
				we_AliceMsg[i]= sumtempss.mod(paillier.nsquare);  //ʱ�临�Ӷ�
			}
			
			/*--------------------------------------------------------- ����ŷʽ����	/���Ͼ���----------------------------------------------------------------------------------------------*/
					
			BigInteger [] em=new BigInteger[NumBobMsg6];
			
			/* ���Լ���Alice��BOB��ŷ����þ���*/
			for(int k=0;k<NumBobMsg6;k++)
			{
			
				em[k]=EuclideanDistance(we_AliceMsg,WBobMsg[k],paillier);
	
			}
		

			/*--------------------------------------------------------- �Ƚ�ŷʽ����	/���Ͼ���----------------------------------------------------------------------------------------------*/
			
			/* 
			 *  ���ԱȽ�ŷ����þ���
			 */
			
			//�ȱ���һ��em��������������
			BigInteger [] embak=new BigInteger[NumBobMsg6];
			for(int mn=0;mn<NumBobMsg6;mn++) 
			{
				embak[mn]=em[mn];					
			}
			for(int mn=0;mn<NumBobMsg6;mn++) 
			{
						System.out.println("����ǰembak��"+mn+"������ľ���Ϊ��"+paillier.Decryption(embak[mn]).toString());
			}
			//��ͨ����������
			embakSortByfun(embak,m3,m4,paillier);
			
			System.out.println("2222");
			int [] mins=new int[Nummindintance];
			for(int mm=0;mm<Nummindintance;mm++) 
			{
				for(int b = 0;b<NumBobMsg6;b++)
				{
					if((embak[mm].compareTo(em[b]))==0) 
					{
						mins[mm]=b+1;
						System.out.println("��"+mm+"������ľ���Ϊ��"+paillier.Decryption(embak[mm]).toString()+"��������ĵ� "+mins[mm]+"��");
						
					}
				}
			}
			System.out.println("--------------------------------------------------------------------------------"+Numofface);
			System.out.println("Numofface������"+Numofface);
			//����ÿ��aliceѭ��׼ȷ�ĸ���
			int [] accuracy=new int[NumBobMsg6];   
			int [] wrong=new int[NumBobMsg6]; 
			int maxlimit=Numofface*10;
			int minlimit=(Numofface-1)*10+1;
			int Numoffacebak=Numofface-1;
			for(int cc=0;cc<Nummindintance;cc++) 
			{
				int b=mins[cc];
				if((b<=maxlimit)&&(b>=minlimit))  //�ڽ����ڣ�����
					accuracy[Numoffacebak]++;
				else
					wrong[Numoffacebak]++;
				
			}
			System.out.println("maxlimit  "+maxlimit+"minlimit"+minlimit+"accuracy  "+accuracy[Numoffacebak]+"wrong  "+wrong[Numoffacebak]);
			sumaccuracy=sumaccuracy+accuracy[Numoffacebak];
			System.out.println("timeForAlice  "+timeForAlice+"timeForBob  "+timeForBob+"timeForAlice2  "+timeForAlice2+"timeForBob2  "+timeForBob2);
			
        }
		System.out.println("��������");
		//������׼ȷ�ʺ��ٻ���	
		accuracysumrate=(double)(sumaccuracy/(Nummindintance*40));
		recallsumrate=(double)(sumaccuracy/400);
		
		System.out.println("sumaccuracy  "+sumaccuracy+"accuracysumrate  "+accuracysumrate+"recallsumrate  "+recallsumrate);
		System.out.println("timeForAlice  "+timeForAlice+"timeForBob  "+timeForBob+"timeForAlice2  "+timeForAlice2+"timeForBob2  "+timeForBob2);
		
		
	}
	
	
	/*--------------------------------------------------------- ����������/ʣ������������Ӻ���----------------------------------------------------------------------------------------------*/
	
	private static void embakSortByfun(BigInteger[] embak,BigInteger m3, BigInteger m4,Paillier paillier) {
		int cishu=0;
		Arrays.sort(embak, new Comparator<BigInteger>() {
		
            @Override
            public int compare(BigInteger x, BigInteger y) {
            	
            	int isabiggerb;
            	isabiggerb= paillier.CompareEncrypted(x,y,m3,m4,paillier);
				if(isabiggerb==1) 
				{
					
					 return 1;
				}
                else if(isabiggerb==-1)
                    return -1;
                else
                    return 0;
            }
        });
		System.out.println("cishu  "+cishu);
	}

	private static int sizeof(BigInteger bigInteger) {
		// TODO Auto-generated method stub
		return 0;
	}

	private static int sizeof(BigInteger[] e_AliceMsg) {
		// TODO Auto-generated method stub
		return 0;
	}

	//-------------------------------------------------------�����Ǽ���ŷ�����/���Ͼ���-----------------------------------------------
	
	/**
	 * Returns an encryption of EuclideanDistance
	 *
	 *  
	 * @param e_AliceMsg��Alice���ܵ���Ϣ��BobMsg���Լ��������Ϣ��������
	 * @param paillier
	 * @return AliceMsg��BobMsg��ŷ����þ���
	 */

	public static BigInteger EuclideanDistance(BigInteger[] e_AliceMsg, int[] BobMsg,Paillier paillier) 
		{
		
			StartCounting2(); 
			long start2 = System.currentTimeMillis();
			
			int sMessage;
			int cMessage;
			int cMessageSquared;
			BigInteger tmp = null;
			BigInteger tmp1 = null;
			BigInteger tmp2 = null;
			BigInteger ed = BigInteger.ONE;
			BigInteger ed1 = BigInteger.ONE;
			BigInteger ed2 = BigInteger.ONE;


			BigInteger[] e_AliceMsgSquared = new BigInteger[BobMsg.length]; // biginteger array that contains x^2	
			BigInteger[] e_BobMsgSquared = new BigInteger[BobMsg.length]; //biginteger array that contains y^2


			BigInteger sumx= null;  //x����ĺ�
			BigInteger e_sumx= null;  //���ܵ�x����ĺ�

			BigInteger [] randoms= new BigInteger [BobMsg.length];  //��������� randoms
			BigInteger [] e_randoms= new BigInteger [BobMsg.length];  //���ܵ���������� e_randoms

			BigInteger[] x= new BigInteger[BobMsg.length];  //x����
			BigInteger[] e_x= new BigInteger[BobMsg.length];  //���ܵ�x����


			//BobMsg����ֱ�Ӽ��ܣ���ΪBOB��BobMsg��ԭֵ�������Ǽ���S1��ÿһλ������e_BobMsgSquared[i]���������ĺ;���S1
			for(int i = 0; i<BobMsg.length; i++)
			{
				sMessage = BobMsg[i];
				sMessage = sMessage*sMessage;
				
		//		System.out.println("BobMsg.length " + ": " + BobMsg.length);
				
				e_BobMsgSquared[i] =paillier.Encryption(BigInteger.valueOf(sMessage));  //ʱ�临�Ӷ�
				//	System.out.println("BobMsg^2 " + i + ": " + paillier.Decryption(e_BobMsgSquared[i]));
			}

			
			//e_AliceMsg������ֱ��ƽ����BOBҪ��ALIECE�ٽ���һ�Σ������Ǽ���S3�Ŀ�ʼ
			//1��BOB�Ȳ���һ��e_x[i]����
			for(int i=0; i<BobMsg.length;i++)
			{
				Random random = new SecureRandom();
				
				//������ĳ���̫�����ᵼ�½��ܵ�ʱ�򣬾����ɸ������߳����������޷�����
				randoms[i] = new BigInteger(BobMsg.length/50, random);
				
				e_randoms[i]=paillier.Encryption(randoms[i]); //���ܵ�i�������  ʱ�临�Ӷ�
				e_x[i]=e_AliceMsg[i].multiply(e_randoms[i]).mod(paillier.nsquare);  //ʱ�临�Ӷ�
				
				//	System.out.println("e_randoms " + i + ": " + paillier.Decryption(e_randoms[i])+"  e_AliceMsg " + i + ": " + paillier.Decryption(e_AliceMsg[i])+"  e_x " + i + ": " + paillier.Decryption(e_x[i]));
			}
			
			timeForBob2 +=System.currentTimeMillis()-start2;
			start2 = System.currentTimeMillis();
			int b;
			//System.out.println("b*** "  + ": " + e_x[1].bitLength());
			
			
			//2��ALICE��e_x[i]���ܣ�����X���ۼӺ͵ļ���e_sumx��BOB
			sumx=zero;
			for(int i=0; i<BobMsg.length;i++)
			{
				tmp=paillier.Decryption(e_x[i]);  //ʱ�临�Ӷ�
				tmp=tmp.multiply(tmp);//�����򣬲���mod  
				sumx= sumx.add(tmp);  
			//	System.out.println("sumx " +  ": " + sumx);
			}
			
			e_sumx=paillier.Encryption(sumx); //�������������e_sumx�ļ���  ʱ�临�Ӷ�
		//	System.out.println("e_sumx " + ": " + paillier.Decryption(e_sumx));

			timeForAlice2 +=System.currentTimeMillis()-start2;
			start2 = System.currentTimeMillis();
			
			//3��BOB�ټ���S3�ĺͣ��Ȱ���ʽ����ǰ��� ʱ�临�Ӷ�
			for(int i=0; i<BobMsg.length;i++)
			{
							
				tmp1 = e_AliceMsg[i].modPow(BigInteger.valueOf(randoms[i].intValue()),paillier.nsquare); //tmp1 = [r^e_AliceMsg]
				tmp1 = tmp1.modPow(two,paillier.nsquare ); //tmp1 = [2e_AliceMsg*r]
					
				tmp2=randoms[i].multiply(randoms[i]).mod(paillier.nsquare);  // .modInverse(paillier.nsquare); //ri��ƽ��
				tmp2 =paillier.Encryption(tmp2);//ri��ƽ���ļ���
				
				ed=ed.multiply(tmp1.modInverse(paillier.nsquare)).multiply(tmp2.modInverse(paillier.nsquare));  //-ri��ƽ��-r^e_AliceMsg
				ed= ed.mod(paillier.nsquare);
				

				
			//	System.out.println("ed " + ": " + paillier.Decryption(ed));//�������ײ�����
			}
			
			e_sumx=e_sumx.multiply(ed); //�������������S3�ļ���
			e_sumx= e_sumx.mod(paillier.nsquare);

			//	System.out.println("e_sumx " + ": " + paillier.Decryption(e_sumx));
			
			//�����Ǹ��ݹ�ʽ(x-y)^2= x^2-2xy+y^2����������Ľ���������
			for(int i = 0; i<BobMsg.length; i++)
			{
				tmp1 = e_AliceMsg[i].modInverse(paillier.nsquare); //tmp1  = - e_AliceMsg
				tmp1 = tmp1.modPow(BigInteger.valueOf(BobMsg[i]),paillier.nsquare); //tmp1 = -e_AliceMsg*BobMsg
				tmp1 = tmp1.modPow(two, paillier.nsquare); //tmp1 = -2e_AliceMsg*BobMsg
				tmp2 =tmp1.multiply(e_BobMsgSquared[i]); 
				tmp2 = tmp2.mod(paillier.nsquare);//tmp2= -2e_AliceMsg*BobMsg+BobMsg^2
				ed2=ed2.multiply(tmp2);
				ed2= ed2.mod(paillier.nsquare);
			}
			
			//	System.out.println("ed2 " + ": " + paillier.Decryption(ed2));//�������������S2�ļ���
			
			
			ed2=e_sumx.multiply(ed2); //�������������S3+s2+s1
			ed2= ed2.mod(paillier.nsquare);

			//System.out.println("ed2 2" + ": " + paillier.Decryption(ed2));//�������������S1+S2+S3�ļ���
			
			timeForBob2 +=System.currentTimeMillis()-start2;
			start2 = System.currentTimeMillis();
			
			return ed2;
		}
	
	
	//-------------------------------------------------------�����ǱȽ�ŷ����þ���-----------------------------------------------
	
	
	/**
	 * Returns true if em is an encryption of zero under the key. 
	 * This method is much faster than Decrypt.
	 *  
	 * @param e_value
	 * @param key
	 * @return
	 * // tmp = em^(vp*vq) mod n ����DGK���ԣ�����̬ͬ���ܲ��Բ����ԣ������������0���򷵻�1�����Ƿ���0
	 */
	
	public static boolean IsEncryptedZero(BigInteger em,Paillier paillier) {
		

		// tmp = em^(vp*vq) mod n
		 BigInteger tmp = paillier.Decryption(em);
		
		 
	//	 System.out.println(" tmp "+tmp.toString());
		 
		if (tmp.equals(zero)) {
			return true; 
		}
		
		return false;
	}
	

	/*
	 * Based on Erkin et. al.'s Privacy-preserving face recognition, Section 5
	 *
	 * Compare the size of encrypted values a and b. 
	 * M is an upper bound for a, b sizes in bits.
	 * kappa is a security parameter.
	 * (M+kappa) must be smaller than key.Lbit! 
	 * @return -1 if a is smaller than b, +1 otherwise
	 */
	public static int CompareEncrypted(BigInteger a, BigInteger b, BigInteger M, BigInteger kappa,Paillier paillier) {
		
	
	//	System.out.println("CompareEncrypted is doing " );
		Random random = new SecureRandom();//random--��ʱ����
		
		
		StartCounting(); 
		long start = System.currentTimeMillis();
		
		// z = 2^M + a - b  20190801
		BigInteger twoToM = BigInteger.valueOf(2).pow(M.intValue()); //twoToM--��ʱ����

		BigInteger e_twoToM = paillier.Encryption(twoToM); //e_twoToM--��ʱ����  20190801
		
		
		BigInteger e_z = e_twoToM.multiply(a).mod(paillier.nsquare).multiply(b.modInverse(paillier.nsquare)).mod(paillier.nsquare);
	
		//e_z--��ʱ����  20190801
//		System.out.println("2^Mֵ"+twoToM.toString());
		
	//	System.out.println("zֵ "+paillier.Decryption(e_z).toString());
		// d = z + r������һ��λ��������2^8��һ�������r
		BigInteger r = new BigInteger(M.add(kappa).intValue(), random);//z--��ʱ����
		
		
		BigInteger e_r = paillier.Encryption(r); //e_r--��ʱ����   20190801
		BigInteger e_d = e_z.multiply(e_r).mod(paillier.nsquare); //e_d--��ʱ����  20190801
		//���ReRandomize����Ҫ��	e_d = ReRandomize(e_d, key); 

		timeForBob +=System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
//		System.out.println("rֵ " +paillier.Decryption(e_r).toString());
	//	System.out.println("dֵ " +paillier.Decryption(e_d).toString());
		
		
		// reduce d to (d mod 2^M)
		DForComparisonResult dForComparison = CompareEncrypted_GetDMod2M_DBits_Encrypted(e_d, M,paillier);
		
		timeForAlice += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();

		BigInteger e_d_hat = dForComparison.d; //e_d_hat-��ʱ����(��e_z_tilde��
		BigInteger[] e_d_bits = dForComparison.d_i;//e_d_bits--ͳ�Ʊ���
		
//		System.out.println("d mod 2^m "+paillier.Decryption(dForComparison.d).toString());
		
		// z_tilde = (d mod 2^M) - (r mod 2^M)
		BigInteger r_hat = r.mod(twoToM); //r_hat-��ʱ����
		BigInteger e_r_hat = paillier.Encryption(r_hat); //e_r_hat-��ʱ����  20190801
		BigInteger e_z_tilde = e_d_hat.multiply(e_r_hat.modInverse(paillier.nsquare)).mod(paillier.nsquare);//e_z_tilde-��ʱ����  20190801
		
	//	System.out.println("e_z_tilde "+paillier.Decryption(e_z_tilde).toString());
		// TODO: remove debug
//		System.out.println("twoToM: "+twoToM);				
//		System.out.println("e_twoToM decrypted: "+Damgard.Decrypt(e_twoToM, key));				
//		System.out.println("e_z decrypted: "+Damgard.Decrypt(e_z, key));	
//		System.out.println("e_d decrypted: "+Damgard.Decrypt(e_d, key));
//		System.out.println("e_d_hat decrypted: "+Damgard.Decrypt(e_d_hat, key));	
//		System.out.println("e_r decrypted: "+Damgard.Decrypt(e_r, key));
//		System.out.println("e_r_hat decrypted: "+Damgard.Decrypt(e_r_hat, key));				
//		System.out.println("e_z_tilde decrypted: "+Damgard.Decrypt(e_z_tilde, key));		
		
		// if (r mod 2^M) < (d mod 2^M), z_tilde is the value of (z mod 2^M)
		// we have to find out if it is the case.
		
		// for technical reasons:  r? = 2*r?, d_hat = 2*d_hat+1
		// modified d's bits are already in e_d_bits
		BigInteger r_hat_comparison = r_hat.multiply(two);  //r_hat_comparison-��ʱ����
		boolean[] r_bits = new boolean[M.intValue()+1];  //r_bits-��Ҫͳ�ƣ����ģ�
		for (int i = 0; i < M.intValue()+1; i++) {
			r_bits[i] = r_hat_comparison.testBit(i) ? true : false;
		}
		
		timeForBob+=System.currentTimeMillis()-start;
		BigInteger e_lambda = CompareBitArrays(e_d_bits, r_bits,paillier); //e_lambda-��ʱ����
		start = System.currentTimeMillis();
		
		// fix possible underflow
		// (z mod 2^M) = z_tilde + lambda*2^M   20190801
		BigInteger e_z_mod = e_z_tilde.multiply(e_lambda.modPow(twoToM, paillier.nsquare)).mod(paillier.nsquare);
		//e_z_mod-��ʱ����
		
		// z[l] = 2^(-M)*(z - (z mod 2^M))
		// ! it is ok to just use (z - (z mod 2^M)), we get 2^M*(z_l)  20190801
		BigInteger e_z_l = e_z.multiply(e_z_mod.modInverse(paillier.nsquare));	//e_z_l-ͳ�Ʊ���

		// TODO: remove debug
		//System.out.println("e_z_mod decrypted: "+Damgard.Decrypt(e_z_mod, key));			
		//System.out.println("e_z_l decrypted: "+Damgard.Decrypt(e_z_l, key));
		
		timeForBob += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
		//�������λ���Բ��������൱�ڱȽ�100000��0000000
//		System.out.println(" 2^M*(z_l) "+paillier.Decryption(e_z_l).toString());
		
		
		// AliceMsg can decrypt the result and find out, if a<b or not.
		boolean isEncryptedZero = IsEncryptedZero(e_z_l,paillier);	//isEncryptedZero-��ʱ����
		
//		System.out.println("isEncryptedZero "+isEncryptedZero);
		
		timeForAlice += System.currentTimeMillis()-start;
		
		if (isEncryptedZero) {
			return -1;
		} else {
			return 1;
		}
	}
	
	private static void StartCounting() {
		timeForAlice = 0;
		timeForBob = 0;
	}
	
	private static void StartCounting2() {
		timeForAlice2 = 0;
		timeForBob2 = 0;
	}
	/**
	 * Based on Erkin et. al.'s Privacy-preserving face recognition, Section 5
	 * decrypt d, reduce it modulo 2^M, encrypt it again
	 * 
	 * DO NOT CALL DIRECTLY! Does AliceMsg's job for SubSection 5.2
	 */
	public static DForComparisonResult CompareEncrypted_GetDMod2M_DBits_Encrypted(BigInteger d, BigInteger M,Paillier paillier) {
		
//		System.out.println("CompareEncrypted_GetDMod2M_DBits_Encrypted is doing " );
		BigInteger decrypted = paillier.Decryption(d);   //decrypted--��ʱ����   20190801
		BigInteger dMod2M = decrypted.mod(two.pow(M.intValue()));  //dMod2M--ͳ�Ʊ������ֲ��������㣩
		
		
	//	System.out.println("dMod2M " +dMod2M.toString());
	
		
		
		BigInteger dModForComparison = dMod2M.multiply(two).add(one);//dModForComparison--��ʱ����
		
	//	System.out.println("dMod2M*2+1 " +dModForComparison.toString());
			
	//	System.out.println("dMod2M*2+1 " +dModForComparison);
		
		BigInteger[] d_i = new BigInteger[M.intValue()+1]; //d_i--ͳ�Ʊ������ֲ��������㣩
		for (int i = 0; i < M.intValue()+1; i++) {
			boolean bitValue = dModForComparison.testBit(i) ? true : false;  //bitValue--��ʱ����
			d_i[i] = paillier.Encryption(bitValue ? one : zero);  //20190801
		}
		
		DForComparisonResult dWithBitsEncrypted = new DForComparisonResult();
		dWithBitsEncrypted.d = paillier.Encryption(dMod2M);    //20190801
		dWithBitsEncrypted.d_i = d_i;
		
		return dWithBitsEncrypted;
	}
	
	/**
	public static boolean[] GetBitArray(BigInteger a, int M) {
		boolean[] result = new boolean[M];
		for (int i = 0; i < M; i++) {
			result[i] = a.testBit(i);
		}
		return result;
	}
	
	
	 * Based on SubSection 5.3 from Etkin et al's Privacy-Preserving face recognition
	 * 
	 * Compare two BigIntegers d, r represented as bit arrays of the same length. 
  	 * First of the two arrays is encrypted using key.
  	 * 
  	 * The result is:
  	 *   an encryption of 1 if r > d
  	 *   an encryption of 0 otherwise 
	 */
	public static BigInteger CompareBitArrays(BigInteger[] e_d_bits, boolean[] r_bits,Paillier paillier) {
		
//		System.out.println("CompareEncrypted_GetDMod2M_DBits_Encrypted is doing " );
		if (e_d_bits.length != r_bits.length) 
			throw new IllegalArgumentException("bit array lengths for d and r do not match!");
		
	
		long start = System.currentTimeMillis();
		
		// encrypt r_bits and minus r_bits  20190801
		//BigInteger[] e_r_bits = new BigInteger[r_bits.length];
		BigInteger[] e_mr_bits = new BigInteger[r_bits.length];//e_mr_bits--��ʱ����
		for (int i = 0; i < r_bits.length; i++) {
			BigInteger bitValue = r_bits[i] ? one : zero;
			BigInteger minusBitValue = r_bits[i] ? minusOne : zero;
		//	e_r_bits[i] = paillier.Encryption(bitValue);
			e_mr_bits[i] = paillier.Encryption(minusBitValue); 
		}

		// w[i] = d[i] XOR r[i]   20190801
		BigInteger[] e_w = new BigInteger[r_bits.length];  //e_w----��ʱ����
		for (int i = 0; i < r_bits.length; i++) {
			if (r_bits[i]==true) {
				BigInteger e_one = paillier.Encryption(one);
				e_w[i] = e_one.multiply(e_d_bits[i].modInverse(paillier.nsquare).mod(paillier.nsquare));
			} else {
				e_w[i] = e_d_bits[i];
			}
		}
		
		// sumw[i] = Sum_{j=i+1}^{M}(w[i])  20190801
		BigInteger[] e_sumw = new BigInteger[e_w.length];   //e_sumw--��ʱ����
		e_sumw[e_w.length-1] = paillier.Encryption(zero);
		for (int i = e_d_bits.length-2; i >= 0; i--) {
			e_sumw[i] = e_sumw[i+1].multiply(e_w[i+1]).mod(paillier.nsquare);
		}
		
		// choose s \in {-1, +1} randomly
		Random random = new SecureRandom();
		BigInteger s = random.nextBoolean() ? minusOne : one;//��ʱ����
		BigInteger e_s = paillier.Encryption(s);//��ʱ����
		
		//TODO: remove debug
		//System.out.println("e_s decrypted: "+Damgard.Decrypt(e_s, key));				
		
		// c[i]  = d_i - r_i + s + 3*sumw[i]  20190801
		BigInteger[] e_c = new BigInteger[r_bits.length];  //e_c--ͳ�Ʊ���
		for (int i = 0; i < r_bits.length; i++) {
			e_c[i] = e_d_bits[i].multiply(e_mr_bits[i]).mod(paillier.nsquare).multiply(e_s).mod(paillier.nsquare).multiply(e_sumw[i].modPow(three, paillier.nsquare)).mod(paillier.nsquare);
		}
		
		// mask each e_c[i] with random even t[i] (that is, t[i] is coprime to 2^Lbit) 
		// and rerandomize e_c[i]
		
		
	//	System.out.println(" paillier.bitLength"+paillier.bitLength);
		
		
		BigInteger[] t = new BigInteger[r_bits.length];//t--��ʱ����
		for (int i = 0; i < r_bits.length; i++) {
			t[i] = new BigInteger(paillier.bitLength-1, random).setBit(0);
			
			
			
		//	System.out.println("e_c[i]1+"+paillier.Decryption(e_c[i]).toString());
			e_c[i] = e_c[i].modPow(t[i], paillier.nsquare);
		//	e_c[i] = ReRandomize(e_c[i], key);
			
		//	System.out.println("t[i]+"+paillier.Decryption(t[i]).toString());
		//	System.out.println("e_c[i]2+"+paillier.Decryption(e_c[i]).toString());
		}
		
		
		
		timeForBob += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
		// ask AliceMsg, if e_c contains encrypted zero. answer is encrypted
		BigInteger e_lambda_hat = DoesContainEncryptedZero(e_c,paillier); //e_lambda_hat--��ʱ����
		BigInteger e_lambda;	
		
		timeForAlice += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
		
	//	System.out.println("e_lambda_hat+"+paillier.Decryption(e_lambda_hat).toString());
		
		
		// lambda = lambda_hat XOR (!s)
		// that is, lambda = 1-lambda_hat if s==-1

		//if S=1�����D>R��ȫ���Ƿ�0��e_lambda_hatӦ����0��e_lambdaҲҪ����0����e_lambda=e_lambda_hat
			//���R>D����,��һ����0��e_lambda_hatӦ����1��e_lambdaҲҪ����1����e_lambda=e_lambda_hat

		//if S=-1�����R>D��ȫ���Ƿ�0��e_lambda_hatӦ����0��e_lam bdaҲҪ����1����e_lambda=-e_lambda_hat
		//	���D>R����,��һ����0��e_lambda_hatӦ����1��e_lambdaҲҪ����0����e_lambda=-e_lambda_hat


		if (s.equals(one)) {
			e_lambda = e_lambda_hat;
		} else {
			e_lambda = paillier.Encryption(one).multiply(e_lambda_hat.modInverse(paillier.nsquare));
		}

	//	System.out.println("e_lambda:"+paillier.Decryption(e_lambda).toString());
	//	System.out.println("s:"+s);
	//	System.out.println("e_s:"+paillier.Decryption(e_s).toString());
		
		//TODO: remove debug
		//System.out.println("e_lambda_hat decrypted: "+Damgard.Decrypt(e_lambda_hat, key));		
		//System.out.println("e_lambda decrypted: "+Damgard.Decrypt(e_lambda, key));				
		
		timeForBob += System.currentTimeMillis() - start;
		return e_lambda;
	}
	
	
	/*
	 * Given an array of encrypted values, return:
	 *    Encrypt(one) if one of those values contains zero.
	 *    Encrypt(zero) if all values are   
	 */
	public static BigInteger DoesContainEncryptedZero(BigInteger[] e_array,Paillier paillier) {
	
		for (BigInteger e_value : e_array) {
			if (IsEncryptedZero(e_value,paillier)) {
				return paillier.Encryption(one);
			}
		}
		return paillier.Encryption(zero);
	}

	
	
	//-------------------------------------------------------�����Ǽ������Ͼ���-----------------------------------------------
	/**
	 * Returns an encryption of EuclideanDistance
	 *
	 *  
	 * @param e_AliceMsg��Alice���ܵ���Ϣ��BobMsg���Լ��������Ϣ��������
	 * @param paillier
	 * @return AliceMsg��BobMsg��ŷ����þ���
	 */

	public static BigInteger MSDistance(BigInteger[] e_AliceMsg, int[] BobMsg,int [][] Cmatric,Paillier paillier) 
		{

			int BobMsgCmatric;
			BigInteger tmp = null;
			BigInteger tmp1 = null;
			BigInteger tmp2 = null;
			BigInteger ed = BigInteger.ONE;
			BigInteger ed2 = BigInteger.ONE;

			BigInteger[] e_B = new BigInteger[BobMsg.length];

			//�ȼ�����˳�e_B
			for(int i = 0; i<BobMsg.length; i++)
			{
				ed2 = BigInteger.ONE;
				for(int j = 0; j<BobMsg.length; j++)
				{
					BobMsgCmatric=Cmatric[j][i]*BobMsg[j];	
					tmp =paillier.Encryption(BigInteger.valueOf(BobMsgCmatric));
	//				System.out.println("tmp" + i + ": " + paillier.Decryption(tmp));				
							
					tmp1 = e_AliceMsg[j].modInverse(paillier.nsquare); //tmp1  = - e_AliceMsg
					tmp1 = tmp1.modPow(BigInteger.valueOf(Cmatric[j][i]),paillier.nsquare); //tmp1 = -e_AliceMsg*Cmatric
					
					tmp2 =tmp1.multiply(tmp); 
					tmp2 = tmp2.mod(paillier.nsquare);//tmp2= Cmatric[j][i]*BobMsg[j]-e_AliceMsg[J]*Cmatric[j][i]
					ed2=ed2.multiply(tmp2);
					ed2=ed2.mod(paillier.nsquare);
	//				System.out.println("tmp" + i + ": " + paillier.Decryption(tmp));	
				}
				e_B[i]=ed2;
			}

			
			//���ҳ˼��������
			for(int i=0; i<BobMsg.length;i++)
			{
				tmp =e_B[i].modPow(BigInteger.valueOf(BobMsg[i]),paillier.nsquare); //tmp1 = [e_B[i]*BobMsg[i]]
				
				BigInteger AliceMsgtmp;
				BigInteger randoms2;
				BigInteger randoms3;
				BigInteger e_randoms2;
				BigInteger e_randoms3;
				BigInteger temp3;
				BigInteger temp4;
				BigInteger temp6;
				BigInteger temp5;
				BigInteger temp7;

				//������������������ڼ������ĵ����Э��
				Random random2 = new SecureRandom();
				Random random3 = new SecureRandom();
				randoms2 = new BigInteger(BobMsg.length, random2);
				randoms3 = new BigInteger(BobMsg.length, random2);
					
				
				e_randoms2=paillier.Encryption(randoms2); //����randoms2
				e_randoms3=paillier.Encryption(randoms3); //����randoms3
				
				temp7=randoms2.multiply(randoms3).multiply(minusOne);
				temp7=paillier.Encryption(temp7);//-c1*c2
				
				temp3=e_AliceMsg[i].multiply(e_randoms2).mod(paillier.nsquare); // C4*C1
				temp4=e_B[i].multiply(e_randoms3).mod(paillier.nsquare); //C5*C2
				
				temp3=paillier.Decryption(temp3);  
				temp4=paillier.Decryption(temp4);
				
				temp6=paillier.Encryption(temp3.multiply(temp4));
				
				tmp1=e_AliceMsg[i].modPow(randoms3.multiply(minusOne),paillier.nsquare);   //-c1*c5
				temp5=e_B[i].modPow(randoms2.multiply(minusOne),paillier.nsquare);  //-c2*c4
				
				temp5=tmp1.multiply(temp5).mod(paillier.nsquare);   //temp5=-c1*c5-c2*c4
				temp5=temp5.multiply(temp7).multiply(temp6).mod(paillier.nsquare);   //temp5=(C4+C1)(C5+C2)-c1*c5-c2*c4-c1*c2
				
	
				temp5 = temp5.modInverse(paillier.nsquare); //temp5  = - temp5   =-e_AliceMsg[J]*e_B[i]
				tmp =e_B[i].modPow(BigInteger.valueOf(BobMsg[i]),paillier.nsquare); //tmp1 = [e_B[i]*BobMsg[i]]
				
				temp5 =temp5.multiply(tmp); 
				temp5 = temp5.mod(paillier.nsquare);//temp5= BobMsg[j][i]*e_B[i]-e_AliceMsg[J]*e_B[i]
				
				ed=ed.multiply(temp5);
				ed= ed.mod(paillier.nsquare);  //ed���ľ���
			}
		
			return ed; //����̬ͬ���ܵ����Ͼ���
		}
	
	//-------------------------------------------------------���Ͼ������-----------------------------------------------
	//-------------------------------------------------------��ʼС���任----------------------------------------------
	//����aliceͼƬ���õ�С���任ϵ������
	public static BigInteger[] DWT_ALICE(int[] AliceMsg1,BigInteger[] e_AliceMsg1,Paillier paillier) 
	{
		//Paillier paillier = new Paillier();
		BigInteger Zero = new BigInteger("0");
        BigInteger encryptedZero;

	
        
	        BigInteger [] dwte_AliceMsg = new BigInteger[AliceMsg1.length];
	  //      BigInteger [] dwtre_AliceMsg = new BigInteger[AliceMsg.length];//С����任ϵͳ��û�á�
	        
	        BigInteger [] return_AliceMsg = new BigInteger[AliceMsg1.length/8];
	        
	        
			  /* ��ʼ��С���任*/
	        
			encryptedZero = paillier.Encryption(Zero);//ʱ�临�Ӷ�--1��
			dwt h = new dwt(encryptedZero);
			
	/*		
			for(int i=0; i<10;i++)
			{
				System.out.println("ûС���任ǰ��������� " + i + ": " + paillier.Decryption(e_AliceMsg1[i]));
			}*/
			dwte_AliceMsg=h.haarDe(3,e_AliceMsg1,paillier.nsquare);//ʱ�临�Ӷ�--haarDe����
			 /* ���С���任��ϵ��*/
			for(int i=0; i<return_AliceMsg.length;i++)
			{
				return_AliceMsg[i]=dwte_AliceMsg[i];
			}
			return return_AliceMsg;
	}
	
	public static double [][] FileTobobAry(int NumBobMsg6,int NumBoblength) throws Exception 
	{
		double [][] BobMsgread=new double[NumBobMsg6][NumBoblength]; 
		BufferedReader brbob = new BufferedReader(new InputStreamReader(new FileInputStream("d:\\PICTER\\testbob3.txt"),"latin1"));//ʹ��BufferedReader ���ô��ǿ��԰��ж�ȡ,ÿ�ζ�ȡһ��
		int indexbob = 0;//����
	        String temp;//�����ַ���,���ڱ���ÿ�ж�ȡ��������
	        while ((temp = brbob.readLine()) != null) {
	        	double[] ary = aryChange(temp);//ͨ���������ַ��������������������
	            BobMsgread[indexbob] = ary;
	            indexbob++;
	    }     
	    brbob.close();// �ر�������  
	    return BobMsgread;
	}
	public static double [][] FileTouAry(int uvectornumber,int NumBoblength) throws Exception 
	{
		double [][] udoublegread=new double[uvectornumber][NumBoblength]; 
		BufferedReader bru = new BufferedReader(new InputStreamReader(new FileInputStream("d:\\PICTER\\testu3.txt"),"latin1"));//ʹ��BufferedReader ���ô��ǿ��԰��ж�ȡ,ÿ�ζ�ȡһ��
		int indexu = 0;//����
	        String temp;//�����ַ���,���ڱ���ÿ�ж�ȡ��������
	        while ((temp = bru.readLine()) != null) {	       
	        	double[] ary = aryChange(temp);//ͨ���������ַ��������������������
	        	udoublegread[indexu] = ary;
	            indexu++;
	    }     
	    bru.close();// �ر�������  
	    return udoublegread;
	} 
	public static double [][] FileToaliceAry(int NumALICElength) throws Exception 
	{
		double [][] aliceMsgread=new double[40][NumALICElength]; 
		BufferedReader bralice = new BufferedReader(new InputStreamReader(new FileInputStream("d:\\PICTER\\testalice-junzhi2.txt"),"latin1"));//ʹ��BufferedReader ���ô��ǿ��԰��ж�ȡ,ÿ�ζ�ȡһ��
		int indexalice = 0;//����
	        String temp;//�����ַ���,���ڱ���ÿ�ж�ȡ��������
	        while ((temp = bralice.readLine()) != null) {
	        	double[] ary = aryChange(temp);//ͨ���������ַ��������������������
	        	aliceMsgread[indexalice] = ary;
	            indexalice++;
	    }     
	    bralice.close();// �ر�������  
	    return aliceMsgread;
	}
	static double[] aryChange(String temp) {// �ַ������������double����
		  String[] ss = temp.trim().split("\\s+");// .trim()����ȥ����β����Ŀո�
		                                                // .split("\\s+")
		                                                // ��ʾ��������ʽȥƥ���и�,\\s+��ʾƥ��һ���������ϵĿհ׷�
		  double[] ary = new double[ss.length];
		  double a;
		  for (int i = 0; i < ary.length; i++) {
			  ary[i] = Double.parseDouble(ss[i]);// ���������ÿһ��Ԫ��
		     // System.out.println("ary " + i + ": " + ary[i]);
		  }
		   return ary;// ����һ��double����
	}	        
	        
}

