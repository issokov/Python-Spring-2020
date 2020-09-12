from urllib import parse
outfile = open('post_create.data', 'w')
# for
# url=http%3A%2F%2Fvk.com&password=
params = ({ 'url': 'http://vk.com/',
			'password':''})
encoded = parse.urlencode(params)
outfile.write(encoded)
outfile.close()
