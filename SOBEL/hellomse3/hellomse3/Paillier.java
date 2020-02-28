package com.test.hellomse3;

/**
* 这里是比较快的做法，从TXT里面读入数据
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
import java.util.Scanner; //这里加一句
import java.util.Arrays;
import java.util.Comparator;
/**
1、通过网站下载图片，通过matlab，将每个图片分解成向量；
2、通过matlab或者java，将图片库里的向量组成矩阵A，并求出PCA；
3、将PCA运用到W计算，计算出库BOB的W和ALICE的W；
4、计算库BOB的W和ALICE（密文）的W之间的欧几里得距离（加密）；
5、比较加密距离，得出比较小的距离对应的BOB的索引；
6、ReRandomize、模板s、bob库里的向量建立索引；

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
   
  		/* --------------------------------------------定义统一变量------------------------------------------------------------- */
		int NumBobMsg6=400;
		int NumBoblength=1288;
		int uvectornumber=300;
		int NumALICElength=10304;
		int Nummindintance=10;
		//int Numofface=6;  //第几张alice人脸
		BigInteger m3= new BigInteger("40");//数值的长度不够，或者值负太多，相乘的时候，负溢出。
		double SS= 0.07;//设置模板等于1000000，变化的时候U要变  ;PCA的时候double SS= 0.07;
		/* --------------------------------------------定义统一变量------------------------------------------------------------- */
      
		/* -------------------------------------------开始读取和处理BOB------------------------------------------------------------ */	
		
		/* 设置BOb已有的向量BobMsg-BobMsg6，及AliceMsg	*/	
		double [][] BobMsgdouble=new double[NumBobMsg6][NumBoblength];  //定义为9*6，即6个1*9的一维向量，每个为一个图片，一共6个图片、
		double [][] udouble=new double[uvectornumber][NumBoblength]; 
		double [][] AliceMsgdoubleall= new double[40][NumALICElength];
		double [] AliceMsgdouble= new double[NumALICElength];
		double [][] Cmatricdouble=  new double[uvectornumber][uvectornumber];
		/*开始读入txt数据：*/
		
		BobMsgdouble=FileTobobAry(NumBobMsg6,NumBoblength);
		udouble=FileTouAry(uvectornumber,NumBoblength);
		AliceMsgdoubleall=FileToaliceAry(NumALICElength);
		
		 //下面通过SS将double型的扩大，方便进行paillier运算	
		int [][] BobMsg= new int[NumBobMsg6][NumBoblength];
		int [][] u= new int[uvectornumber][NumBoblength];
		int [][] Cmatric= new int[uvectornumber][uvectornumber];
		
		
		/*--------------------------------------------------------- 下面通过SS开始扩大所有的数	----------------------------------------*/
		for(int i=0; i<BobMsg.length;i++)
		{
			for(int j=0;j<BobMsg[1].length;j++)
			{
				//System.out.println("BobMsg " + i+"空" +j+ ": " + BobMsgdouble[i][j]);
				BobMsg[i][j]=(int)(BobMsgdouble[i][j]*SS*2.828);//将每一个值进行扩大
		//		System.out.println("BobMsg " + i +j+ ": " + BobMsg[i][j]);
			}
		}
		
		for(int i=0; i<u.length;i++)
		{
			for(int j=0;j<u[0].length;j++)
			{
				
			//	System.out.println("udouble " + i+"  " +j+ ": " + udouble[i][j]);
					
				u[i][j]=(int)(udouble[i][j])/16; // PCA的时候再* 80;
			//	u[i][j]=(int)(udouble[i][j]);// LFDA不用	
			//	System.out.println("u " + i+"  " +j+ ": " + u[i][j]);
			}
		}
		
		
		/* -------------------------------------------结束读取和处理BOB------------------------------------------------------------ */	
		/* -------------------------------------------开始循环读取和处理ALICE------------------------------------------------------------ */	
		int sumaccuracy=0;//初始化总命中的个数为0
		double accuracysumrate=0.00;//初始化总准确率为0
		double recallsumrate=0.00;//初始化总召回率为0
		for(int Numofface=1;Numofface<=40;Numofface++)
        {
		
			Paillier paillier = new Paillier();
			BigInteger m4 = new BigInteger("1");	
			
			AliceMsgdouble=AliceMsgdoubleall[Numofface-1];
			
			int [] AliceMsg= new int [NumALICElength];
			for(int j=0;j<AliceMsg.length;j++)
			{
			//	System.out.println("AliceMsgdouble " +j+ ": " + AliceMsgdouble[j]);
				AliceMsg[j]=(int)(AliceMsgdouble[j]*SS);//将每一个值进行扩大
				
			}
			/*--------------------------------------------------------- 扩大完毕，通过PCA计算欧式距离	----------------------------------------------------------------------------------------------*/
			//Alice加密元图像的每一位e_AliceMsg
			
			BigInteger [] e_AliceMsg = new BigInteger[AliceMsg.length]; //biginteger array that contains x
			BigInteger [] we_AliceMsg = new BigInteger[uvectornumber]; //biginteger array that contains x
			int a;
			int temps=0;
			BigInteger tempss;
			
			/*计算B0b库里的平均值Ψ，放到AverageBOb，并计算加密的AverageBOb*/
			int []AverageBOb= new int[NumBoblength]; 
			BigInteger[] e_AverageBOb = new BigInteger[AverageBOb.length];

			for(int i=0; i<AverageBOb.length;i++)
			{
				double sumBOb=0;
				for(int j=0;j<NumBobMsg6;j++)
				{
					sumBOb=sumBOb+BobMsg[j][i];//将Bob库里的向量累加起来
				}
				
					sumBOb= sumBOb/NumBobMsg6;
					AverageBOb[i] =(int)sumBOb;
					e_AverageBOb[i] = paillier.Encryption(BigInteger.valueOf(AverageBOb[i]));//时间复杂度--1288个Encryption
			}
			
			/*根据计算BOB库里的向量W*/
			int [][]WBobMsg= new int[NumBobMsg6][uvectornumber]; //每维扩成u的个数

			for(int k=0;k<NumBobMsg6;k++)
			{
				for(int i=0; i<u.length;i++)
				{
				
					WBobMsg[k][i]=0;
					for(int j=0; j<AverageBOb.length;j++)
					{
						temps=BobMsg[k][j]-AverageBOb[j];
						temps=u[i][j]*(BobMsg[k][j]-AverageBOb[j]); //U的转置乘以差值
						WBobMsg[k][i]=WBobMsg[k][i]+temps;
					}
				}
			}
			
			
			for(int i=0; i<AliceMsg.length;i++)
			{
				temps = AliceMsg[i]; 
				e_AliceMsg[i] = paillier.Encryption(BigInteger.valueOf(temps)); //时间复杂度--10304个Encryption
				a=sizeof(e_AliceMsg[i]);
			//	System.out.println("a*** " + i + ": " + a);
			}
			
			/*传入通过AliceMsg和AliceMsg的密文，进行小波分解，获得加密的小波密文给bob*/
			e_AliceMsg=DWT_ALICE(AliceMsg,e_AliceMsg,paillier);
			
			/*Alice通过加密的值，计算加密的向量W，得到we_AliceMsg*/
			for(int i=0; i<u.length;i++)
			{
	
				BigInteger sumtempss= BigInteger.ONE;
	
				for(int j=0; j<e_AliceMsg.length;j++)
				{

					tempss=e_AliceMsg[j].multiply((e_AverageBOb[j]).modInverse(paillier.nsquare));  //[I] · [?Ψ1] 时间复杂度

					tempss =tempss.modPow(BigInteger.valueOf(u[i][j]),paillier.nsquare); 	// [Φ1]^u  时间复杂度

					sumtempss=sumtempss.multiply(tempss).mod(paillier.nsquare);//累乘 [Φ1]^u作为Alice的第i个W值  时间复杂度
			
				}
				we_AliceMsg[i]= sumtempss.mod(paillier.nsquare);  //时间复杂度
			}
			
			/*--------------------------------------------------------- 计算欧式距离	/马氏距离----------------------------------------------------------------------------------------------*/
					
			BigInteger [] em=new BigInteger[NumBobMsg6];
			
			/* 测试计算Alice和BOB的欧几里得距离*/
			for(int k=0;k<NumBobMsg6;k++)
			{
			
				em[k]=EuclideanDistance(we_AliceMsg,WBobMsg[k],paillier);
	
			}
		

			/*--------------------------------------------------------- 比较欧式距离	/马氏距离----------------------------------------------------------------------------------------------*/
			
			/* 
			 *  测试比较欧几里得距离
			 */
			
			//先备份一个em出来，用于排序
			BigInteger [] embak=new BigInteger[NumBobMsg6];
			for(int mn=0;mn<NumBobMsg6;mn++) 
			{
				embak[mn]=em[mn];					
			}
			for(int mn=0;mn<NumBobMsg6;mn++) 
			{
						System.out.println("排序前embak第"+mn+"个最近的距离为："+paillier.Decryption(embak[mn]).toString());
			}
			//先通过函数排序
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
						System.out.println("第"+mm+"个最近的距离为："+paillier.Decryption(embak[mm]).toString()+"，是输入的第 "+mins[mm]+"个");
						
					}
				}
			}
			System.out.println("--------------------------------------------------------------------------------"+Numofface);
			System.out.println("Numofface次数："+Numofface);
			//计算每次alice循环准确的个数
			int [] accuracy=new int[NumBobMsg6];   
			int [] wrong=new int[NumBobMsg6]; 
			int maxlimit=Numofface*10;
			int minlimit=(Numofface-1)*10+1;
			int Numoffacebak=Numofface-1;
			for(int cc=0;cc<Nummindintance;cc++) 
			{
				int b=mins[cc];
				if((b<=maxlimit)&&(b>=minlimit))  //在界限内，命中
					accuracy[Numoffacebak]++;
				else
					wrong[Numoffacebak]++;
				
			}
			System.out.println("maxlimit  "+maxlimit+"minlimit"+minlimit+"accuracy  "+accuracy[Numoffacebak]+"wrong  "+wrong[Numoffacebak]);
			sumaccuracy=sumaccuracy+accuracy[Numoffacebak];
			System.out.println("timeForAlice  "+timeForAlice+"timeForBob  "+timeForBob+"timeForAlice2  "+timeForAlice2+"timeForBob2  "+timeForBob2);
			
        }
		System.out.println("输出最后结果");
		//最后计算准确率和召回率	
		accuracysumrate=(double)(sumaccuracy/(Nummindintance*40));
		recallsumrate=(double)(sumaccuracy/400);
		
		System.out.println("sumaccuracy  "+sumaccuracy+"accuracysumrate  "+accuracysumrate+"recallsumrate  "+recallsumrate);
		System.out.println("timeForAlice  "+timeForAlice+"timeForBob  "+timeForBob+"timeForAlice2  "+timeForAlice2+"timeForBob2  "+timeForBob2);
		
		
	}
	
	
	/*--------------------------------------------------------- 结束主函数/剩余的其他调用子函数----------------------------------------------------------------------------------------------*/
	
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

	//-------------------------------------------------------下面是计算欧几里得/马氏距离-----------------------------------------------
	
	/**
	 * Returns an encryption of EuclideanDistance
	 *
	 *  
	 * @param e_AliceMsg，Alice加密的消息，BobMsg，自己库里的消息，是明文
	 * @param paillier
	 * @return AliceMsg和BobMsg的欧几里得距离
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


			BigInteger sumx= null;  //x数组的和
			BigInteger e_sumx= null;  //加密的x数组的和

			BigInteger [] randoms= new BigInteger [BobMsg.length];  //随机数数组 randoms
			BigInteger [] e_randoms= new BigInteger [BobMsg.length];  //加密的随机数数组 e_randoms

			BigInteger[] x= new BigInteger[BobMsg.length];  //x数组
			BigInteger[] e_x= new BigInteger[BobMsg.length];  //加密的x数组


			//BobMsg可以直接加密，因为BOB有BobMsg的原值，下面是计算S1的每一位，存在e_BobMsgSquared[i]，加起来的和就是S1
			for(int i = 0; i<BobMsg.length; i++)
			{
				sMessage = BobMsg[i];
				sMessage = sMessage*sMessage;
				
		//		System.out.println("BobMsg.length " + ": " + BobMsg.length);
				
				e_BobMsgSquared[i] =paillier.Encryption(BigInteger.valueOf(sMessage));  //时间复杂度
				//	System.out.println("BobMsg^2 " + i + ": " + paillier.Decryption(e_BobMsgSquared[i]));
			}

			
			//e_AliceMsg不可以直接平方，BOB要与ALIECE再交互一次，下面是计算S3的开始
			//1、BOB先产生一个e_x[i]数组
			for(int i=0; i<BobMsg.length;i++)
			{
				Random random = new SecureRandom();
				
				//随机数的长度太长，会导致解密的时候，距离变成负数或者超出，导致无法解密
				randoms[i] = new BigInteger(BobMsg.length/50, random);
				
				e_randoms[i]=paillier.Encryption(randoms[i]); //加密第i个随机数  时间复杂度
				e_x[i]=e_AliceMsg[i].multiply(e_randoms[i]).mod(paillier.nsquare);  //时间复杂度
				
				//	System.out.println("e_randoms " + i + ": " + paillier.Decryption(e_randoms[i])+"  e_AliceMsg " + i + ": " + paillier.Decryption(e_AliceMsg[i])+"  e_x " + i + ": " + paillier.Decryption(e_x[i]));
			}
			
			timeForBob2 +=System.currentTimeMillis()-start2;
			start2 = System.currentTimeMillis();
			int b;
			//System.out.println("b*** "  + ": " + e_x[1].bitLength());
			
			
			//2、ALICE对e_x[i]解密，计算X的累加和的加密e_sumx给BOB
			sumx=zero;
			for(int i=0; i<BobMsg.length;i++)
			{
				tmp=paillier.Decryption(e_x[i]);  //时间复杂度
				tmp=tmp.multiply(tmp);//明文域，不用mod  
				sumx= sumx.add(tmp);  
			//	System.out.println("sumx " +  ": " + sumx);
			}
			
			e_sumx=paillier.Encryption(sumx); //这是最终算出的e_sumx的加密  时间复杂度
		//	System.out.println("e_sumx " + ": " + paillier.Decryption(e_sumx));

			timeForAlice2 +=System.currentTimeMillis()-start2;
			start2 = System.currentTimeMillis();
			
			//3、BOB再计算S3的和，先按公式计算前面截 时间复杂度
			for(int i=0; i<BobMsg.length;i++)
			{
							
				tmp1 = e_AliceMsg[i].modPow(BigInteger.valueOf(randoms[i].intValue()),paillier.nsquare); //tmp1 = [r^e_AliceMsg]
				tmp1 = tmp1.modPow(two,paillier.nsquare ); //tmp1 = [2e_AliceMsg*r]
					
				tmp2=randoms[i].multiply(randoms[i]).mod(paillier.nsquare);  // .modInverse(paillier.nsquare); //ri的平方
				tmp2 =paillier.Encryption(tmp2);//ri的平方的加密
				
				ed=ed.multiply(tmp1.modInverse(paillier.nsquare)).multiply(tmp2.modInverse(paillier.nsquare));  //-ri的平方-r^e_AliceMsg
				ed= ed.mod(paillier.nsquare);
				

				
			//	System.out.println("ed " + ": " + paillier.Decryption(ed));//负数健米不出来
			}
			
			e_sumx=e_sumx.multiply(ed); //这是最终算出的S3的加密
			e_sumx= e_sumx.mod(paillier.nsquare);

			//	System.out.println("e_sumx " + ": " + paillier.Decryption(e_sumx));
			
			//下面是根据公式(x-y)^2= x^2-2xy+y^2，利用上面的结果算出所有
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
			
			//	System.out.println("ed2 " + ": " + paillier.Decryption(ed2));//这是最终算出的S2的加密
			
			
			ed2=e_sumx.multiply(ed2); //这是最终算出的S3+s2+s1
			ed2= ed2.mod(paillier.nsquare);

			//System.out.println("ed2 2" + ": " + paillier.Decryption(ed2));//这是最终算出的S1+S2+S3的加密
			
			timeForBob2 +=System.currentTimeMillis()-start2;
			start2 = System.currentTimeMillis();
			
			return ed2;
		}
	
	
	//-------------------------------------------------------下面是比较欧几里得距离-----------------------------------------------
	
	
	/**
	 * Returns true if em is an encryption of zero under the key. 
	 * This method is much faster than Decrypt.
	 *  
	 * @param e_value
	 * @param key
	 * @return
	 * // tmp = em^(vp*vq) mod n 对于DGK可以，对于同态加密测试不可以，如果解密了是0，则返回1，不是返回0
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
		Random random = new SecureRandom();//random--临时变量
		
		
		StartCounting(); 
		long start = System.currentTimeMillis();
		
		// z = 2^M + a - b  20190801
		BigInteger twoToM = BigInteger.valueOf(2).pow(M.intValue()); //twoToM--临时变量

		BigInteger e_twoToM = paillier.Encryption(twoToM); //e_twoToM--临时变量  20190801
		
		
		BigInteger e_z = e_twoToM.multiply(a).mod(paillier.nsquare).multiply(b.modInverse(paillier.nsquare)).mod(paillier.nsquare);
	
		//e_z--临时变量  20190801
//		System.out.println("2^M值"+twoToM.toString());
		
	//	System.out.println("z值 "+paillier.Decryption(e_z).toString());
		// d = z + r，产生一个位数不长于2^8的一个随机数r
		BigInteger r = new BigInteger(M.add(kappa).intValue(), random);//z--临时变量
		
		
		BigInteger e_r = paillier.Encryption(r); //e_r--临时变量   20190801
		BigInteger e_d = e_z.multiply(e_r).mod(paillier.nsquare); //e_d--临时变量  20190801
		//这个ReRandomize后面要做	e_d = ReRandomize(e_d, key); 

		timeForBob +=System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
//		System.out.println("r值 " +paillier.Decryption(e_r).toString());
	//	System.out.println("d值 " +paillier.Decryption(e_d).toString());
		
		
		// reduce d to (d mod 2^M)
		DForComparisonResult dForComparison = CompareEncrypted_GetDMod2M_DBits_Encrypted(e_d, M,paillier);
		
		timeForAlice += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();

		BigInteger e_d_hat = dForComparison.d; //e_d_hat-临时变量(给e_z_tilde）
		BigInteger[] e_d_bits = dForComparison.d_i;//e_d_bits--统计变量
		
//		System.out.println("d mod 2^m "+paillier.Decryption(dForComparison.d).toString());
		
		// z_tilde = (d mod 2^M) - (r mod 2^M)
		BigInteger r_hat = r.mod(twoToM); //r_hat-临时变量
		BigInteger e_r_hat = paillier.Encryption(r_hat); //e_r_hat-临时变量  20190801
		BigInteger e_z_tilde = e_d_hat.multiply(e_r_hat.modInverse(paillier.nsquare)).mod(paillier.nsquare);//e_z_tilde-临时变量  20190801
		
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
		BigInteger r_hat_comparison = r_hat.multiply(two);  //r_hat_comparison-临时变量
		boolean[] r_bits = new boolean[M.intValue()+1];  //r_bits-需要统计（明文）
		for (int i = 0; i < M.intValue()+1; i++) {
			r_bits[i] = r_hat_comparison.testBit(i) ? true : false;
		}
		
		timeForBob+=System.currentTimeMillis()-start;
		BigInteger e_lambda = CompareBitArrays(e_d_bits, r_bits,paillier); //e_lambda-临时变量
		start = System.currentTimeMillis();
		
		// fix possible underflow
		// (z mod 2^M) = z_tilde + lambda*2^M   20190801
		BigInteger e_z_mod = e_z_tilde.multiply(e_lambda.modPow(twoToM, paillier.nsquare)).mod(paillier.nsquare);
		//e_z_mod-临时变量
		
		// z[l] = 2^(-M)*(z - (z mod 2^M))
		// ! it is ok to just use (z - (z mod 2^M)), we get 2^M*(z_l)  20190801
		BigInteger e_z_l = e_z.multiply(e_z_mod.modInverse(paillier.nsquare));	//e_z_l-统计变量

		// TODO: remove debug
		//System.out.println("e_z_mod decrypted: "+Damgard.Decrypt(e_z_mod, key));			
		//System.out.println("e_z_l decrypted: "+Damgard.Decrypt(e_z_l, key));
		
		timeForBob += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
		//这里的移位可以不用做，相当于比较100000和0000000
//		System.out.println(" 2^M*(z_l) "+paillier.Decryption(e_z_l).toString());
		
		
		// AliceMsg can decrypt the result and find out, if a<b or not.
		boolean isEncryptedZero = IsEncryptedZero(e_z_l,paillier);	//isEncryptedZero-临时变量
		
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
		BigInteger decrypted = paillier.Decryption(d);   //decrypted--临时变量   20190801
		BigInteger dMod2M = decrypted.mod(two.pow(M.intValue()));  //dMod2M--统计变量（局部变量不算）
		
		
	//	System.out.println("dMod2M " +dMod2M.toString());
	
		
		
		BigInteger dModForComparison = dMod2M.multiply(two).add(one);//dModForComparison--临时变量
		
	//	System.out.println("dMod2M*2+1 " +dModForComparison.toString());
			
	//	System.out.println("dMod2M*2+1 " +dModForComparison);
		
		BigInteger[] d_i = new BigInteger[M.intValue()+1]; //d_i--统计变量（局部变量不算）
		for (int i = 0; i < M.intValue()+1; i++) {
			boolean bitValue = dModForComparison.testBit(i) ? true : false;  //bitValue--临时变量
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
		BigInteger[] e_mr_bits = new BigInteger[r_bits.length];//e_mr_bits--临时变量
		for (int i = 0; i < r_bits.length; i++) {
			BigInteger bitValue = r_bits[i] ? one : zero;
			BigInteger minusBitValue = r_bits[i] ? minusOne : zero;
		//	e_r_bits[i] = paillier.Encryption(bitValue);
			e_mr_bits[i] = paillier.Encryption(minusBitValue); 
		}

		// w[i] = d[i] XOR r[i]   20190801
		BigInteger[] e_w = new BigInteger[r_bits.length];  //e_w----临时变量
		for (int i = 0; i < r_bits.length; i++) {
			if (r_bits[i]==true) {
				BigInteger e_one = paillier.Encryption(one);
				e_w[i] = e_one.multiply(e_d_bits[i].modInverse(paillier.nsquare).mod(paillier.nsquare));
			} else {
				e_w[i] = e_d_bits[i];
			}
		}
		
		// sumw[i] = Sum_{j=i+1}^{M}(w[i])  20190801
		BigInteger[] e_sumw = new BigInteger[e_w.length];   //e_sumw--临时变量
		e_sumw[e_w.length-1] = paillier.Encryption(zero);
		for (int i = e_d_bits.length-2; i >= 0; i--) {
			e_sumw[i] = e_sumw[i+1].multiply(e_w[i+1]).mod(paillier.nsquare);
		}
		
		// choose s \in {-1, +1} randomly
		Random random = new SecureRandom();
		BigInteger s = random.nextBoolean() ? minusOne : one;//临时变量
		BigInteger e_s = paillier.Encryption(s);//临时变量
		
		//TODO: remove debug
		//System.out.println("e_s decrypted: "+Damgard.Decrypt(e_s, key));				
		
		// c[i]  = d_i - r_i + s + 3*sumw[i]  20190801
		BigInteger[] e_c = new BigInteger[r_bits.length];  //e_c--统计变量
		for (int i = 0; i < r_bits.length; i++) {
			e_c[i] = e_d_bits[i].multiply(e_mr_bits[i]).mod(paillier.nsquare).multiply(e_s).mod(paillier.nsquare).multiply(e_sumw[i].modPow(three, paillier.nsquare)).mod(paillier.nsquare);
		}
		
		// mask each e_c[i] with random even t[i] (that is, t[i] is coprime to 2^Lbit) 
		// and rerandomize e_c[i]
		
		
	//	System.out.println(" paillier.bitLength"+paillier.bitLength);
		
		
		BigInteger[] t = new BigInteger[r_bits.length];//t--临时变量
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
		BigInteger e_lambda_hat = DoesContainEncryptedZero(e_c,paillier); //e_lambda_hat--临时变量
		BigInteger e_lambda;	
		
		timeForAlice += System.currentTimeMillis()-start;
		start = System.currentTimeMillis();
		
		
	//	System.out.println("e_lambda_hat+"+paillier.Decryption(e_lambda_hat).toString());
		
		
		// lambda = lambda_hat XOR (!s)
		// that is, lambda = 1-lambda_hat if s==-1

		//if S=1，如果D>R，全部是非0，e_lambda_hat应该是0；e_lambda也要返回0，则e_lambda=e_lambda_hat
			//如果R>D，则,有一个是0，e_lambda_hat应该是1，e_lambda也要返回1，则e_lambda=e_lambda_hat

		//if S=-1，如果R>D，全部是非0，e_lambda_hat应该是0；e_lam bda也要返回1，则e_lambda=-e_lambda_hat
		//	如果D>R，则,有一个是0，e_lambda_hat应该是1，e_lambda也要返回0，则e_lambda=-e_lambda_hat


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

	
	
	//-------------------------------------------------------下面是计算马氏距离-----------------------------------------------
	/**
	 * Returns an encryption of EuclideanDistance
	 *
	 *  
	 * @param e_AliceMsg，Alice加密的消息，BobMsg，自己库里的消息，是明文
	 * @param paillier
	 * @return AliceMsg和BobMsg的欧几里得距离
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

			//先计算左乘出e_B
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

			
			//再右乘计算出距离
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

				//产生两个随机数，用于加密密文的相乘协议
				Random random2 = new SecureRandom();
				Random random3 = new SecureRandom();
				randoms2 = new BigInteger(BobMsg.length, random2);
				randoms3 = new BigInteger(BobMsg.length, random2);
					
				
				e_randoms2=paillier.Encryption(randoms2); //加密randoms2
				e_randoms3=paillier.Encryption(randoms3); //加密randoms3
				
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
				ed= ed.mod(paillier.nsquare);  //ed最后的距离
			}
		
			return ed; //返回同态加密的马氏距离
		}
	
	//-------------------------------------------------------马氏距离结束-----------------------------------------------
	//-------------------------------------------------------开始小波变换----------------------------------------------
	//输入alice图片，得到小波变换系数密文
	public static BigInteger[] DWT_ALICE(int[] AliceMsg1,BigInteger[] e_AliceMsg1,Paillier paillier) 
	{
		//Paillier paillier = new Paillier();
		BigInteger Zero = new BigInteger("0");
        BigInteger encryptedZero;

	
        
	        BigInteger [] dwte_AliceMsg = new BigInteger[AliceMsg1.length];
	  //      BigInteger [] dwtre_AliceMsg = new BigInteger[AliceMsg.length];//小波逆变换系统，没用。
	        
	        BigInteger [] return_AliceMsg = new BigInteger[AliceMsg1.length/8];
	        
	        
			  /* 初始化小波变换*/
	        
			encryptedZero = paillier.Encryption(Zero);//时间复杂度--1个
			dwt h = new dwt(encryptedZero);
			
	/*		
			for(int i=0; i<10;i++)
			{
				System.out.println("没小波变换前，解密输出 " + i + ": " + paillier.Decryption(e_AliceMsg1[i]));
			}*/
			dwte_AliceMsg=h.haarDe(3,e_AliceMsg1,paillier.nsquare);//时间复杂度--haarDe里面
			 /* 输出小波变换的系数*/
			for(int i=0; i<return_AliceMsg.length;i++)
			{
				return_AliceMsg[i]=dwte_AliceMsg[i];
			}
			return return_AliceMsg;
	}
	
	public static double [][] FileTobobAry(int NumBobMsg6,int NumBoblength) throws Exception 
	{
		double [][] BobMsgread=new double[NumBobMsg6][NumBoblength]; 
		BufferedReader brbob = new BufferedReader(new InputStreamReader(new FileInputStream("d:\\PICTER\\testbob3.txt"),"latin1"));//使用BufferedReader 最大好处是可以按行读取,每次读取一行
		int indexbob = 0;//索引
	        String temp;//定义字符串,用于保存每行读取到的数据
	        while ((temp = brbob.readLine()) != null) {
	        	double[] ary = aryChange(temp);//通过函数吧字符串数组解析成整数数组
	            BobMsgread[indexbob] = ary;
	            indexbob++;
	    }     
	    brbob.close();// 关闭输入流  
	    return BobMsgread;
	}
	public static double [][] FileTouAry(int uvectornumber,int NumBoblength) throws Exception 
	{
		double [][] udoublegread=new double[uvectornumber][NumBoblength]; 
		BufferedReader bru = new BufferedReader(new InputStreamReader(new FileInputStream("d:\\PICTER\\testu3.txt"),"latin1"));//使用BufferedReader 最大好处是可以按行读取,每次读取一行
		int indexu = 0;//索引
	        String temp;//定义字符串,用于保存每行读取到的数据
	        while ((temp = bru.readLine()) != null) {	       
	        	double[] ary = aryChange(temp);//通过函数吧字符串数组解析成整数数组
	        	udoublegread[indexu] = ary;
	            indexu++;
	    }     
	    bru.close();// 关闭输入流  
	    return udoublegread;
	} 
	public static double [][] FileToaliceAry(int NumALICElength) throws Exception 
	{
		double [][] aliceMsgread=new double[40][NumALICElength]; 
		BufferedReader bralice = new BufferedReader(new InputStreamReader(new FileInputStream("d:\\PICTER\\testalice-junzhi2.txt"),"latin1"));//使用BufferedReader 最大好处是可以按行读取,每次读取一行
		int indexalice = 0;//索引
	        String temp;//定义字符串,用于保存每行读取到的数据
	        while ((temp = bralice.readLine()) != null) {
	        	double[] ary = aryChange(temp);//通过函数吧字符串数组解析成整数数组
	        	aliceMsgread[indexalice] = ary;
	            indexalice++;
	    }     
	    bralice.close();// 关闭输入流  
	    return aliceMsgread;
	}
	static double[] aryChange(String temp) {// 字符串数组解析成double数组
		  String[] ss = temp.trim().split("\\s+");// .trim()可以去掉首尾多余的空格
		                                                // .split("\\s+")
		                                                // 表示用正则表达式去匹配切割,\\s+表示匹配一个或者以上的空白符
		  double[] ary = new double[ss.length];
		  double a;
		  for (int i = 0; i < ary.length; i++) {
			  ary[i] = Double.parseDouble(ss[i]);// 解析数组的每一个元素
		     // System.out.println("ary " + i + ": " + ary[i]);
		  }
		   return ary;// 返回一个double数组
	}	        
	        
}

