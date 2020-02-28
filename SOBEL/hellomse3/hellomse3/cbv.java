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