import random
import copy

def generate_random(num_digits):
	binary = ''
	for i in range(num_digits):
		r = random.random()
		if r > .5:
			binary += '1'
		else:
			binary += '0'
	return int(binary, base=2)

def xor(a, b):
	if type(a) is list:
		if type(b) is list:
			return [a[i] ^ b[i] for i in range(len(a))]
		return [a[i] ^ b for i in range(len(a))]
	elif type(b) is list:
		return [a ^ b[i] for i in range(len(b))]
	return a ^ b

def gf_degree(a) :
	res = 0
	a >>= 1
	while (a != 0):
		a >>= 1;
		res += 1;
	return res

def gf_mpy(x, y):                  # mpy two 8 bit values
	p = 0b100011011             # mpy modulo x^8+x^4+x^3+x+1
	m = 0                       # m will be product
	for i in range(8):
		m = m << 1
		if m & 0b100000000:
			m = m ^ p
		if y & 0b010000000:
			m = m ^ x
		y = y << 1
	return m

def gf_invert(a, mod=0x1B):
	v = mod
	g1 = 1
	g2 = 0
	j = gf_degree(a) - 8

	while (a != 1) :
		if (j < 0) :
			a, v = v, a
			g1, g2 = g2, g1
			j = -j

		a ^= v << j
		g1 ^= g2 << j

		a %= 256  # Emulating 8-bit overflow
		g1 %= 256 # Emulating 8-bit overflow

		j = gf_degree(a) - gf_degree(v)

	return g1

def bin_array_to_int(bin_array):
	output = 0
	for i in range(len(bin_array)):
		output = output | (bin_array[i] << (len(bin_array)-1-i))
	return output

def byte_sub_matrix_mul(number):
	binary = '{:08b}'.format(number)
	bin_array = [int(binary[i]) for i in range(len(binary)-1, -1, -1)]
	m = [
	[1, 0, 0, 0, 1, 1, 1, 1], 
	[1, 1, 0, 0, 0, 1, 1, 1], 
	[1, 1, 1, 0, 0, 0, 1, 1], 
	[1, 1, 1, 1, 0, 0, 0, 1], 
	[1, 1, 1, 1, 1, 0, 0, 0], 
	[0, 1, 1, 1, 1, 1, 0, 0], 
	[0, 0, 1, 1, 1, 1, 1, 0],
	[0, 0, 0, 1, 1, 1, 1, 1]]
	b = [1, 1, 0, 0, 0, 1, 1, 0]
	bin_output = []
	for i in range(len(m)):
		bin_num = 0
		for j in range(len(bin_array)):
			bin_num = xor(bin_num, gf_mpy(m[i][j], bin_array[j]))
		bin_output.append(bin_num)
	for i in range(len(bin_output)):
		bin_output[i] = xor(bin_output[i], b[i])
	bin_output.reverse()
	return bin_array_to_int(bin_output)


def byte_sub(input_matrix):
	output_matrix = []
	for row in input_matrix:
		cur_row = []
		for i in row:
			if i == 0:
				cur_row.append(byte_sub_matrix_mul(0))
			else:
				cur_row.append(byte_sub_matrix_mul(gf_invert(i)))
		output_matrix.append(cur_row)
	return output_matrix

def inverse_byte_sub_matrix_mul(number):
	binary = '{:08b}'.format(number)
	bin_array = [int(binary[i]) for i in range(len(binary)-1, -1, -1)]
	m=[
	[0, 0, 1, 0, 0, 1, 0, 1],
	[1, 0, 0, 1, 0, 0, 1, 0],
	[0, 1, 0, 0, 1, 0, 0, 1],
	[1, 0, 1, 0, 0, 1, 0, 0],
	[0, 1, 0, 1, 0, 0, 1, 0],
	[0, 0, 1, 0, 1, 0, 0, 1],
	[1, 0, 0, 1, 0, 1, 0, 0],
	[0, 1, 0, 0, 1, 0, 1, 0]]
	b = [1, 1, 0, 0, 0, 1, 1, 0]
	bin_output = []
	for i in range(len(bin_array)):
		bin_array[i] = bin_array[i] ^ b[i]
	for i in range(len(m)):
		bin_num = 0
		for j in range(len(bin_array)):
			bin_num = xor(bin_num, gf_mpy(m[i][j], bin_array[j]))
		bin_output.append(bin_num)
	
	bin_output.reverse()
	return bin_array_to_int(bin_output)

def inverse_byte_sub(input_matrix):
	output_matrix = []
	for row in input_matrix:
		cur_row = []
		for i in row:
			i = inverse_byte_sub_matrix_mul(i)
			if i == 0:
				cur_row.append(0)
			else:
				cur_row.append(gf_invert(i))
		output_matrix.append(cur_row)
	return output_matrix


def shift_row(input_matrix):
	output_matrix = []
	output_matrix.append(input_matrix[0])
	for i in range(1, len(input_matrix)):
		output_matrix.append([0,0,0,0])
		for j in range(len(input_matrix[i])):
			output_matrix[i][j] = input_matrix[i][(j+i)%len(input_matrix[i])]
	return output_matrix

def inverse_shift_row(input_matrix):
	output_matrix = []
	output_matrix.append(input_matrix[0])
	for i in range(1, len(input_matrix)):
		output_matrix.append([0,0,0,0])
		for j in range(len(input_matrix[i])):
			output_matrix[i][j] = input_matrix[i][(j-i)%len(input_matrix[i])]
	return output_matrix


def mix_column_transformation(input_matrix):
	output_matrix = []
	m = [[2,3,1,1],[1,2,3,1],[1,1,2,3],[3,1,1,2]]
	for i in range(len(input_matrix)):
		row = []
		for j in range(len(input_matrix[i])):
			val = 0
			for k in range(len(m)):
				val = xor(val, gf_mpy(m[i][k], input_matrix[k][j]))
			row.append(val)
		output_matrix.append(row)
	return output_matrix

def inverse_mix_column_transformation(input_matrix):
	output_matrix = []
	m = [[14, 11, 13,  9],[ 9, 14, 11, 13],[13,  9, 14, 11],[11, 13,  9, 14]]

	for i in range(len(input_matrix)):
		row = []
		for j in range(len(input_matrix[i])):
			val = 0
			for k in range(len(m)):
				val = xor(val, gf_mpy(m[i][k], input_matrix[k][j]))
			row.append(val)
		output_matrix.append(row)
	return output_matrix


def bytes_from_key(key):
	output_matrix = []
	for i in range(4):
		row = []
		for j in range(4):
			shift = (i*4+j)*8
			row.append((key >> shift) & 0xFF)
		output_matrix.append(row)
	return output_matrix

def round_key_addition(input_matrix, key_matrix):
	output_matrix = []
	for i in range(len(input_matrix)):
		row = []
		for j in range(len(input_matrix[i])):
			row.append(xor(input_matrix[i][j], key_matrix[i][j]))
		output_matrix.append(row)
	return output_matrix

def inverse_round_key_addition(input_matrix, key_matrix):
	return [[input_matrix[i][j]^key_matrix[i][j] for j in range(len(input_matrix[i]))] for i in range(len(input_matrix))]

def column(matrix, i):
	return [row[i] for row in matrix]

def key_transform(input_column, rcon):
	output_array = []
	output_array.append(xor(byte_sub_matrix_mul(input_column[1]), rcon))
	output_array.append(byte_sub_matrix_mul(input_column[2]))
	output_array.append(byte_sub_matrix_mul(input_column[3]))
	output_array.append(byte_sub_matrix_mul(input_column[0]))
	return output_array

def transpose_matrix(matrix):
	return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]

def key_schedule(key_matrix, round_number):
	r = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
	columns = transpose_matrix(key_matrix)
	output_key = []
	w4 = []
	for index in range(len(columns[0])):
		w4.append(xor(columns[0][index], columns[3][index]))
	output_key.append(w4)
	for index in range(1, len(columns)):
		trans = key_transform(output_key[index-1], r[round_number])

		output_key.append(xor(columns[index], trans))
	return transpose_matrix(output_key)


def aes_encrypt(byte_str, key):
	if type(key) is list:
		current_key = key
	else:
		current_key = bytes_from_key(key)
	current_str = round_key_addition(byte_str, current_key)
	for i in range(9):
		current_key = key_schedule(current_key, i)
		current_str = byte_sub(current_str)
		current_str = shift_row(current_str)
		current_str = mix_column_transformation(current_str)
		current_str = round_key_addition(current_str, current_key)
	current_str = byte_sub(current_str)
	current_str = shift_row(current_str)
	current_key = key_schedule(current_key, 9)
	return round_key_addition(current_str, current_key)

def key_to_string(key_int):
	#key length should be 128 bits
	print(hex((key_int >> 96)&0xFF))
	print(hex((key_int >> 64)&0xFF))
	print(hex((key_int >> 32)&0xFF))
	print(hex((key_int >> 0)&0xFF))
	return f"{chr((key_int >> 96)&0xFF)}{chr((key_int >> 64)&0xFF)}{chr((key_int >> 32)&0xFF)}{chr(key_int&0xFF)}"







def generate_round_keys(key):
	keys = [key]
	for i in range(10):
		keys.append(key_schedule(keys[i], i))
	return keys

def aes_decrypt(byte_str, key):
	if type(key) is not list:
		key = bytes_from_key(key)
	keys = generate_round_keys(key)
	current_matrix = inverse_round_key_addition(byte_str, keys[10])
	current_matrix = inverse_shift_row(current_matrix)
	current_matrix = inverse_byte_sub(current_matrix)
	for i in range(9, 0, -1):
		current_matrix = inverse_round_key_addition(current_matrix, keys[i])
		current_matrix = inverse_mix_column_transformation(current_matrix)
		current_matrix = inverse_shift_row(current_matrix)
		current_matrix = inverse_byte_sub(current_matrix)
	current_matrix = inverse_round_key_addition(current_matrix, keys[0])
	return current_matrix

def array_to_matrix(array, dim):
	output_matrix = [[0 for j in range(dim)] for i in range(dim)]
	for i in range(len(array)):
		output_matrix[int(i/dim)][i%dim] = array[i]
	return output_matrix


def format_to_bytes(string):
	if type(string) is str:
		byte_str = string.encode('utf-8')
	else:
		byte_str = string
	byte_strs = []
	cur_str = b''
	for byte in byte_str:
		cur_str += byte.to_bytes(1, 'big')
		if len(cur_str) == 16:
			byte_strs.append(cur_str)
			cur_str = b''
	byte_strs.append(cur_str)
	for i in range(len(byte_strs)):
		byte_strs[i] = array_to_matrix(byte_strs[i], 4)

	return byte_strs

def byte_array_to_str(byte_matrix):
	output_str = ''
	for row in byte_matrix:
		for e in row:
			if type(e) is int:
				output_str += e.to_bytes(1, 'big').decode('utf-8')
	return output_str

def byte_array_to_byte_str(byte_matrix):
	output_str = b''
	for row in byte_matrix:
		for e in row:
			output_str += e.to_bytes(1, 'big')
	return output_str

def decode_matrix_bytes(byte_matrices):
	output_str = ''
	for matrix in byte_matrices:
		output_str += byte_array_to_str(matrix)
	return output_str


def generate_key():
	return generate_random(128)

def encrypt(string, key):
	if type(key) is int:
		key = bytes_from_key(key)
	string = format_to_bytes(string)
	output = b''
	for s in string:
		output += byte_array_to_byte_str(aes_encrypt(s, key))
	return output

def decrypt(string, key):
	if type(string) is str:
		string = string.encode('utf-8')
	elif type(string) is int:
		string = string.to_bytes(1, 'big')
	string = format_to_bytes(string)
	if type(key) is int:
		key = bytes_from_key(key)
	output = b''
	for s in string:
		if s[0] == [0,0,0,0]:
			break
		output += byte_array_to_byte_str(aes_decrypt(s, key))
	return output


# key = generate_key()
# encrypted = encrypt("hello how are you? this is my string", key)
# print(encrypted)

# decrypted = decrypt(encrypted, key)
# print(decode_matrix_bytes(decrypted))
# print(decrypted.decode('utf-8'))

# print(decode_matrix_bytes(format_to_bytes("hello this is my name")))


