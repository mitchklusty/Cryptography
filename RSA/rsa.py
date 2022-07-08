import math
import random

def extended_euclid(a, b):
	if a == 0:
		return b, 0, 1
	else:
		gcd, x, y = extended_euclid(b % a, a)
	return gcd, y - (b // a) * x, x

def modexp(x, y, n):
	# returns x^y(mod n)
	z = 1
	bin_y = format(y, 'b')
	for i in range(len(bin_y)):
		z = z*z % n
		if bin_y[i] == '1':
			z = (z*x) % n
	return z

def generate_random(min_digits, max_digits):
	num_digits = random.randint(min_digits, max_digits)
	binary = ''
	for i in range(num_digits):
		r = random.random()
		if r > .5:
			binary += '1'
		else:
			binary += '0'
	return int(binary, base=2)


def generate_prime():
	p = generate_random(400, 800)
	while not miller_rabin(p):
		p = generate_random(400, 800)
	return p

def miller_rabin(n):
	a = generate_random(1,int(math.log(n, 2)))
	while a < 1 or a >= n:
		a = generate_random(1,int(math.log(n, 2)))

	if n == 2 or n == 3:
		return True
	if n % 2 == 0:
		return False
	m = n-1
	k = 1
	while m % 2 == 0:
		m //= 2
		k += 1
	b = modexp(a, m, n)
	if b == 1 or b == n-1:
		return True
	for i in range(k):
		b = modexp(b, 2, n)
		if b == 1:
			return False
		if b == n-1:
			return True
	return False

def generate_keys():
	p, q = generate_prime(), generate_prime()
	n = p*q
	e = 65537
	s = (p-1)*(q-1)
	while extended_euclid(e, s)[0] != 1 or e < 1 or e >= n:
		e = generate_random(1,int(math.log(s, 2)))
	public_key = '' + str(n) + ' ' + str(e)
	f = open("public_key", "w+")
	f.write(public_key)
	f.close()
	gcd, x_mul, y_mul = extended_euclid(e, s)
	d = x_mul % s
	f = open("private_key", "w+")
	f.write(str(d))
	f.close()
	return (n,e), d


def encrypt(m, e, n):
	return modexp(m, e, n)

def decrypt(c, d, n):
	return modexp(c, d, n)


if __name__ == "__main__":
	msg_file = open("message", "r")
	message = msg_file.read()
	msg_file.close()
	message = int(message)
	public_key, private_key = generate_keys()
	ciphertext = encrypt(message, public_key[1], public_key[0])
	ciphertext_file = open("ciphertext", "w+")
	ciphertext_file.write(str(ciphertext))
	ciphertext_file.close()
	decrypted_msg = decrypt(ciphertext, private_key, public_key[0])
	decrypted_file = open("decrypted_msg", "w+")
	decrypted_file.write(str(decrypted_msg))
	decrypted_file.close()


